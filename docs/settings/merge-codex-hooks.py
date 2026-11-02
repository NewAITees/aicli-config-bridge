#!/usr/bin/env python3
"""Merge managed hooks without replacing personal configuration.

See cross-agent-settings-policy.md. Run without --apply to inspect counts only.
Backups contain the original bytes and symlink metadata for manual restoration.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import stat
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def validate_config(value: object) -> dict[str, Any]:
    """Reject malformed hook structures before modifying any file."""
    if not isinstance(value, dict):
        raise ValueError("configuration must be a JSON object")
    hooks = value.get("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("hooks must be an object")
    for event, entries in hooks.items():
        if not isinstance(event, str) or not isinstance(entries, list):
            raise ValueError("each hook event must contain a list")
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("hooks"), list):
                raise ValueError("each hook entry must contain a hooks list")
            if "matcher" in entry and not isinstance(entry["matcher"], str):
                raise ValueError("hook matcher must be a string")
            for hook in entry["hooks"]:
                if not isinstance(hook, dict) or not isinstance(hook.get("type"), str):
                    raise ValueError("each hook must have a string type")
                if hook["type"] == "command" and (
                    not isinstance(hook.get("command"), str) or not hook["command"].strip()
                ):
                    raise ValueError("command hooks must have a nonempty command")
                if "commandWindows" in hook and not isinstance(hook["commandWindows"], str):
                    raise ValueError("commandWindows must be a string")
    return copy.deepcopy(value)


def hook_identity(hook: dict[str, Any]) -> str:
    """Identify only managed launchers, including shell-neutral Windows bootstraps."""
    guard_code = (
        "from pathlib import Path; import runpy; "
        "runpy.run_path(str(Path.home()/'.codex/hooks/guard.py'), run_name='__main__')"
    )
    rtk_code = (
        "import(require('node:url').pathToFileURL(require('node:path').join("
        "require('node:os').homedir(),'.codex','hooks','rtk_pre_tool_use.mjs')).href)"
    )
    for field in ("command", "commandWindows"):
        command = hook.get(field, "")
        if not isinstance(command, str):
            continue
        # Match complete known bootstrap programs, not a mention of their path
        # inside another personal hook. Regression tests read the real template.
        if command in {
            f'python -X utf8 -c "{guard_code}" pre',
            f'python -X utf8 -c "{guard_code}" stop',
        }:
            return "bridge:guard"
        if command == f'node -e "{rtk_code}"':
            return "bridge:rtk"
        # Unknown wrappers, shell expressions and mere path mentions are personal.
        # Recognize only a complete supported interpreter/script invocation.
        token = r"""(?:"[^"\r\n]+"|'[^'\r\n]+'|[^\s"';&|<>`]+)"""
        match = re.fullmatch(
            rf"(?P<executable>{token})\s+(?:-X\s+utf8\s+)?"
            rf"(?P<script>{token})(?:\s+(?P<mode>pre|stop))?",
            command,
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        executable = re.split(r"[/\\]", match["executable"].strip("\"'"))[-1].lower()
        script = match["script"].strip("\"'")
        if any(character in script for character in ";&|<>`$\r\n"):
            continue
        script_match = re.fullmatch(
            r".*[/\\]\.codex[/\\]hooks[/\\](guard\.py|rtk_pre_tool_use\.(?:py|mjs))",
            script,
            flags=re.IGNORECASE,
        )
        if not script_match:
            continue
        name = script_match[1].lower()
        python = re.fullmatch(r"python(?:3(?:\.\d+)?)?(?:\.exe)?", executable)
        if name == "guard.py" and python and match["mode"] in {"pre", "stop"}:
            return "bridge:guard"
        if match["mode"] is None and (
            (name == "rtk_pre_tool_use.py" and python)
            or (name == "rtk_pre_tool_use.mjs" and executable in {"node", "node.exe"})
        ):
            return "bridge:rtk"
    return "exact:" + json.dumps(hook, sort_keys=True, ensure_ascii=False)


def merge_hooks(current: object, managed: object) -> dict[str, Any]:
    """Preserve personal data and put managed guards before output rewrites."""
    result = validate_config(current)
    template = validate_config(managed)
    existing_events = result.setdefault("hooks", {})
    for event, required_entries in template.get("hooks", {}).items():
        identities = {hook_identity(hook) for entry in required_entries for hook in entry["hooks"]}
        retained = []
        for entry in existing_events.get(event, []):
            kept = [hook for hook in entry["hooks"] if hook_identity(hook) not in identities]
            if kept:
                entry["hooks"] = kept
                retained.append(entry)
            elif not entry["hooks"]:
                retained.append(entry)
        existing_events[event] = copy.deepcopy(required_entries) + retained
    return result


def snapshot(target: Path) -> tuple[bytes | None, str | None]:
    symlink_target = os.readlink(target) if target.is_symlink() else None
    content = target.read_bytes() if target.exists() or target.is_symlink() else None
    return content, symlink_target


def durable_write(path: Path, content: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def merge_file(target: Path, managed: object, *, apply: bool = False) -> dict[str, object]:
    """Dry-run by default; apply atomically replaces the leaf, never its link target."""
    target = Path(os.path.abspath(target.expanduser()))
    original, symlink_target = snapshot(target)
    current = json.loads(original.decode("utf-8-sig")) if original is not None else {}
    merged = merge_hooks(current, managed)
    required = validate_config(managed)
    count = sum(
        len(entry["hooks"]) for entries in required.get("hooks", {}).values() for entry in entries
    )
    changed = merged != current or symlink_target is not None
    summary: dict[str, object] = {
        "managed_hook_count": count,
        "changed": changed,
        "applied": False,
    }
    if not apply or not changed:
        return summary
    target.parent.mkdir(parents=True, exist_ok=True)
    original_mode = stat.S_IMODE(target.stat().st_mode) if original is not None else None
    if original is not None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = target.parent / ".aicli-backup" / f"{target.name}.{stamp}.{uuid.uuid4().hex}"
        backup.mkdir(parents=True, mode=0o700)
        durable_write(backup / "content.json", original)
        metadata = {
            "target": str(target),
            "symlink_target": symlink_target,
            "original_mode": original_mode,
            "restore": "Restore content.json as the original file, or recreate symlink_target.",
        }
        durable_write(
            backup / "metadata.json",
            (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
    encoded = (json.dumps(merged, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(
        prefix=f".{target.name}.", dir=target.parent, delete=False
    ) as tmp:
        temporary = Path(tmp.name)
        tmp.write(encoded)
        tmp.flush()
        os.fsync(tmp.fileno())
    try:
        if original_mode is not None:
            temporary.chmod(original_mode)
        if snapshot(target) != (original, symlink_target):
            raise RuntimeError("configuration changed during merge; refusing replacement")
        os.replace(temporary, target)
    finally:
        # Only this call's freshly created temporary leaf can be removed.
        temporary.unlink(missing_ok=True)
    summary["applied"] = True
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path.home() / ".codex" / "hooks.json")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[2] / "project-configs" / ".codex" / "hooks.json"
    try:
        managed = json.loads(source.read_text(encoding="utf-8-sig"))
        summary = merge_file(args.target, managed, apply=args.apply)
    except (OSError, ValueError, RuntimeError):
        # Never print parsed personal configuration or offending JSON fragments.
        print(
            "Hook merge stopped: invalid configuration or file operation failure.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
