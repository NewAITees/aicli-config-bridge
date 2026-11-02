from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "project-configs/.codex/hooks/guard.py"


def call(mode, payload):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), mode],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout) if result.stdout else None


def test_codex_danger_is_denied_instead_of_unsupported_ask():
    result = call("pre", {"tool_input": {"command": "rm -rf example"}})
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "ask" not in result["hookSpecificOutput"].values()


def test_codex_sfw_denial_is_preserved():
    result = call("pre", {"tool_input": {"command": "npm install pkg@1.0.0"}})
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_codex_routine_command_does_not_override_other_permissions():
    assert call("pre", {"tool_input": {"command": "git status"}}) is None


def test_invalid_adapter_mode_fails_closed():
    result = call("invalid", {"tool_input": {"command": "git status"}})
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_codex_stop_malformed_input_blocks_completion():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "stop"],
        input="not json",
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(result.stdout)["decision"] == "block"


def test_codex_stop_untrusted_project_reports_untested(tmp_path):
    result = call("stop", {"cwd": str(tmp_path)})
    assert "未実行" in result["systemMessage"]
