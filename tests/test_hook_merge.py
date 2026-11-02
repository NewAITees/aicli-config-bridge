from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "docs/settings/merge-codex-hooks.py"


def load_merge():
    spec = importlib.util.spec_from_file_location("hook_merge_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def command(script, **extra):
    return {"type": "command", "command": f"python3 ~/.codex/hooks/{script}", **extra}


def template():
    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "^Bash$",
                    "hooks": [
                        command("guard.py pre"),
                        command("rtk_pre_tool_use.py", timeout=30),
                    ],
                }
            ],
            "Stop": [{"hooks": [command("guard.py stop", timeout=130)]}],
        }
    }


def test_merge_preserves_unknown_settings_and_other_hooks():
    module = load_merge()
    custom = {"matcher": "mcp__custom", "hooks": [{"type": "command", "command": "custom"}]}
    current = {
        "private": {"setting": "keep"},
        "hooks": {"PreToolUse": [custom], "SessionStart": []},
    }
    merged = module.merge_hooks(current, template())
    assert merged["private"] == current["private"]
    assert merged["hooks"]["SessionStart"] == []
    assert merged["hooks"]["PreToolUse"][-1] == custom
    assert "Stop" not in current["hooks"]


def test_existing_rtk_is_updated_without_duplicate_or_lost_sibling():
    module = load_merge()
    current = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "extra": "keep",
                    "hooks": [
                        {
                            "type": "command",
                            "command": (
                                "/usr/bin/python3 /home/old/.codex/hooks/rtk_pre_tool_use.py"
                            ),
                        },
                        {"type": "command", "command": "personal-check"},
                    ],
                }
            ]
        }
    }
    merged = module.merge_hooks(current, template())
    entries = merged["hooks"]["PreToolUse"]
    hooks = [hook for entry in entries for hook in entry["hooks"]]
    assert sum("rtk_pre_tool_use" in hook["command"] for hook in hooks) == 1
    assert hooks[0]["command"].endswith("guard.py pre")
    assert entries[-1]["extra"] == "keep"
    assert entries[-1]["hooks"] == [{"type": "command", "command": "personal-check"}]


def test_merge_is_idempotent():
    module = load_merge()
    once = module.merge_hooks({}, template())
    assert module.merge_hooks(once, template()) == once


@pytest.mark.parametrize(
    "bad",
    [
        [],
        {"hooks": []},
        {"hooks": {"Stop": {}}},
        {"hooks": {"Stop": [{"hooks": "bad"}]}},
        {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": 2}]}]}},
    ],
)
def test_malformed_hook_structure_is_rejected(bad):
    with pytest.raises(ValueError):
        load_merge().merge_hooks(bad, template())


def test_dryrun_does_not_create_any_files(tmp_path):
    target = tmp_path / "new-config" / "hooks.json"
    result = load_merge().merge_file(target, template())
    assert result == {"managed_hook_count": 3, "changed": True, "applied": False}
    assert not target.parent.exists()


def test_apply_backs_up_content_and_is_idempotent(tmp_path):
    module = load_merge()
    target = tmp_path / "hooks.json"
    original = b'{"private":true}\n'
    target.write_bytes(original)
    result = module.merge_file(target, template(), apply=True)
    assert result["applied"] is True
    assert json.loads(target.read_text())["private"] is True
    backups = list((tmp_path / ".aicli-backup").iterdir())
    assert len(backups) == 1
    assert (backups[0] / "content.json").read_bytes() == original
    metadata = json.loads((backups[0] / "metadata.json").read_text())
    assert metadata["symlink_target"] is None
    assert module.merge_file(target, template(), apply=True)["changed"] is False
    assert len(list((tmp_path / ".aicli-backup").iterdir())) == 1


def test_symlink_target_is_untouched_and_link_metadata_is_backed_up(tmp_path):
    module = load_merge()
    source = tmp_path / "source.json"
    source.write_text('{"private":true}')
    target = tmp_path / "hooks.json"
    target.symlink_to(source)
    original_link = os.readlink(target)
    module.merge_file(target, template(), apply=True)
    assert not target.is_symlink()
    assert source.read_text() == '{"private":true}'
    metadata_file = next((tmp_path / ".aicli-backup").glob("*/metadata.json"))
    metadata = json.loads(metadata_file.read_text())
    assert metadata["symlink_target"] == original_link


def test_invalid_json_stops_before_any_write(tmp_path):
    target = tmp_path / "hooks.json"
    target.write_text("broken json")
    with pytest.raises(ValueError):
        load_merge().merge_file(target, template(), apply=True)
    assert target.read_text() == "broken json"
    assert not (tmp_path / ".aicli-backup").exists()


def test_atomic_replace_failure_keeps_original(tmp_path, monkeypatch):
    module = load_merge()
    target = tmp_path / "hooks.json"
    target.write_text('{"private":true}')

    def fail_replace(*args):
        raise OSError("replacement denied")

    monkeypatch.setattr(module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="replacement denied"):
        module.merge_file(target, template(), apply=True)
    assert target.read_text() == '{"private":true}'


def test_windows_rtk_path_is_recognized_without_duplicate():
    module = load_merge()
    current = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 /different/linux/path",
                            "commandWindows": (
                                r'node "%USERPROFILE%\.codex\hooks\rtk_pre_tool_use.mjs"'
                            ),
                        }
                    ],
                }
            ]
        }
    }
    merged = module.merge_hooks(current, template())
    hooks = [hook for entry in merged["hooks"]["PreToolUse"] for hook in entry["hooks"]]
    assert len(hooks) == 2


def test_concurrent_change_prevents_replacement(tmp_path, monkeypatch):
    module = load_merge()
    target = tmp_path / "hooks.json"
    target.write_text('{"private":true}')
    real_snapshot = module.snapshot
    calls = []

    def changed_snapshot(path):
        calls.append(path)
        if len(calls) == 2:
            target.write_text('{"new-personal-setting":true}')
        return real_snapshot(path)

    monkeypatch.setattr(module, "snapshot", changed_snapshot)
    with pytest.raises(RuntimeError, match="changed during merge"):
        module.merge_file(target, template(), apply=True)
    assert json.loads(target.read_text()) == {"new-personal-setting": True}


def deployed_template():
    source = Path(__file__).parents[1] / "project-configs/.codex/hooks.json"
    return json.loads(source.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "event,index,identity",
    [
        ("PreToolUse", 0, "bridge:guard"),
        ("PreToolUse", 1, "bridge:rtk"),
        ("Stop", 0, "bridge:guard"),
    ],
)
def test_windows_bootstrap_command_has_stable_bridge_identity(event, index, identity):
    module = load_merge()
    hook = deployed_template()["hooks"][event][index]["hooks"][0]
    windows_only = {"type": "command", "command": hook["commandWindows"]}
    assert module.hook_identity(windows_only) == identity


def test_mixed_legacy_and_bootstrap_registration_converges_to_three_managed_hooks():
    module = load_merge()
    managed = deployed_template()
    current = template()
    personal_pre = {"type": "command", "command": "personal-check"}
    personal_stop = {"type": "command", "command": "personal-stop"}
    for event, entries in managed["hooks"].items():
        for entry in entries:
            hook = entry["hooks"][0]
            current["hooks"][event].append(
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": hook["commandWindows"],
                        }
                    ]
                }
            )
    current["hooks"]["PreToolUse"].append({"hooks": [personal_pre]})
    current["hooks"]["Stop"].append({"hooks": [personal_stop]})
    merged = module.merge_hooks(current, managed)
    all_hooks = [
        hook for entries in merged["hooks"].values() for entry in entries for hook in entry["hooks"]
    ]
    assert len(all_hooks) == 5
    assert personal_pre in all_hooks
    assert personal_stop in all_hooks
    assert sum(module.hook_identity(hook).startswith("bridge:") for hook in all_hooks) == 3
    assert module.merge_hooks(merged, managed) == merged


def test_similar_personal_bootstrap_is_not_removed():
    module = load_merge()
    managed = deployed_template()
    windows = managed["hooks"]["PreToolUse"][1]["hooks"][0]["commandWindows"]
    personal = {"type": "command", "command": "echo " + windows}
    current = {"hooks": {"PreToolUse": [{"hooks": [personal]}]}}
    merged = module.merge_hooks(current, managed)
    all_pre = [hook for entry in merged["hooks"]["PreToolUse"] for hook in entry["hooks"]]
    assert personal in all_pre


@pytest.mark.parametrize(
    "personal_command",
    [
        "echo ~/.codex/hooks/guard.py",
        "echo ~/.codex/hooks/rtk_pre_tool_use.py",
        "python3 ~/.codex/hooks/guard.py pre && personal-check",
        "personal-check; python3 ~/.codex/hooks/guard.py pre",
        "python3 ~/.codex/hooks/guard.py.backup pre",
        "python3 personal-wrapper.py ~/.codex/hooks/guard.py",
    ],
)
def test_personal_legacy_path_mentions_are_retained(personal_command):
    module = load_merge()
    personal = {"type": "command", "command": personal_command}
    current = {"hooks": {"PreToolUse": [{"hooks": [personal]}]}}
    merged = module.merge_hooks(current, deployed_template())
    assert personal in [hook for entry in merged["hooks"]["PreToolUse"] for hook in entry["hooks"]]


@pytest.mark.parametrize(
    "launcher,identity",
    [
        ("python3 -X utf8 ~/.codex/hooks/guard.py pre", "bridge:guard"),
        ("/usr/bin/python3 /home/old/.codex/hooks/guard.py stop", "bridge:guard"),
        ('python "C:\\Users\\Name Here\\.codex\\hooks\\guard.py" pre', "bridge:guard"),
        ('node "%USERPROFILE%\\.codex\\hooks\\rtk_pre_tool_use.mjs"', "bridge:rtk"),
        ("python3 ~/.codex/hooks/rtk_pre_tool_use.py", "bridge:rtk"),
    ],
)
def test_known_legacy_launchers_keep_managed_identity(launcher, identity):
    assert load_merge().hook_identity({"type": "command", "command": launcher}) == identity
