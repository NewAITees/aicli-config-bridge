from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "project-configs" / ".claude" / "hooks" / "sfw_pre_tool_use.py"


def run_hook(stdin: str) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=stdin,
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def bash(command: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


@pytest.mark.parametrize(
    "command",
    [
        "npm install left-pad@1.3.0",
        "npm i -g pkg@1.0.0",
        "pnpm add pkg@1.0.0",
        "pip install requests==2.0.0",
        "python3 -m pip install requests==2.0.0",
        "uv add litellm==1.93.2",
        "uv sync",
        "uv pip install pkg==1.0.0",
        "cd app && npm ci",
        "FOO=1 npm install pkg@1.0.0",
        "/opt/homebrew/bin/npm install pkg@1.0.0",
        "bash -c 'npm install pkg@1.0.0'",
        "echo done; uv lock",
        "pip3 install requests==2.0.0",
        "pip3.12 install requests==2.0.0",
        "python3.12 -m pip install requests==2.0.0",
        "sudo -u root npm install pkg@1.0.0",
        "env -i npm install pkg@1.0.0",
        "env -u HOME npm install pkg@1.0.0",
        "timeout 60 npm install pkg@1.0.0",
        "bash -lc 'npm install pkg@1.0.0'",
        "sh -ec 'uv add pkg==1.0.0'",
        "eval 'npm install pkg@1.0.0'",
        "npm --prefix app install pkg@1.0.0",
        "echo $(npm install pkg@1.0.0)",
        "echo `uv add pkg==1.0.0`",
        "echo pkg | xargs npm install",
        "echo pkg | xargs -n 1 pip install",
        "./sfw npm install pkg@1.0.0",
        "yarn",
        "npm --prefix test install pkg@1.0.0",
        "npm --workspace run install pkg@1.0.0",
        "uv --directory run add pkg==1.0.0",
        "env -S 'npm install pkg@1.0.0'",
        "env --split-string='uv add pkg==1.0.0'",
        "env -Snpm\\ install\\ pkg@1.0.0",
        "echo a#b; npm install pkg@1.0.0",
        "FOO=sfw npm install pkg@1.0.0",
        "echo sfw; npm install pkg@1.0.0 'x",
        'echo "unterminated; npm install pkg@1.0.0',
    ],
)
def test_denies_unguarded_install(command: str) -> None:
    output = json.loads(run_hook(bash(command)))
    specific = output["hookSpecificOutput"]
    assert specific["permissionDecision"] == "deny"
    assert "sfw" in specific["permissionDecisionReason"]


@pytest.mark.parametrize(
    "command",
    [
        "sfw npm install pkg@1.0.0",
        "sfw uv add pkg==1.0.0",
        "cd app && sfw npm ci",
        "npm run build",
        "npm test",
        "uv run pytest",
        "uv pip list",
        "pip list",
        "poetry lock",
        "git status",
        'echo "npm install is guarded"',
        "brew install jq",
        "sudo -u root sfw npm install pkg@1.0.0",
        "/opt/homebrew/bin/sfw npm install pkg@1.0.0",
        "pip3 list",
        "uv run pytest tests/test_add.py",
        "uv run python add.py",
        "npm run install-hooks",
        "echo $(date)",
        "sudo ls /tmp",
        "bash -lc 'ls'",
        "cat <<'EOF'\nit's fine\nEOF",
    ],
)
def test_allows_other_commands(command: str) -> None:
    assert run_hook(bash(command)) == ""


@pytest.mark.parametrize(
    "stdin",
    [
        "",
        "not json",
        "[]",
        json.dumps({"tool_input": {}}),
        json.dumps({"tool_input": {"command": 1}}),
    ],
)
def test_ignores_malformed_input(stdin: str) -> None:
    assert run_hook(stdin) == ""


def test_unbalanced_quote_without_install_is_allowed() -> None:
    assert run_hook(bash("echo 'unterminated")) == ""


def test_unbalanced_quote_with_install_is_denied() -> None:
    output = json.loads(run_hook(bash("echo 'unterminated npm install")))
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_unbalanced_quote_with_sfw_is_allowed() -> None:
    assert run_hook(bash("sfw npm install pkg@1.0.0 'unterminated")) == ""
