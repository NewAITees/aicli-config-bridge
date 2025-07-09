"""MCP サーバー管理ハンドラ."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from ..config import ConfigManager, MCPServer, ToolType
from ..linker import LinkManager


class MCPHandler:
    """MCP サーバー管理ハンドラ."""

    def __init__(self, config_manager: ConfigManager, link_manager: LinkManager) -> None:
        """初期化.

        Args:
            config_manager: 設定管理マネージャー
            link_manager: リンク管理マネージャー
        """
        self.config_manager = config_manager
        self.link_manager = link_manager

    @property
    def claude_mcp_paths(self) -> Dict[str, Path]:
        """Claude Code の MCP 設定パス."""
        return {
            "system": Path.home() / ".claude" / "mcp_servers.json",
            "project": self.config_manager.project_root
            / "configs"
            / "claude-code"
            / "mcp_servers.json",
        }

    @property
    def gemini_mcp_paths(self) -> Dict[str, Path]:
        """Gemini CLI の MCP 設定パス."""
        return {
            "system": Path.home() / ".gemini" / "mcp_servers.json",
            "project": self.config_manager.project_root
            / "configs"
            / "gemini-cli"
            / "mcp_servers.json",
        }

    def get_mcp_paths(self, tool_type: ToolType) -> Dict[str, Path]:
        """指定ツールの MCP 設定パスを取得."""
        if tool_type == ToolType.CLAUDE_CODE:
            return self.claude_mcp_paths
        elif tool_type == ToolType.GEMINI_CLI:
            return self.gemini_mcp_paths
        else:
            raise ValueError(f"サポートされていないツール: {tool_type}")

    def detect_existing_mcp_config(self, tool_type: ToolType) -> Optional[Path]:
        """既存の MCP 設定を検出."""
        paths = self.get_mcp_paths(tool_type)

        for path in paths.values():
            if path.exists() and path.is_file():
                return path
        return None

    def load_mcp_servers(self, config_path: Path) -> Dict[str, MCPServer]:
        """MCP サーバー設定を読み込み."""
        if not config_path.exists():
            return {}

        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Claude Code 形式
            if "mcpServers" in data:
                servers = {}
                for name, server_data in data["mcpServers"].items():
                    servers[name] = MCPServer(
                        command=server_data.get("command", ""),
                        args=server_data.get("args", []),
                        env=server_data.get("env", {}),
                    )
                return servers

            # Gemini CLI 形式
            elif "mcp_servers" in data:
                servers = {}
                for name, server_data in data["mcp_servers"].items():
                    servers[name] = MCPServer(
                        command=server_data.get("command", ""),
                        args=server_data.get("args", []),
                        env=server_data.get("env", {}),
                    )
                return servers

            # 直接形式
            else:
                servers = {}
                for name, server_data in data.items():
                    if isinstance(server_data, dict):
                        servers[name] = MCPServer(
                            command=server_data.get("command", ""),
                            args=server_data.get("args", []),
                            env=server_data.get("env", {}),
                        )
                return servers

        except (json.JSONDecodeError, KeyError, TypeError):
            return {}

    def save_mcp_servers(
        self, servers: Dict[str, MCPServer], config_path: Path, tool_type: ToolType
    ) -> None:
        """MCP サーバー設定を保存."""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # フォーマット決定
        if tool_type == ToolType.CLAUDE_CODE:
            # Claude Code 形式
            data = {
                "mcpServers": {
                    name: {
                        "command": server.command,
                        "args": server.args,
                        "env": server.env,
                    }
                    for name, server in servers.items()
                }
            }
        elif tool_type == ToolType.GEMINI_CLI:
            # Gemini CLI 形式
            data = {
                "mcp_servers": {
                    name: {
                        "command": server.command,
                        "args": server.args,
                        "env": server.env,
                    }
                    for name, server in servers.items()
                }
            }
        else:
            raise ValueError(f"サポートされていないツール: {tool_type}")

        with config_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_mcp_config(
        self,
        tool_type: ToolType,
        source_path: Optional[Path] = None,
        target_path: Optional[Path] = None,
    ) -> Path:
        """MCP 設定をインポート."""
        # ソースパスの決定
        if source_path is None:
            source_path = self.detect_existing_mcp_config(tool_type)
            if source_path is None:
                raise FileNotFoundError(f"{tool_type.value} の MCP 設定ファイルが見つかりません")

        # ターゲットパスの決定
        if target_path is None:
            paths = self.get_mcp_paths(tool_type)
            target_path = paths["project"]

        # MCP サーバー設定を読み込み
        servers = self.load_mcp_servers(source_path)

        # プロジェクト設定に保存
        self.save_mcp_servers(servers, target_path, tool_type)

        # プロジェクト設定を更新
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(tool_type.value)
        if tool_config:
            tool_config.mcp_servers = servers
            self.config_manager.save_project_config(project_config)

        return target_path

    def create_mcp_link(
        self,
        tool_type: ToolType,
        system_path: Optional[Path] = None,
        project_path: Optional[Path] = None,
    ) -> bool:
        """MCP 設定をリンク."""
        # プロジェクトパスの決定
        if project_path is None:
            paths = self.get_mcp_paths(tool_type)
            project_path = paths["project"]

        # システムパスの決定
        if system_path is None:
            paths = self.get_mcp_paths(tool_type)
            system_path = paths["system"]

        # リンクを作成
        try:
            self.link_manager.create_link(project_path, system_path)
            return True
        except (OSError, FileNotFoundError):
            return False

    def create_default_mcp_config(self, tool_type: ToolType, path: Optional[Path] = None) -> Path:
        """デフォルトの MCP 設定を作成."""
        if path is None:
            paths = self.get_mcp_paths(tool_type)
            path = paths["project"]

        # デフォルトのMCPサーバー設定
        default_servers = {
            "filesystem": MCPServer(command="mcp-server-filesystem", args=[], env={}),
            "stdio": MCPServer(command="mcp-server-stdio", args=[], env={}),
        }

        # 設定を保存
        self.save_mcp_servers(default_servers, path, tool_type)

        # プロジェクト設定を更新
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(tool_type.value)
        if tool_config:
            tool_config.mcp_servers = default_servers
            self.config_manager.save_project_config(project_config)

        return path

    def list_mcp_servers(self, tool_type: ToolType) -> Dict[str, MCPServer]:
        """MCP サーバー一覧を取得."""
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(tool_type.value)

        if tool_config and tool_config.mcp_servers:
            return tool_config.mcp_servers

        # プロジェクト設定に見つからない場合はファイルから読み込み
        paths = self.get_mcp_paths(tool_type)
        for path in paths.values():
            if path.exists():
                return self.load_mcp_servers(path)

        return {}

    def add_mcp_server(self, tool_type: ToolType, name: str, server: MCPServer) -> None:
        """MCP サーバーを追加."""
        servers = self.list_mcp_servers(tool_type)
        servers[name] = server

        # プロジェクト設定に保存
        paths = self.get_mcp_paths(tool_type)
        project_path = paths["project"]
        self.save_mcp_servers(servers, project_path, tool_type)

        # プロジェクト設定を更新
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(tool_type.value)
        if tool_config:
            tool_config.mcp_servers = servers
            self.config_manager.save_project_config(project_config)

    def remove_mcp_server(self, tool_type: ToolType, name: str) -> bool:
        """MCP サーバーを削除."""
        servers = self.list_mcp_servers(tool_type)

        if name not in servers:
            return False

        del servers[name]

        # プロジェクト設定に保存
        paths = self.get_mcp_paths(tool_type)
        project_path = paths["project"]
        self.save_mcp_servers(servers, project_path, tool_type)

        # プロジェクト設定を更新
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(tool_type.value)
        if tool_config:
            tool_config.mcp_servers = servers
            self.config_manager.save_project_config(project_config)

        return True

    def get_mcp_status(self, tool_type: ToolType) -> Dict[str, str]:
        """MCP 設定の状態を取得."""
        status = {}
        paths = self.get_mcp_paths(tool_type)

        # プロジェクト設定の存在確認
        project_path = paths["project"]
        if project_path.exists():
            status["project_mcp"] = "存在"
        else:
            status["project_mcp"] = "不存在"

        # システム設定のリンク状態確認
        system_path = paths["system"]
        link_status = self.link_manager.check_link_status(system_path)
        status["system_mcp"] = link_status.value

        return status
