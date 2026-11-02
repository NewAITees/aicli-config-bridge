from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).parents[1] / "project-configs" / ".claude" / "hooks"
SCRIPT = HOOKS_DIR / "hook_pre_commands.sh"
# The PATH may resolve bash to the WSL launcher, which cannot read native paths.
BASH = shutil.which("bash") or "bash"
if os.name == "nt" and (git := shutil.which("git")):
    git_bash = Path(git).resolve().parents[1] / "bin" / "bash.exe"
    if git_bash.is_file():
        BASH = str(git_bash)

pytestmark = pytest.mark.skipif(shutil.which("jq") is None, reason="jq is required")


@pytest.fixture
def home(tmp_path: Path) -> Path:
    rules_dir = tmp_path / ".claude" / "hooks" / "rules"
    rules_dir.mkdir(parents=True)
    shutil.copy(HOOKS_DIR / "rules" / "hook_pre_commands_rules.json", rules_dir)
    return tmp_path


def run_hook(home: Path, command: str) -> str:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    # as_posix(): MSYS2 bash.exe parses its argv as POSIX, so a Windows
    # backslash path (e.g. "C:\...\hook.sh") loses every backslash to
    # escape-sequence collapsing and the script is "not found".
    result = subprocess.run(
        [BASH, SCRIPT.as_posix()],
        input=payload,
        env={**os.environ, "HOME": str(home)},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf build",
        "rm -fr build",
        "rm -r -f build",
        "rm -Rf build",
        "rm --recursive --force build",
        "rm   -rf   build",
        "rm\t-rf\tbuild",
        "ls && /bin/rm -rf build",
        "\\rm -rf build",
        "command rm -rf build",
        "{ rm -rf build; }",
        "(rm -fr build)",
        "/usr/bin/sudo ls",
        "\\sudo ls",
        "{ sudo ls; }",
        '"sudo" ls',
        "bash -c 'rm -rf build'",
        "git push --force origin main",
        "git push -f origin main",
        "git push origin main --force-with-lease",
        "git push origin +main",
        "git push -uf origin main",
        "git   reset   --hard HEAD~1",
        "git reset HEAD~1 --hard",
        "sudo ls",
        "ls; sudo ls",
        "terraform destroy",
        "terraform -chdir=infra apply",
        "kubectl -n prod delete pod x",
        "psql -c 'DROP   TABLE users'",
        "echo done\nrm -rf build",
    ],
)
def test_risky_commands_ask(home: Path, command: str) -> None:
    output = json.loads(run_hook(home, command))
    assert output["hookSpecificOutput"]["permissionDecision"] == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "rm file.txt",
        "rm -f file.txt",
        "ls -la",
        "git push origin main",
        "git push -u origin feature",
        "git push --follow-tags origin main",
        "git reset --soft HEAD~1",
        "cat /etc/sudoers.d/readme",
        "terraform plan",
        "kubectl get pods",
    ],
)
def test_routine_commands_pass(home: Path, command: str) -> None:
    assert run_hook(home, command) == ""
