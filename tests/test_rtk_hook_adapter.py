from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).parents[1] / "project-configs" / ".codex" / "hooks" / "rtk_pre_tool_use.py"
WINDOWS_SCRIPT = SCRIPT.with_name("rtk_pre_tool_use.mjs")


def load_adapter() -> ModuleType:
    spec = importlib.util.spec_from_file_location("rtk_pre_tool_use", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_adds_codex_allow_decision_to_rtk_rewrite(monkeypatch, capsys) -> None:
    module = load_adapter()
    rtk_output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {"command": "rtk git status"},
        }
    }
    completed = subprocess.CompletedProcess(
        args=["rtk", "hook", "claude"],
        returncode=0,
        stdout=json.dumps(rtk_output),
        stderr="",
    )
    monkeypatch.setattr(module.shutil, "which", lambda _: "/usr/bin/rtk")
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: completed)
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"tool_input":{"command":"git status"}}'))

    assert module.main() == 0

    output = json.loads(capsys.readouterr().out)
    specific = output["hookSpecificOutput"]
    assert specific["updatedInput"] == {"command": "rtk git status"}
    assert specific["permissionDecision"] == "allow"


def test_outputs_nothing_when_rtk_does_not_rewrite(monkeypatch, capsys) -> None:
    module = load_adapter()
    completed = subprocess.CompletedProcess(
        args=["rtk", "hook", "claude"],
        returncode=0,
        stdout="",
        stderr="",
    )
    monkeypatch.setattr(module.shutil, "which", lambda _: "/usr/bin/rtk")
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: completed)
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"tool_input":{"command":"rtk git status"}}'))

    assert module.main() == 0
    assert capsys.readouterr().out == ""


def test_windows_node_adapter_adds_codex_allow_decision(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        return

    fake_rtk = tmp_path / "rtk.exe"
    fake_rtk.write_text(
        "#!/bin/sh\n"
        "cat >/dev/null\n"
        "printf '%s\\n' "
        '\'{"hookSpecificOutput":{"hookEventName":"PreToolUse",\''
        '\'"updatedInput":{"command":"rtk git status"}}}\'\n',
        encoding="utf-8",
    )
    fake_rtk.chmod(0o755)
    env = {**os.environ, "RTK_BINARY": str(fake_rtk)}

    result = subprocess.run(
        [node, str(WINDOWS_SCRIPT)],
        input='{"tool_input":{"command":"git status"}}',
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    specific = output["hookSpecificOutput"]
    assert specific["updatedInput"] == {"command": "rtk git status"}
    assert specific["permissionDecision"] == "allow"
