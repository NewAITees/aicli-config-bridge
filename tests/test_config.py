"""設定管理モジュールのテスト."""

import json
import tempfile
from pathlib import Path

import pytest

from aicli_config_bridge.config import (
    ConfigManager,
    ProjectConfig,
    ToolType,
)


def test_config_manager_init() -> None:
    """ConfigManager の初期化テスト."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = ConfigManager(Path(temp_dir))
        assert manager.project_root == Path(temp_dir)
        assert manager.config_file == Path(temp_dir) / "aicli-config.json"


def test_load_project_config_default() -> None:
    """デフォルトプロジェクト設定のロードテスト."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        manager = ConfigManager(temp_path)

        config = manager.load_project_config()

        assert config.name == temp_path.name
        assert config.root_path == temp_path
        assert config.version == "0.1.0"
        assert len(config.tools) == 0


def test_save_and_load_project_config() -> None:
    """プロジェクト設定の保存・ロードテスト."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        manager = ConfigManager(temp_path)

        # 設定を作成・保存
        config = ProjectConfig(
            name="test-project",
            root_path=temp_path,
            description="テストプロジェクト",
        )
        manager.save_project_config(config)

        # ファイルが作成されているか確認
        assert manager.config_file.exists()

        # 新しいマネージャーでロード
        manager2 = ConfigManager(temp_path)
        loaded_config = manager2.load_project_config()

        assert loaded_config.name == "test-project"
        assert loaded_config.description == "テストプロジェクト"
        assert loaded_config.root_path == temp_path


def test_detect_tool_configs() -> None:
    """ツール設定検出テスト."""
    manager = ConfigManager()
    detected = manager.detect_tool_configs()

    # 戻り値の形式確認
    assert isinstance(detected, dict)
    assert ToolType.CLAUDE_CODE in detected
    assert ToolType.GEMINI_CLI in detected

    # 値は Path または None
    for tool_type, path in detected.items():
        assert path is None or isinstance(path, Path)


def test_env_var_substitution() -> None:
    """環境変数置換テスト."""
    import os

    # テスト用環境変数を設定
    os.environ["TEST_VAR"] = "test_value"
    os.environ["ANOTHER_VAR"] = "another_value"

    manager = ConfigManager()

    # 置換テスト
    test_data = {
        "simple": "${TEST_VAR}",
        "with_default": "${MISSING_VAR:-default_value}",
        "nested": {
            "value": "${ANOTHER_VAR}",
            "list": ["${TEST_VAR}", "static_value"],
        },
        "no_substitution": "normal_string",
    }

    result = manager.substitute_env_vars(test_data)

    assert result["simple"] == "test_value"
    assert result["with_default"] == "default_value"
    assert result["nested"]["value"] == "another_value"
    assert result["nested"]["list"][0] == "test_value"
    assert result["nested"]["list"][1] == "static_value"
    assert result["no_substitution"] == "normal_string"

    # 環境変数をクリーンアップ
    del os.environ["TEST_VAR"]
    del os.environ["ANOTHER_VAR"]
