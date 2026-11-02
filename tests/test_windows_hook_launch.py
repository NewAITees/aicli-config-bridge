"""Exercise managed Windows hook commands through native shells, not direct Python."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows hook launch contract")


@pytest.mark.parametrize("shell", ["powershell", "cmd"])
@pytest.mark.parametrize("mode", ["pre", "stop"])
def test_guard_launches_from_both_windows_shells(shell, mode, tmp_path):
    config = json.loads((ROOT / "project-configs/.codex/hooks.json").read_text(encoding="utf-8"))
    event = "PreToolUse" if mode == "pre" else "Stop"
    command = config["hooks"][event][0]["hooks"][0]["commandWindows"]
    installed = tmp_path / ".codex" / "hooks" / "guard.py"
    installed.parent.mkdir(parents=True)
    installed.symlink_to(ROOT / "project-configs/.codex/hooks/guard.py")
    env = {**os.environ, "USERPROFILE": str(tmp_path)}
    payload = {"cwd": str(tmp_path), "tool_input": {"command": "rm -rf never-executed"}}
    if shell == "powershell":
        program = shutil.which("pwsh")
        assert program is not None
        args = [program, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command]
    else:
        args = f'{os.environ["COMSPEC"]} /d /s /c "{command}"'
    result = subprocess.run(
        args,
        input=json.dumps(payload),
        cwd=tmp_path,
        encoding="utf-8",
        capture_output=True,
        timeout=20,
        check=False,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    if mode == "pre":
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    else:
        assert "未実行" in output["systemMessage"]


@pytest.mark.parametrize("shell", ["powershell", "cmd"])
def test_rtk_bootstrap_uses_native_home_and_preserves_rewrite(shell, tmp_path):
    config = json.loads((ROOT / "project-configs/.codex/hooks.json").read_text(encoding="utf-8"))
    command = config["hooks"]["PreToolUse"][1]["hooks"][0]["commandWindows"]
    installed = tmp_path / ".codex" / "hooks" / "rtk_pre_tool_use.mjs"
    installed.parent.mkdir(parents=True)
    installed.symlink_to(ROOT / "project-configs/.codex/hooks/rtk_pre_tool_use.mjs")
    node = shutil.which("node")
    assert node is not None
    rewritten = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {"command": "rtk git status"},
        }
    }
    (tmp_path / "hook").write_text(
        "process.stdout.write(" + json.dumps(json.dumps(rewritten)) + ");", encoding="utf-8"
    )
    env = {**os.environ, "USERPROFILE": str(tmp_path), "RTK_BINARY": node}
    if shell == "powershell":
        args = [shutil.which("pwsh"), "-NoProfile", "-Command", command]
    else:
        args = f'{os.environ["COMSPEC"]} /d /s /c "{command}"'
    result = subprocess.run(
        args,
        input='{"tool_input":{"command":"git status"}}',
        cwd=tmp_path,
        env=env,
        encoding="utf-8",
        capture_output=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    specific = json.loads(result.stdout)["hookSpecificOutput"]
    assert specific["updatedInput"]["command"] == "rtk git status"
    assert specific["permissionDecision"] == "allow"
