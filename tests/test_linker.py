"""シンボリックリンク管理のテスト."""

import json
import tempfile
from pathlib import Path

import pytest

from aicli_config_bridge.config import ConfigManager, ProjectConfig, ToolType
from aicli_config_bridge.linker import LinkManager


@pytest.fixture
def temp_project() -> Path:
    """テンポラリプロジェクトディレクトリを作成."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def config_manager(temp_project: Path) -> ConfigManager:
    """設定管理マネージャーを作成."""
    return ConfigManager(temp_project)


@pytest.fixture
def link_manager(config_manager: ConfigManager) -> LinkManager:
    """リンク管理マネージャーを作成."""
    return LinkManager(config_manager)


def test_create_link(link_manager: LinkManager, temp_project: Path) -> None:
    """シンボリックリンク作成テスト."""
    # テストファイルを作成
    source_file = temp_project / "source.json"
    source_file.write_text('{"test": "data"}')

    target_file = temp_project / "target.json"

    # リンクを作成
    link_info = link_manager.create_link(source_file, target_file)

    assert link_info.source_path == source_file.resolve()
    assert link_info.target_path == target_file.resolve()
    assert target_file.exists()


def test_create_link_with_backup(link_manager: LinkManager, temp_project: Path) -> None:
    """既存ファイルがある場合のリンク作成テスト."""
    # ソースファイルを作成
    source_file = temp_project / "source.json"
    source_file.write_text('{"new": "data"}')

    # 既存のターゲットファイルを作成
    target_file = temp_project / "target.json"
    target_file.write_text('{"old": "data"}')

    # リンクを作成（バックアップあり）
    link_info = link_manager.create_link(source_file, target_file, backup=True)

    assert target_file.exists()
    # バックアップファイルが作成されているか確認
    backup_dir = target_file.parent / ".aicli-backup"
    assert backup_dir.exists()
    backup_files = list(backup_dir.glob("*.backup_*"))
    assert len(backup_files) > 0


def test_create_link_source_not_exists(link_manager: LinkManager, temp_project: Path) -> None:
    """存在しないソースファイルでのリンク作成テスト."""
    source_file = temp_project / "nonexistent.json"
    target_file = temp_project / "target.json"

    with pytest.raises(FileNotFoundError):
        link_manager.create_link(source_file, target_file)


def test_remove_link(link_manager: LinkManager, temp_project: Path) -> None:
    """リンク削除テスト."""
    # リンクを作成
    source_file = temp_project / "source.json"
    source_file.write_text('{"test": "data"}')
    target_file = temp_project / "target.json"

    link_manager.create_link(source_file, target_file)
    assert target_file.exists()

    # リンクを削除
    result = link_manager.remove_link(target_file, restore_backup=False)
    assert result is True
    assert not target_file.exists()


def test_check_link_status(link_manager: LinkManager, temp_project: Path) -> None:
    """リンク状態チェックテスト."""
    from aicli_config_bridge.config import LinkStatus

    # 存在しないファイル
    nonexistent_file = temp_project / "nonexistent.json"
    status = link_manager.check_link_status(nonexistent_file)
    assert status == LinkStatus.NOT_LINKED

    # 通常ファイル
    normal_file = temp_project / "normal.json"
    normal_file.write_text('{"test": "data"}')
    status = link_manager.check_link_status(normal_file)
    assert status == LinkStatus.LINKED


def test_validate_links(link_manager: LinkManager, temp_project: Path) -> None:
    """リンク検証テスト."""
    # プロジェクト設定にツール設定を追加
    from aicli_config_bridge.config import ClaudeCodeConfig

    source_file = temp_project / "configs" / "claude-settings.json"
    source_file.parent.mkdir(exist_ok=True)
    source_file.write_text('{"theme": "dark"}')

    target_file = temp_project / "system" / "claude-settings.json"

    # ツール設定を作成
    tool_config = ClaudeCodeConfig(
        name="claude-code",
        system_config_path=target_file,
        project_config_path=source_file,
        theme="dark",
    )

    # プロジェクト設定に追加
    project_config = link_manager.config_manager.project_config
    project_config.tools["claude-code"] = tool_config
    link_manager.config_manager.save_project_config(project_config)

    # リンクを作成
    link_manager.create_link(source_file, target_file)

    # 検証実行
    results = link_manager.validate_links()
    assert "claude-code" in results
    assert results["claude-code"] is True
