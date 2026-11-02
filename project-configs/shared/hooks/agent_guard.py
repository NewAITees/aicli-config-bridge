#!/usr/bin/env python3
"""Shared guard contract; see docs/skills/sfw-common-spec.md and cross-agent settings.

Reuse Claude's package parser and dangerous-command rules before any RTK rewrite.
This is a command guard, not a complete shell or PowerShell security boundary.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType

CONFIGS = Path(__file__).resolve().parents[2]
CLAUDE_HOOKS = CONFIGS / ".claude" / "hooks"
TEST_TIMEOUT = 120


def package_parser() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "aicli_sfw_guard", CLAUDE_HOOKS / "sfw_pre_tool_use.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("sfw parser could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_windows_command(command: str) -> str:
    """Recognize native executable suffixes without changing the executed command."""
    names = (
        r"npm|pnpm|yarn|pip[\d.]*|python[\d.]*|uv|cargo|go|gem|bundle|sfw|git|"
        r"powershell|pwsh|cmd|rm|sudo|terraform|kubectl"
    )
    # Windows executable names are case-insensitive. Limit case folding to the
    # recognized suffix forms; an unsuffixed POSIX executable keeps its spelling.
    return re.sub(
        rf"(?i)\b({names})\.(?:exe|cmd|bat|ps1)\b",
        lambda match: match.group(1).lower(),
        command.replace("\\", "/"),
    )


def package_fetch_without_sfw(command: str) -> bool:
    parser = package_parser()
    if parser.find_unguarded(command):
        return True
    native = normalized_windows_command(command)
    if parser.find_unguarded(native):
        return True
    # Native shell wrappers are not POSIX shells, so inspect their literal
    # scripts separately. Encoded/dynamic scripts remain outside coverage.
    try:
        for tokens in parser.split_segments(native):
            for index, token in enumerate(tokens[:-1]):
                wrappers = {word.rsplit("/", 1)[-1].lower() for word in tokens[:index]}
                powershell_script = token.lower() in {"-command", "-c"} and bool(
                    wrappers & {"powershell", "pwsh"}
                )
                cmd_script = token.lower() in {"/c", "/k"} and "cmd" in wrappers
                if powershell_script or cmd_script:
                    if package_fetch_without_sfw(" ".join(tokens[index + 1 :])):
                        return True
    except ValueError:
        return bool(parser.fails_closed(native))
    return False


def dangerous_reason(command: str) -> str:
    rules_path = CLAUDE_HOOKS / "rules" / "hook_pre_commands_rules.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8"))["rules"]
    normalized = re.sub(r"\s+", " ", command.replace("\n", ";"))
    native = normalized_windows_command(normalized)
    # A quoted Windows executable path leaves a closing quote between its
    # basename and arguments. Remove that delimiter only for guarded names
    # in this matching copy; keep the parser and executed command unchanged.
    native = re.sub(r"(?i)\b(rm|git|sudo|terraform|kubectl)[\"'](?=\s)", r"\1", native)
    for rule in rules:
        if not rule.get("enabled"):
            continue
        pattern = rule["pattern"].replace("[:space:]", r"\s").replace("[:alnum:]", "a-zA-Z0-9")
        if any(
            re.search(pattern, candidate, flags=re.IGNORECASE) for candidate in (normalized, native)
        ):
            return str(rule["message"])
    # Native Windows recursive deletion has different names and switches.
    if re.search(
        r"(?i)\b(remove-item|del|erase|ri|rd|rmdir)\b[^;|&]*\s-(recurse|recurs|recur|recu|rec|re|r)\b",
        normalized,
    ):
        return "再帰的なWindowsファイル削除です。対象と復旧手段を確認してください。"
    if re.search(r"(?i)\b(rd|rmdir|del|erase)\b[^;|&]*\s/s\b", normalized):
        return "再帰的なWindowsディレクトリ削除です。対象と復旧手段を確認してください。"
    return ""


def evaluate_pre(payload: object) -> dict[str, str]:
    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return {"decision": "deny", "reason": "シェル入力を解析できないため実行を拒否しました。"}
    if package_fetch_without_sfw(command):
        return {
            "decision": "deny",
            "reason": "パッケージ取得・更新は sfw 経由、exact版で実行してください。",
        }
    reason = dangerous_reason(command)
    return {"decision": "ask" if reason else "allow", "reason": reason}


def trust_file_for(agent: str) -> Path:
    if agent == "codex":
        return Path.home() / ".codex" / "test_gate_trusted_dirs"
    if agent == "opencode":
        return Path.home() / ".config" / "opencode" / "test_gate_trusted_dirs"
    raise ValueError(f"unsupported agent: {agent}")


def trusted_project(project: Path, trust_file: Path) -> bool:
    if not trust_file.is_file():
        return False
    for line in trust_file.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        candidate = Path(line).expanduser()
        if candidate.is_absolute() and candidate.is_dir() and candidate.resolve() == project:
            return True
    return False


def evaluate_stop(payload: object, agent: str) -> dict[str, str]:
    cwd = payload.get("cwd") if isinstance(payload, dict) else None
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        return {"decision": "allow", "reason": "未実行: 絶対パスの作業フォルダがありません。"}
    project = Path(cwd).resolve()
    if not trusted_project(project, trust_file_for(agent)):
        return {
            "decision": "allow",
            "reason": "未実行: テスト実行の信頼リストに登録されていません。",
        }
    command: list[str] | None = None
    if (project / "pyproject.toml").is_file() and (project / ".venv").is_dir():
        uv = shutil.which("uv")
        if uv:
            command = [uv, "run", "--frozen", "--no-sync", "pytest"]
    elif (project / "package.json").is_file() and (project / "node_modules").is_dir():
        npm = shutil.which("npm")
        if npm:
            command = [npm, "test", "--silent"]
    if command is None:
        return {
            "decision": "allow",
            "reason": "未実行: 対応するテスト環境・導入済み依存がありません。",
        }
    with tempfile.NamedTemporaryFile(prefix="aicli-test-gate-", suffix=".log", delete=False) as log:
        log_path = Path(log.name)
    try:
        result = subprocess.run(
            command,
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
            timeout=TEST_TIMEOUT,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log_path.write_text(str(exc), encoding="utf-8")
        return {"decision": "deny", "reason": f"テスト実行を完了できません。詳細: {log_path}"}
    log_path.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        return {
            "decision": "deny",
            "reason": f"テストが失敗しています。修正してから完了してください。詳細: {log_path}",
        }
    return {"decision": "allow", "reason": f"テスト通過。詳細: {log_path}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("pre", "stop"))
    parser.add_argument("--agent", choices=("codex", "opencode"), required=True)
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin)
        result = evaluate_pre(payload) if args.mode == "pre" else evaluate_stop(payload, args.agent)
    except Exception as exc:
        result = {
            "decision": "deny",
            "reason": f"安全フックを評価できません: {type(exc).__name__}: {exc}",
        }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
