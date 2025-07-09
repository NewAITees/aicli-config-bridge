"""
設定データモデル定義

このモジュールは aicli-config-bridge で使用するデータモデルを定義します。
Pydantic を使用して型安全な設定データの管理を行います。

主なモデル：
- ToolType: サポートされるAI CLIツールの種類
- LinkStatus: リンク状態の定義
- MCPServer: MCPサーバー設定
- ToolConfig: ツール設定の基底クラス
- ClaudeCodeConfig: Claude Code設定
- GeminiCLIConfig: Gemini CLI設定
- LinkInfo: リンク情報
- ProjectConfig: プロジェクト設定

Usage:
    from aicli_config_bridge.config.models import ProjectConfig, ToolType
    
    config = ProjectConfig(
        name="my-project",
        tools={
            ToolType.CLAUDE_CODE: {...}
        }
    )
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ToolType(str, Enum):
    """サポートするAI CLI ツールタイプ."""

    CLAUDE_CODE = "claude-code"
    GEMINI_CLI = "gemini-cli"


class LinkStatus(str, Enum):
    """リンク状態."""

    LINKED = "linked"
    NOT_LINKED = "not_linked"
    BROKEN = "broken"


class MCPServer(BaseModel):
    """MCP サーバー設定."""

    command: str = Field(..., description="実行コマンド")
    args: List[str] = Field(default_factory=list, description="コマンド引数")
    env: Dict[str, str] = Field(default_factory=dict, description="環境変数")


class ToolConfig(BaseModel):
    """ツール設定の基底クラス."""

    tool_type: ToolType = Field(..., description="ツールタイプ")
    name: str = Field(..., description="ツール名")
    system_config_path: Path = Field(..., description="システム設定ファイルパス")
    project_config_path: Optional[Path] = Field(None, description="プロジェクト設定ファイルパス")
    # マークダウンファイルの管理を追加
    system_context_path: Optional[Path] = Field(
        None, description="システムコンテキストファイルパス"
    )
    project_context_path: Optional[Path] = Field(
        None, description="プロジェクトコンテキストファイルパス"
    )
    is_enabled: bool = Field(True, description="有効フラグ")

    @field_validator(
        "system_config_path",
        "project_config_path",
        "system_context_path",
        "project_context_path",
        mode="before",
    )
    def validate_paths(cls, v: Any) -> Optional[Path]:  # noqa: ANN401
        """パスのバリデーション."""
        if v is None:
            return v
        return Path(v).expanduser().resolve()


class ClaudeCodeConfig(ToolConfig):
    """Claude Code 設定."""

    tool_type: ToolType = Field(default=ToolType.CLAUDE_CODE)
    mcp_servers: Dict[str, MCPServer] = Field(default_factory=dict, description="MCP サーバー設定")
    allowed_tools: List[str] = Field(default_factory=list, description="許可ツール")
    theme: str = Field(default="dark", description="テーマ")

    model_config = {"extra": "allow"}  # 追加設定を許可


class GeminiCLIConfig(ToolConfig):
    """Gemini CLI 設定."""

    tool_type: ToolType = Field(default=ToolType.GEMINI_CLI)
    theme: str = Field(default="Atom One", description="テーマ")
    auto_accept: bool = Field(default=False, description="自動承認")
    checkpointing: Dict[str, Any] = Field(default_factory=dict, description="チェックポイント設定")
    mcp_servers: Dict[str, MCPServer] = Field(default_factory=dict, description="MCP サーバー設定")

    model_config = {"extra": "allow"}  # 追加設定を許可


class LinkInfo(BaseModel):
    """リンク情報."""

    source_path: Path = Field(..., description="ソースパス")
    target_path: Path = Field(..., description="ターゲットパス")
    status: LinkStatus = Field(..., description="リンク状態")
    created_at: Optional[str] = Field(None, description="作成日時")

    @field_validator("source_path", "target_path", mode="before")
    def validate_paths(cls, v: Any) -> Path:  # noqa: ANN401
        """パスのバリデーション."""
        return Path(v).expanduser().resolve()


class ProjectConfig(BaseModel):
    """プロジェクト設定."""

    name: str = Field(..., description="プロジェクト名")
    version: str = Field(default="0.1.0", description="バージョン")
    description: Optional[str] = Field(None, description="説明")
    root_path: Path = Field(..., description="プロジェクトルートパス")
    tools: Dict[str, ToolConfig] = Field(default_factory=dict, description="ツール設定")
    links: Dict[str, LinkInfo] = Field(default_factory=dict, description="リンク情報")
    profiles: List[str] = Field(default_factory=list, description="利用可能プロファイル")
    active_profile: Optional[str] = Field(None, description="アクティブプロファイル")

    @field_validator("root_path", mode="before")
    def validate_root_path(cls, v: Any) -> Path:  # noqa: ANN401
        """ルートパスのバリデーション."""
        return Path(v).expanduser().resolve()

    model_config = {"extra": "forbid", "validate_assignment": True}
