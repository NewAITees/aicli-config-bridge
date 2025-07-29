"""
設定管理マネージャー

このモジュールは AI CLI ツールの設定ファイルの管理を行います。
プロジェクト設定の読み込み・保存、各種AI CLIツールの設定検出、
環境変数の置換処理などを提供します。

主な機能：
- プロジェクト設定の管理 (config.json)
- AI CLI ツールの設定検出 (Claude Code, Gemini CLI)
- 環境変数の置換処理 (${VAR_NAME} 形式)
- 設定ファイルの検証

Usage:
    from aicli_config_bridge.config import ConfigManager

    manager = ConfigManager()

    # 設定を検出
    detected = manager.detect_tool_configs()

    # 環境変数を置換
    config_data = manager.substitute_env_vars(config_data)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union

from pydantic import ValidationError

from .models import ClaudeCodeConfig, GeminiCLIConfig, ProjectConfig, ToolConfig, ToolType

T = TypeVar("T", bound=ToolConfig)


class ConfigManager:
    """設定管理マネージャー."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """初期化.

        Args:
            project_root: プロジェクトルートパス
        """
        self.project_root = project_root or Path.cwd()
        self.config_file = self.project_root / "aicli-config.json"
        self._project_config: Optional[ProjectConfig] = None

    @property
    def project_config(self) -> ProjectConfig:
        """プロジェクト設定を取得."""
        if self._project_config is None:
            self._project_config = self.load_project_config()
        return self._project_config

    def load_project_config(self) -> ProjectConfig:
        """プロジェクト設定をロード."""
        if not self.config_file.exists():
            # デフォルト設定を作成
            return ProjectConfig(
                name=self.project_root.name,
                root_path=self.project_root,
            )

        try:
            with open(self.config_file, encoding="utf-8") as f:
                data = json.load(f)
            return ProjectConfig.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"設定ファイルの読み込みに失敗しました: {e}") from e

    def save_project_config(self, config: Optional[ProjectConfig] = None) -> None:
        """プロジェクト設定を保存."""
        config = config or self.project_config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=2, ensure_ascii=False, default=str)

        self._project_config = config

    def load_tool_config(self, tool_type: ToolType, config_path: Path) -> ToolConfig:
        """ツール設定をロード."""
        if not config_path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON形式が正しくありません: {e}") from e

        config_class = self._get_config_class(tool_type)
        try:
            return config_class(
                tool_type=tool_type,
                name=tool_type.value,
                system_config_path=config_path,
                **data,
            )
        except ValidationError as e:
            raise ValueError(f"設定データが正しくありません: {e}") from e

    def save_tool_config(self, config: ToolConfig, config_path: Path) -> None:
        """ツール設定を保存."""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # ツール固有の設定のみを抽出
        data = config.model_dump(
            exclude={
                "tool_type",
                "name",
                "system_config_path",
                "project_config_path",
                "is_enabled",
            }
        )

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def detect_tool_configs(self) -> Dict[ToolType, Optional[Path]]:
        """既存のツール設定を検出."""
        detected = {}

        # Claude Code の検出
        claude_paths = [
            Path.home() / ".claude" / "settings.json",
            Path.cwd() / ".claude" / "settings.json",
        ]
        detected[ToolType.CLAUDE_CODE] = self._find_existing_config(claude_paths)

        # Gemini CLI の検出
        gemini_paths = [
            Path.home() / ".gemini" / "settings.json",
            Path.cwd() / ".gemini" / "settings.json",
        ]
        detected[ToolType.GEMINI_CLI] = self._find_existing_config(gemini_paths)

        return detected

    def import_tool_config(
        self, tool_type: ToolType, source_path: Path, target_path: Path
    ) -> ToolConfig:
        """ツール設定をインポート."""
        if not source_path.exists():
            raise FileNotFoundError(f"インポート元ファイルが見つかりません: {source_path}")

        # 設定をロード・検証
        config = self.load_tool_config(tool_type, source_path)

        # プロジェクト設定パスを設定
        config.project_config_path = target_path

        # プロジェクト内に保存
        self.save_tool_config(config, target_path)

        # プロジェクト設定に追加
        project_config = self.project_config
        project_config.tools[tool_type.value] = config
        self.save_project_config(project_config)

        return config

    def substitute_env_vars(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """環境変数を置換."""
        if isinstance(data, dict):
            return {k: self.substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            return self._substitute_string_env_vars(data)
        else:
            return data

    def _substitute_string_env_vars(self, value: str) -> str:
        """文字列内の環境変数を置換."""
        import re

        def replace_env_var(match: Any) -> str:  # noqa: ANN401
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)

        # ${VAR_NAME} または ${VAR_NAME:-default} 形式をサポート
        pattern = r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*?))?\}"
        return re.sub(pattern, replace_env_var, value)

    def _get_config_class(self, tool_type: ToolType) -> Type[ToolConfig]:
        """ツールタイプに対応する設定クラスを取得."""
        mapping = {
            ToolType.CLAUDE_CODE: ClaudeCodeConfig,
            ToolType.GEMINI_CLI: GeminiCLIConfig,
        }
        return mapping[tool_type]

    def _find_existing_config(self, paths: list[Path]) -> Optional[Path]:
        """既存の設定ファイルを検索."""
        for path in paths:
            if path.exists() and path.is_file():
                return path
        return None
