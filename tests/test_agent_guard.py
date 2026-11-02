from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "project-configs/shared/hooks/agent_guard.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("agent_guard_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "command",
    [
        "npm install pkg@1.0.0",
        "env -S 'uv add pkg==1.0.0'",
        "echo $(npm install pkg@1.0.0)",
        "echo sfw; npm install pkg@1.0.0 'x",
        "npm.cmd install pkg@1.0.0",
        '"C:/Program Files/nodejs/npm.cmd" install pkg@1.0.0',
        "pip.exe install pkg==1.0.0",
        "NPM.CMD install pkg@1.0.0",
        "UV.EXE sync",
        'powershell -Command "NPM.CMD install pkg@1.0.0"',
        'cmd /c "npm install pkg@1.0.0"',
        'CMD.EXE /d /s /c "npm.cmd install pkg@1.0.0"',
        "cmd /c npm install pkg@1.0.0",
        'powershell -Command "npm install pkg@1.0.0"',
    ],
)
def test_sfw_is_reused_for_unguarded_fetches(command):
    assert load_guard().evaluate_pre({"tool_input": {"command": command}})["decision"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "sfw npm install pkg@1.0.0",
        "sfw uv add pkg==1.0.0",
        "git status",
        "uv run --frozen --no-sync pytest",
        "npm test",
        "rd empty-folder",
        "rmdir empty-folder",
        'cmd /c "sfw npm install pkg@1.0.0"',
        'CMD.EXE /d /s /c "git.exe status"',
        "NPM install pkg@1.0.0",  # POSIX names without a Windows suffix stay case-sensitive.
        "SFw npm install pkg@1.0.0",
    ],
)
def test_routine_commands_are_allowed(command):
    assert load_guard().evaluate_pre({"tool_input": {"command": command}})["decision"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "git.exe reset --hard HEAD~1",
        "rm -rf build",
        "rm.exe -rf build",
        r'"C:\Program Files\Git\usr\bin\rm.exe" -rf build',
        "TERRAFORM.EXE apply",
        r'"C:\Program Files\Terraform\terraform.exe" apply',
        r'"C:\Program Files\Git\cmd\git.exe" reset --hard HEAD~1',
        "kubectl.exe delete pod x",
        "SUDO.EXE ls",
        "rm -fr build",
        "rm -r -f build",
        "rm\t-Rf build",
        "ls && /bin/rm -rf build",
        r"\rm -rf build",
        "{ rm -rf build; }",
        '"sudo" ls',
        "git push origin main --force-with-lease",
        "git push origin +main",
        "git reset HEAD~1 --hard",
        "terraform -chdir=infra apply",
        "kubectl -n prod delete pod x",
        "psql -c 'DROP   TABLE users'",
        "echo done\nrm -rf build",
        "Remove-Item -Recurse folder",
        "Remove-Item folder -r -Force",
        "rmdir -Recurse folder",
        "rd folder -r",
        "RMDIR -RECURSE folder",
        "cmd /c rd /s /q folder",
    ],
)
def test_risky_original_commands_require_approval(command):
    result = load_guard().evaluate_pre({"tool_input": {"command": command}})
    assert result["decision"] == "ask"
    assert result["reason"]


@pytest.mark.parametrize("payload", [{}, [], {"tool_input": {}}, {"tool_input": {"command": 3}}])
def test_malformed_shell_payload_is_denied(payload):
    assert load_guard().evaluate_pre(payload)["decision"] == "deny"


def make_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[project]\nname='test'\n")
    (project / ".venv").mkdir()
    return project


def test_untrusted_project_never_executes_tests(tmp_path, monkeypatch):
    module = load_guard()
    project = make_project(tmp_path)
    monkeypatch.setattr(module, "trust_file_for", lambda _: tmp_path / "absent")
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("must not execute"))
    result = module.evaluate_stop({"cwd": str(project)}, "codex")
    assert result["decision"] == "allow"
    assert "未実行" in result["reason"]


def test_trust_does_not_extend_to_child_directories(tmp_path, monkeypatch):
    module = load_guard()
    project = make_project(tmp_path)
    trust = tmp_path / "trusted"
    trust.write_text(str(tmp_path))
    monkeypatch.setattr(module, "trust_file_for", lambda _: trust)
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("must not execute"))
    assert module.evaluate_stop({"cwd": str(project)}, "codex")["decision"] == "allow"


@pytest.mark.parametrize("exit_code, decision", [(0, "allow"), (1, "deny")])
def test_trusted_test_run_never_resolves_dependencies(tmp_path, monkeypatch, exit_code, decision):
    module = load_guard()
    project = make_project(tmp_path)
    trust = tmp_path / "trusted"
    trust.write_text(f"# comment\n{project}\n")
    monkeypatch.setattr(module, "trust_file_for", lambda _: trust)
    monkeypatch.setattr(module.shutil, "which", lambda name: f"/tools/{name}")
    calls = []

    def run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, exit_code, "output", "")

    monkeypatch.setattr(module.subprocess, "run", run)
    result = module.evaluate_stop({"cwd": str(project)}, "codex")
    assert result["decision"] == decision
    assert calls[0][0] == ["/tools/uv", "run", "--frozen", "--no-sync", "pytest"]
    assert calls[0][1]["cwd"] == project.resolve()
    assert calls[0][1]["timeout"] > 0


def test_timeout_blocks_completion(tmp_path, monkeypatch):
    module = load_guard()
    project = make_project(tmp_path)
    trust = tmp_path / "trusted"
    trust.write_text(str(project))
    monkeypatch.setattr(module, "trust_file_for", lambda _: trust)
    monkeypatch.setattr(module.shutil, "which", lambda name: f"/tools/{name}")

    def run(args, **kwargs):
        raise subprocess.TimeoutExpired(args, 120)

    monkeypatch.setattr(module.subprocess, "run", run)
    assert module.evaluate_stop({"cwd": str(project)}, "codex")["decision"] == "deny"


def test_trusted_project_without_dependencies_is_explicitly_untested(tmp_path, monkeypatch):
    module = load_guard()
    project = tmp_path / "project"
    project.mkdir()
    (project / "package.json").write_text('{"scripts":{"test":"echo test"}}')
    trust = tmp_path / "trusted"
    trust.write_text(str(project))
    monkeypatch.setattr(module, "trust_file_for", lambda _: trust)
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("must not execute"))
    result = module.evaluate_stop({"cwd": str(project)}, "opencode")
    assert result["decision"] == "allow"
    assert "未実行" in result["reason"]
