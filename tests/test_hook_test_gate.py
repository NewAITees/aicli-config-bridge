from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "project-configs" / ".claude" / "hooks" / "hook_test_gate.sh"


def make_fake_uv(bin_dir: Path, exit_code: int) -> Path:
    calls = bin_dir / "uv.calls"
    uv = bin_dir / "uv"
    uv.write_text(f'#!/bin/sh\necho "$@" >> "{calls}"\nexit {exit_code}\n')
    uv.chmod(0o755)
    return calls


def run_gate(
    tmp_path: Path,
    *,
    trusted: bool,
    with_venv: bool,
    uv_exit: int = 0,
    trust_file_exists: bool = True,
) -> tuple[subprocess.CompletedProcess[str], Path]:
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    if with_venv:
        (project / ".venv").mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = make_fake_uv(bin_dir, uv_exit)
    trust_file = tmp_path / "trusted"
    if trust_file_exists:
        trust_file.write_text(f"# trusted projects\n{project if trusted else tmp_path / 'other'}\n")
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "CLAUDE_PROJECT_DIR": str(project),
        "CLAUDE_TEST_GATE_TRUST_FILE": str(trust_file),
    }
    result = subprocess.run(
        ["/bin/bash", str(SCRIPT)], env=env, capture_output=True, text=True, check=False
    )
    return result, calls


def test_untrusted_project_is_not_executed(tmp_path: Path) -> None:
    result, calls = run_gate(tmp_path, trusted=False, with_venv=True, uv_exit=1)
    assert result.returncode == 0
    assert not calls.exists()


def test_missing_trust_file_does_not_execute(tmp_path: Path) -> None:
    result, calls = run_gate(
        tmp_path, trusted=True, with_venv=True, uv_exit=1, trust_file_exists=False
    )
    assert result.returncode == 0
    assert not calls.exists()


def test_trusted_project_runs_frozen_without_sync(tmp_path: Path) -> None:
    result, calls = run_gate(tmp_path, trusted=True, with_venv=True)
    assert result.returncode == 0
    assert calls.read_text().strip() == "run --frozen --no-sync pytest"


def test_failing_tests_block_completion(tmp_path: Path) -> None:
    result, _ = run_gate(tmp_path, trusted=True, with_venv=True, uv_exit=1)
    assert result.returncode == 2
    assert "テストが失敗しています" in result.stderr


def test_trusted_project_without_venv_does_not_install(tmp_path: Path) -> None:
    result, calls = run_gate(tmp_path, trusted=True, with_venv=False, uv_exit=1)
    assert result.returncode == 0
    assert not calls.exists()
