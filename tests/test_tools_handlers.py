"""ツールハンドラのテスト."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aicli_config_bridge.config import ConfigManager, ToolType
from aicli_config_bridge.linker import LinkManager
from aicli_config_bridge.tools import ClaudeCodeHandler, GeminiCLIHandler, MarkdownHandler


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    return tmp_path


def test_claude_code_default_config_and_link(project_root: Path) -> None:
    config_manager = ConfigManager(project_root)
    link_manager = LinkManager(config_manager)
    handler = ClaudeCodeHandler(config_manager, link_manager)

    config = handler.create_default_config()
    assert config.project_config_path is not None
    assert config.project_config_path.exists()

    data = json.loads(config.project_config_path.read_text(encoding="utf-8"))
    assert data["theme"] == "dark"
    assert "allowed_tools" in data

    system_path = project_root / "system" / "claude-settings.json"
    assert handler.create_link(system_path=system_path) is True
    assert system_path.exists()


def test_claude_code_context_import_and_link(project_root: Path) -> None:
    config_manager = ConfigManager(project_root)
    link_manager = LinkManager(config_manager)
    handler = ClaudeCodeHandler(config_manager, link_manager)

    # tool config must exist for context update
    handler.create_default_config()

    source = project_root / "source" / "CLAUDE.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("source", encoding="utf-8")

    target = project_root / "CLAUDE.md"
    imported = handler.import_context(source_path=source, target_path=target)
    assert imported == target
    assert target.read_text(encoding="utf-8") == "source"

    system_path = project_root / ".claude" / "CLAUDE.md"
    assert handler.create_context_link(system_path=system_path) is True
    assert system_path.exists()


def test_gemini_default_config_and_status(project_root: Path) -> None:
    config_manager = ConfigManager(project_root)
    link_manager = LinkManager(config_manager)
    handler = GeminiCLIHandler(config_manager, link_manager)

    config = handler.create_default_config()
    assert config.project_config_path is not None
    assert config.project_config_path.exists()

    status = handler.get_status()
    assert status["project_config"] in {"存在", "不存在", "未設定"}


def test_markdown_handler_default_and_import(project_root: Path) -> None:
    config_manager = ConfigManager(project_root)
    link_manager = LinkManager(config_manager)
    handler = MarkdownHandler(config_manager, link_manager)

    claude_path = handler.create_default_markdown(ToolType.CLAUDE_CODE)
    assert claude_path.exists()

    source = project_root / "source" / "GEMINI.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("gemini source", encoding="utf-8")

    target = project_root / "GEMINI.md"
    imported = handler.import_markdown(ToolType.GEMINI_CLI, source_path=source, target_path=target)
    assert imported == target
    assert target.read_text(encoding="utf-8") == "gemini source"

    system_path = project_root / ".gemini" / "GEMINI.md"
    assert handler.create_link(ToolType.GEMINI_CLI, system_path=system_path) is True
    assert system_path.exists()
