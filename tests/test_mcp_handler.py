"""MCP ハンドラのテスト."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aicli_config_bridge.config import ClaudeCodeConfig, ConfigManager, MCPServer, ToolType
from aicli_config_bridge.linker import LinkManager
from aicli_config_bridge.tools import MCPHandler


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    return tmp_path


def test_load_mcp_servers_formats(project_root: Path) -> None:
    config_manager = ConfigManager(project_root)
    handler = MCPHandler(config_manager, LinkManager(config_manager))

    claude_path = project_root / "claude.json"
    claude_path.write_text(
        json.dumps(
            {"mcpServers": {"fs": {"command": "mcp-fs", "args": ["-a"], "env": {"A": "1"}}}}
        ),
        encoding="utf-8",
    )
    servers = handler.load_mcp_servers(claude_path)
    assert servers["fs"].command == "mcp-fs"

    gemini_path = project_root / "gemini.json"
    gemini_path.write_text(
        json.dumps({"mcp_servers": {"stdio": {"command": "mcp-stdio", "args": [], "env": {}}}}),
        encoding="utf-8",
    )
    servers = handler.load_mcp_servers(gemini_path)
    assert servers["stdio"].command == "mcp-stdio"

    direct_path = project_root / "direct.json"
    direct_path.write_text(
        json.dumps({"x": {"command": "mcp-x", "args": ["1"], "env": {}}}),
        encoding="utf-8",
    )
    servers = handler.load_mcp_servers(direct_path)
    assert servers["x"].args == ["1"]


def test_save_import_and_manage_mcp(project_root: Path) -> None:
    config_manager = ConfigManager(project_root)
    handler = MCPHandler(config_manager, LinkManager(config_manager))

    # project config needs tool entry for updates
    tool_config = ClaudeCodeConfig(
        name=ToolType.CLAUDE_CODE.value,
        system_config_path=project_root / "system" / "settings.json",
        project_config_path=project_root / "configs" / "claude-code" / "settings.json",
    )
    project_config = config_manager.project_config
    project_config.tools[ToolType.CLAUDE_CODE.value] = tool_config
    config_manager.save_project_config(project_config)

    servers = {"fs": MCPServer(command="mcp-fs", args=[], env={})}
    target = project_root / "configs" / "claude-code" / "mcp_servers.json"
    handler.save_mcp_servers(servers, target, ToolType.CLAUDE_CODE)
    assert target.exists()

    imported = handler.import_mcp_config(
        ToolType.CLAUDE_CODE, source_path=target, target_path=target
    )
    assert imported == target

    handler.add_mcp_server(ToolType.CLAUDE_CODE, "stdio", MCPServer(command="mcp-stdio"))
    listed = handler.list_mcp_servers(ToolType.CLAUDE_CODE)
    assert "stdio" in listed

    removed = handler.remove_mcp_server(ToolType.CLAUDE_CODE, "stdio")
    assert removed is True

    status = handler.get_mcp_status(ToolType.CLAUDE_CODE)
    assert status["project_mcp"] in {"存在", "不存在"}
