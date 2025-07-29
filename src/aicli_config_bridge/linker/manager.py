"""
シンボリックリンク管理マネージャー

このモジュールは以下の機能を提供します：
- シンボリックリンクの作成・削除
- バックアップ機能
- リンク状態の監視・検証
- クロスプラットフォーム対応 (Windows, Linux, macOS, WSL)

Usage:
    from aicli_config_bridge.linker import LinkManager
    from aicli_config_bridge.config import ConfigManager

    config_manager = ConfigManager()
    link_manager = LinkManager(config_manager)

    # シンボリックリンクを作成
    link_info = link_manager.create_link(source_path, target_path)

    # リンクを削除
    link_manager.remove_link(target_path)
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..config import ConfigManager, LinkInfo, LinkStatus, ToolType
from ..utils.platform import get_platform_info


class LinkManager:
    """シンボリックリンク管理マネージャー."""

    def __init__(self, config_manager: ConfigManager) -> None:
        """初期化.

        Args:
            config_manager: 設定管理マネージャー
        """
        self.config_manager = config_manager

    def create_link(
        self,
        source_path: Path,
        target_path: Path,
        backup: bool = True,
    ) -> LinkInfo:
        """シンボリックリンクを作成.

        Args:
            source_path: リンク元パス
            target_path: リンク先パス
            backup: 既存ファイルをバックアップするか

        Returns:
            LinkInfo: リンク情報

        Raises:
            FileNotFoundError: リンク元ファイルが存在しない
            FileExistsError: リンク先に既存ファイルが存在し、バックアップが無効
        """
        if not source_path.exists():
            raise FileNotFoundError(f"リンク元ファイルが存在しません: {source_path}")

        # ターゲットディレクトリを作成
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # 既存ファイルの処理
        if target_path.exists():
            if backup:
                self._backup_file(target_path)
                target_path.unlink()  # バックアップ後に元ファイルを削除
            else:
                raise FileExistsError(f"リンク先ファイルが既に存在します: {target_path}")

        # シンボリックリンクを作成
        try:
            platform_info = get_platform_info()

            if platform_info.supports_symlinks:
                # Unix系 (Linux, macOS, WSL) - シンボリックリンクを使用
                os.symlink(source_path, target_path)
            else:
                # Windows ネイティブ - 管理者権限が必要な場合があるため、コピーを使用
                shutil.copy2(source_path, target_path)

            link_info = LinkInfo(
                source_path=source_path,
                target_path=target_path,
                status=LinkStatus.LINKED,
                created_at=datetime.now().isoformat(),
            )

            return link_info

        except OSError as e:
            raise OSError(f"シンボリックリンクの作成に失敗しました: {e}") from e

    def remove_link(self, target_path: Path, restore_backup: bool = True) -> bool:
        """シンボリックリンクを削除.

        Args:
            target_path: リンク先パス
            restore_backup: バックアップを復元するか

        Returns:
            bool: 削除成功フラグ
        """
        if not target_path.exists():
            return False

        try:
            # リンクまたはファイルを削除
            if target_path.is_symlink():
                target_path.unlink()
            else:
                target_path.unlink()

            # バックアップを復元
            if restore_backup:
                backup_path = self._get_backup_path(target_path)
                if backup_path.exists():
                    shutil.move(str(backup_path), str(target_path))

            return True

        except OSError:
            return False

    def check_link_status(self, target_path: Path) -> LinkStatus:
        """リンク状態をチェック.

        Args:
            target_path: リンク先パス

        Returns:
            LinkStatus: リンク状態
        """
        if not target_path.exists():
            return LinkStatus.NOT_LINKED

        if target_path.is_symlink():
            # シンボリックリンクの場合、リンク先を確認
            try:
                resolved = target_path.resolve()
                if resolved.exists():
                    return LinkStatus.LINKED
                else:
                    return LinkStatus.BROKEN
            except OSError:
                return LinkStatus.BROKEN
        else:
            # 通常ファイルの場合（Windows でのコピー）
            return LinkStatus.LINKED

    def get_all_links(self) -> Dict[str, LinkInfo]:
        """すべてのリンク情報を取得.

        Returns:
            Dict[str, LinkInfo]: リンク情報の辞書
        """
        project_config = self.config_manager.project_config
        links = {}

        for tool_name, tool_config in project_config.tools.items():
            if tool_config.project_config_path and tool_config.system_config_path:
                status = self.check_link_status(tool_config.system_config_path)
                link_info = LinkInfo(
                    source_path=tool_config.project_config_path,
                    target_path=tool_config.system_config_path,
                    status=status,
                )
                links[tool_name] = link_info

        return links

    def repair_broken_links(self) -> List[str]:
        """壊れたリンクを修復.

        Returns:
            List[str]: 修復されたツール名のリスト
        """
        repaired = []
        links = self.get_all_links()

        for tool_name, link_info in links.items():
            if link_info.status == LinkStatus.BROKEN:
                try:
                    self.create_link(
                        link_info.source_path,
                        link_info.target_path,
                        backup=True,
                    )
                    repaired.append(tool_name)
                except (FileNotFoundError, OSError):
                    # 修復に失敗した場合はスキップ
                    continue

        return repaired

    def validate_links(self) -> Dict[str, bool]:
        """すべてのリンクを検証.

        Returns:
            Dict[str, bool]: ツール名と検証結果の辞書
        """
        results = {}
        links = self.get_all_links()

        for tool_name, link_info in links.items():
            # リンク状態チェック
            status_ok = link_info.status == LinkStatus.LINKED

            # ファイル内容チェック（可能な場合）
            content_ok = True
            if status_ok and link_info.source_path.exists():
                try:
                    # 簡単なファイルサイズ比較
                    if link_info.target_path.exists():
                        content_ok = (
                            link_info.source_path.stat().st_size
                            == link_info.target_path.stat().st_size
                        )
                except OSError:
                    content_ok = False

            results[tool_name] = status_ok and content_ok

        return results

    def _backup_file(self, file_path: Path) -> Path:
        """ファイルをバックアップ.

        Args:
            file_path: バックアップするファイルパス

        Returns:
            Path: バックアップファイルパス
        """
        backup_path = self._get_backup_path(file_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file_path, backup_path)
        return backup_path

    def _get_backup_path(self, file_path: Path) -> Path:
        """バックアップファイルパスを取得.

        Args:
            file_path: 元ファイルパス

        Returns:
            Path: バックアップファイルパス
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup_{timestamp}"
        return file_path.parent / ".aicli-backup" / backup_name
