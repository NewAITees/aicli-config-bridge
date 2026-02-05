"""Link blueprint models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LinkItemType(str, Enum):
    """リンクアイテムの種類."""

    FILE = "file"
    DIRECTORY = "directory"


class LinkItem(BaseModel):
    """リンク設計図の個別アイテム."""

    id: str = Field(..., description="リンクの一意識別子")
    name: str = Field(..., description="人間が読める説明")
    type: LinkItemType = Field(..., description="リンク対象の種類")
    source: str = Field(..., description="ソースパス(相対パス)")
    target: str = Field(..., description="ターゲットパス(~使用可能)")
    create_if_missing: bool = Field(default=False, description="ファイルがない場合に作成")
    default_content: str | None = Field(default=None, description="デフォルト内容")

    model_config = {"use_enum_values": True}


class LinksConfig(BaseModel):
    """リンク設計図全体."""

    version: str = Field(default="0.2.0", description="スキーマバージョン")
    description: str = Field(default="", description="設定の説明")
    links: list[LinkItem] = Field(default_factory=list, description="リンクアイテムのリスト")

    model_config = {"use_enum_values": True}
