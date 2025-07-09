"""Claude Code ツールハンドラ."""

from pathlib import Path
from typing import Dict, List, Optional

from ..config import ClaudeCodeConfig, ConfigManager, ToolType
from ..linker import LinkManager


class ClaudeCodeHandler:
    """Claude Code ツールハンドラ."""

    def __init__(self, config_manager: ConfigManager, link_manager: LinkManager) -> None:
        """初期化.

        Args:
            config_manager: 設定管理マネージャー
            link_manager: リンク管理マネージャー
        """
        self.config_manager = config_manager
        self.link_manager = link_manager
        self.tool_type = ToolType.CLAUDE_CODE

    @property
    def default_system_paths(self) -> List[Path]:
        """デフォルトのシステム設定パス一覧."""
        return [
            Path.home() / ".claude" / "settings.json",
            Path.home() / ".claude" / "settings.local.json",
        ]

    @property
    def default_project_paths(self) -> List[Path]:
        """デフォルトのプロジェクト設定パス一覧."""
        project_root = self.config_manager.project_root
        return [
            project_root / "configs" / "claude-code" / "settings.json",
            project_root / "configs" / "claude-code" / "settings.local.json",
        ]

    @property
    def default_context_paths(self) -> Dict[str, Path]:
        """デフォルトのコンテキストファイルパス一覧."""
        project_root = self.config_manager.project_root
        return {
            "system": Path.home() / ".claude" / "CLAUDE.md",
            "project": project_root / "CLAUDE.md",
            "config_dir": project_root / ".claude" / "CLAUDE.md",
        }

    def detect_existing_config(self) -> Optional[Path]:
        """既存の設定を検出."""
        for path in self.default_system_paths:
            if path.exists() and path.is_file():
                return path
        return None

    def import_config(
        self,
        source_path: Optional[Path] = None,
        target_path: Optional[Path] = None,
    ) -> ClaudeCodeConfig:
        """設定をインポート.

        Args:
            source_path: インポート元パス（None の場合は自動検出）
            target_path: インポート先パス（None の場合はデフォルト）

        Returns:
            ClaudeCodeConfig: インポートされた設定

        Raises:
            FileNotFoundError: 設定ファイルが見つからない
        """
        # ソースパスの決定
        if source_path is None:
            source_path = self.detect_existing_config()
            if source_path is None:
                raise FileNotFoundError("Claude Code の設定ファイルが見つかりません")

        # ターゲットパスの決定
        if target_path is None:
            target_path = self.default_project_paths[0]

        # 設定をインポート
        config = self.config_manager.import_tool_config(self.tool_type, source_path, target_path)

        return config  # type: ignore

    def create_link(
        self,
        system_path: Optional[Path] = None,
        project_path: Optional[Path] = None,
    ) -> bool:
        """設定ファイルをリンク.

        Args:
            system_path: システム設定パス（None の場合はデフォルト）
            project_path: プロジェクト設定パス（None の場合はプロジェクト設定から取得）

        Returns:
            bool: リンク成功フラグ

        Raises:
            FileNotFoundError: プロジェクト設定ファイルが見つからない
        """
        # プロジェクト設定パスの決定
        if project_path is None:
            project_config = self.config_manager.project_config
            tool_config = project_config.tools.get(self.tool_type.value)
            if tool_config is None or tool_config.project_config_path is None:
                raise FileNotFoundError("プロジェクト内に Claude Code 設定が見つかりません")
            project_path = tool_config.project_config_path

        # システム設定パスの決定
        if system_path is None:
            system_path = self.default_system_paths[0]

        # リンクを作成
        try:
            self.link_manager.create_link(project_path, system_path)
            return True
        except (OSError, FileNotFoundError):
            return False

    def remove_link(self, system_path: Optional[Path] = None) -> bool:
        """設定ファイルのリンクを削除.

        Args:
            system_path: システム設定パス（None の場合はデフォルト）

        Returns:
            bool: 削除成功フラグ
        """
        if system_path is None:
            system_path = self.default_system_paths[0]

        return self.link_manager.remove_link(system_path)

    def get_status(self) -> Dict[str, str]:
        """現在の状態を取得.

        Returns:
            Dict[str, str]: 状態情報
        """
        status = {}

        # プロジェクト設定の存在確認
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(self.tool_type.value)
        if tool_config and tool_config.project_config_path:
            if tool_config.project_config_path.exists():
                status["project_config"] = "存在"
            else:
                status["project_config"] = "不存在"
        else:
            status["project_config"] = "未設定"

        # システム設定のリンク状態確認
        for i, system_path in enumerate(self.default_system_paths):
            key = f"system_config_{i}"
            link_status = self.link_manager.check_link_status(system_path)
            status[key] = link_status.value

        return status

    def validate_config(self) -> Dict[str, bool]:
        """設定の妥当性を検証.

        Returns:
            Dict[str, bool]: 検証結果
        """
        results = {}

        # プロジェクト設定の検証
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(self.tool_type.value)

        results["has_project_config"] = tool_config is not None
        results["project_config_exists"] = (
            tool_config is not None
            and tool_config.project_config_path is not None
            and tool_config.project_config_path.exists()
        )

        # リンク状態の検証
        link_results = self.link_manager.validate_links()
        results["links_valid"] = link_results.get(self.tool_type.value, False)

        return results

    def detect_existing_context(self) -> Optional[Path]:
        """既存のコンテキストファイルを検出."""
        for path in self.default_context_paths.values():
            if path.exists() and path.is_file():
                return path
        return None

    def import_context(
        self,
        source_path: Optional[Path] = None,
        target_path: Optional[Path] = None,
    ) -> Path:
        """コンテキストファイルをインポート."""
        # ソースパスの決定
        if source_path is None:
            source_path = self.detect_existing_context()
            if source_path is None:
                raise FileNotFoundError("Claude Code のコンテキストファイルが見つかりません")

        # ターゲットパスの決定
        if target_path is None:
            target_path = self.default_context_paths["project"]

        # ファイルをコピー
        import shutil

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

        # プロジェクト設定を更新
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(self.tool_type.value)
        if tool_config:
            tool_config.project_context_path = target_path
            self.config_manager.save_project_config(project_config)

        return target_path

    def create_context_link(
        self,
        system_path: Optional[Path] = None,
        project_path: Optional[Path] = None,
    ) -> bool:
        """コンテキストファイルをリンク."""
        # プロジェクトパスの決定
        if project_path is None:
            project_config = self.config_manager.project_config
            tool_config = project_config.tools.get(self.tool_type.value)
            if tool_config is None or tool_config.project_context_path is None:
                raise FileNotFoundError(
                    "プロジェクト内に Claude Code コンテキストファイルが見つかりません"
                )
            project_path = tool_config.project_context_path

        # システムパスの決定
        if system_path is None:
            system_path = self.default_context_paths["config_dir"]

        # リンクを作成
        try:
            self.link_manager.create_link(project_path, system_path)
            return True
        except (OSError, FileNotFoundError):
            return False

    def create_default_context(self, path: Optional[Path] = None) -> Path:
        """デフォルトのコンテキストファイルを作成."""
        if path is None:
            path = self.default_context_paths["project"]

        content = """# Claude Code Project Context

## プロジェクト概要
このプロジェクトについての説明を記載してください。

## 技術スタック
- Python 3.12+
- 主要なライブラリ・フレームワーク

## アーキテクチャ
- プロジェクト構造
- 主要なコンポーネント

## 開発ガイドライン
- コーディング規約
- テスト方針
- 型ヒント必須

## 注意事項
- 重要な制約事項
- セキュリティ考慮事項
"""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        # プロジェクト設定を更新
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(self.tool_type.value)
        if tool_config:
            tool_config.project_context_path = path
            self.config_manager.save_project_config(project_config)

        return path

    def create_default_config(self, path: Optional[Path] = None) -> ClaudeCodeConfig:
        """デフォルト設定を作成.

        Args:
            path: 設定ファイルパス（None の場合はデフォルト）

        Returns:
            ClaudeCodeConfig: 作成された設定
        """
        if path is None:
            path = self.default_project_paths[0]

        # デフォルト設定を作成
        config = ClaudeCodeConfig(
            name=self.tool_type.value,
            system_config_path=self.default_system_paths[0],
            project_config_path=path,
            theme="dark",
            allowed_tools=["read", "write", "shell"],
        )

        # ファイルに保存
        self.config_manager.save_tool_config(config, path)

        # プロジェクト設定に追加
        project_config = self.config_manager.project_config
        project_config.tools[self.tool_type.value] = config
        self.config_manager.save_project_config(project_config)

        return config
