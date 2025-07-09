"""マークダウンファイル管理ハンドラ."""

from pathlib import Path
from typing import Dict, List, Optional

from ..config import ConfigManager, ToolType
from ..linker import LinkManager


class MarkdownHandler:
    """マークダウンファイル管理ハンドラ."""

    def __init__(self, config_manager: ConfigManager, link_manager: LinkManager) -> None:
        """初期化.

        Args:
            config_manager: 設定管理マネージャー
            link_manager: リンク管理マネージャー
        """
        self.config_manager = config_manager
        self.link_manager = link_manager

    @property
    def claude_md_paths(self) -> Dict[str, Path]:
        """Claude Code のマークダウンファイルパス."""
        project_root = self.config_manager.project_root
        return {
            "project_root": project_root / "CLAUDE.md",
            "claude_dir": project_root / ".claude" / "CLAUDE.md",
            "system_global": Path.home() / "CLAUDE.md",
        }

    @property
    def gemini_md_paths(self) -> Dict[str, Path]:
        """Gemini CLI のマークダウンファイルパス."""
        project_root = self.config_manager.project_root
        return {
            "project_root": project_root / "GEMINI.md",
            "gemini_dir": project_root / ".gemini" / "GEMINI.md",
            "system_global": Path.home() / "GEMINI.md",
        }

    def detect_existing_markdown(self, tool_type: ToolType) -> List[Path]:
        """既存のマークダウンファイルを検出.

        Args:
            tool_type: ツールタイプ

        Returns:
            List[Path]: 検出されたファイルパスのリスト
        """
        existing_files = []

        if tool_type == ToolType.CLAUDE_CODE:
            paths = self.claude_md_paths
        elif tool_type == ToolType.GEMINI_CLI:
            paths = self.gemini_md_paths
        else:
            return existing_files

        for location, path in paths.items():
            if path.exists() and path.is_file():
                existing_files.append(path)

        return existing_files

    def import_markdown(
        self,
        tool_type: ToolType,
        source_path: Optional[Path] = None,
        target_path: Optional[Path] = None,
    ) -> Path:
        """マークダウンファイルをインポート.

        Args:
            tool_type: ツールタイプ
            source_path: インポート元パス（None の場合は自動検出）
            target_path: インポート先パス（None の場合はデフォルト）

        Returns:
            Path: インポート先パス

        Raises:
            FileNotFoundError: ファイルが見つからない
        """
        # ソースパスの決定
        if source_path is None:
            existing_files = self.detect_existing_markdown(tool_type)
            if not existing_files:
                raise FileNotFoundError(f"{tool_type.value} のマークダウンファイルが見つかりません")
            source_path = existing_files[0]  # 最初に見つかったファイルを使用

        # ターゲットパスの決定
        if target_path is None:
            if tool_type == ToolType.CLAUDE_CODE:
                target_path = self.claude_md_paths["project_root"]
            elif tool_type == ToolType.GEMINI_CLI:
                target_path = self.gemini_md_paths["project_root"]
            else:
                raise ValueError(f"サポートされていないツール: {tool_type}")

        # ファイルをコピー
        import shutil

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

        # プロジェクト設定を更新
        self._update_project_config(tool_type, target_path)

        return target_path

    def create_link(
        self,
        tool_type: ToolType,
        system_path: Optional[Path] = None,
        project_path: Optional[Path] = None,
    ) -> bool:
        """マークダウンファイルをリンク.

        Args:
            tool_type: ツールタイプ
            system_path: システムパス（None の場合はデフォルト）
            project_path: プロジェクトパス（None の場合はプロジェクト設定から取得）

        Returns:
            bool: リンク成功フラグ
        """
        # プロジェクトパスの決定
        if project_path is None:
            project_config = self.config_manager.project_config
            tool_config = project_config.tools.get(tool_type.value)
            if tool_config is None or tool_config.project_context_path is None:
                raise FileNotFoundError(
                    f"プロジェクト内に {tool_type.value} のマークダウンファイルが見つかりません"
                )
            project_path = tool_config.project_context_path

        # システムパスの決定
        if system_path is None:
            if tool_type == ToolType.CLAUDE_CODE:
                system_path = self.claude_md_paths["claude_dir"]
            elif tool_type == ToolType.GEMINI_CLI:
                system_path = self.gemini_md_paths["gemini_dir"]
            else:
                raise ValueError(f"サポートされていないツール: {tool_type}")

        # リンクを作成
        try:
            self.link_manager.create_link(project_path, system_path)
            return True
        except (OSError, FileNotFoundError):
            return False

    def get_status(self, tool_type: ToolType) -> Dict[str, str]:
        """マークダウンファイルの状態を取得.

        Args:
            tool_type: ツールタイプ

        Returns:
            Dict[str, str]: 状態情報
        """
        status = {}

        # プロジェクトファイルの存在確認
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(tool_type.value)

        if tool_config and tool_config.project_context_path:
            if tool_config.project_context_path.exists():
                status["project_markdown"] = "存在"
            else:
                status["project_markdown"] = "不存在"
        else:
            status["project_markdown"] = "未設定"

        # システムファイルのリンク状態確認
        if tool_type == ToolType.CLAUDE_CODE:
            system_paths = self.claude_md_paths
        elif tool_type == ToolType.GEMINI_CLI:
            system_paths = self.gemini_md_paths
        else:
            return status

        for location, path in system_paths.items():
            if location != "project_root":  # プロジェクトルートは除外
                link_status = self.link_manager.check_link_status(path)
                status[f"system_{location}"] = link_status.value

        return status

    def create_default_markdown(self, tool_type: ToolType, path: Optional[Path] = None) -> Path:
        """デフォルトのマークダウンファイルを作成.

        Args:
            tool_type: ツールタイプ
            path: ファイルパス（None の場合はデフォルト）

        Returns:
            Path: 作成されたファイルパス
        """
        if path is None:
            if tool_type == ToolType.CLAUDE_CODE:
                path = self.claude_md_paths["project_root"]
            elif tool_type == ToolType.GEMINI_CLI:
                path = self.gemini_md_paths["project_root"]
            else:
                raise ValueError(f"サポートされていないツール: {tool_type}")

        # デフォルト内容を作成
        if tool_type == ToolType.CLAUDE_CODE:
            content = self._get_default_claude_md_content()
        elif tool_type == ToolType.GEMINI_CLI:
            content = self._get_default_gemini_md_content()
        else:
            content = f"# {tool_type.value.upper()} Configuration\n\nProject context file.\n"

        # ファイルを作成
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        # プロジェクト設定を更新
        self._update_project_config(tool_type, path)

        return path

    def _update_project_config(self, tool_type: ToolType, context_path: Path) -> None:
        """プロジェクト設定を更新."""
        project_config = self.config_manager.project_config
        tool_config = project_config.tools.get(tool_type.value)

        if tool_config:
            tool_config.project_context_path = context_path
        else:
            # ツール設定が存在しない場合は簡単な設定を作成
            from ..config import ClaudeCodeConfig, GeminiCLIConfig

            if tool_type == ToolType.CLAUDE_CODE:
                tool_config = ClaudeCodeConfig(
                    name=tool_type.value,
                    system_config_path=Path.home() / ".claude" / "settings.json",
                    project_context_path=context_path,
                )
            elif tool_type == ToolType.GEMINI_CLI:
                tool_config = GeminiCLIConfig(
                    name=tool_type.value,
                    system_config_path=Path.home() / ".gemini" / "settings.json",
                    project_context_path=context_path,
                )
            else:
                return

            project_config.tools[tool_type.value] = tool_config

        self.config_manager.save_project_config(project_config)

    def _get_default_claude_md_content(self) -> str:
        """デフォルトのCLAUDE.md内容."""
        return """# Claude Code Project Context

## プロジェクト概要
このプロジェクトについての説明を記載してください。

## 技術スタック
- 使用言語・フレームワーク
- 主要な依存関係

## アーキテクチャ
- プロジェクト構造
- 主要なコンポーネント

## 開発ガイドライン
- コーディング規約
- テスト方針
- デプロイメント手順

## 注意事項
- 重要な制約事項
- セキュリティ考慮事項
"""

    def _get_default_gemini_md_content(self) -> str:
        """デフォルトのGEMINI.md内容."""
        return """# Gemini CLI Project Context

## Project Overview
Describe your project here.

## Technical Stack
- Programming languages & frameworks
- Key dependencies

## Architecture
- Project structure
- Main components

## Development Guidelines
- Coding standards
- Testing approach
- Deployment procedures

## Important Notes
- Key constraints
- Security considerations
"""
