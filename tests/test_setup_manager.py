"""セットアップマネージャーのテスト."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from aicli_config_bridge.setup.manager import LinkSetup
from aicli_config_bridge.setup.models import LinkItem, LinkItemType


@pytest.fixture
def temp_project(monkeypatch: pytest.MonkeyPatch):
    """テンポラリプロジェクト."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        home_path = project_path / "home"
        home_path.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(Path, "home", lambda: home_path)

        config = {
            "version": "0.2.0",
            "description": "テスト用設定",
            "links": [
                {
                    "id": "test-file",
                    "name": "テストファイル",
                    "type": "file",
                    "source": "source.txt",
                    "target": "~/target.txt",
                    "create_if_missing": True,
                    "default_content": "test content",
                }
            ],
        }

        config_file = project_path / "aicli-links.json"
        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

        yield project_path


def test_load_config(temp_project: Path) -> None:
    """設計図の読み込みテスト."""
    setup = LinkSetup(temp_project)
    config = setup.load_config()

    assert config.version == "0.2.0"
    assert len(config.links) == 1
    assert config.links[0].id == "test-file"


def test_resolve_path(temp_project: Path) -> None:
    """パス解決のテスト."""
    setup = LinkSetup(temp_project)

    path = setup._resolve_path("source.txt")
    assert path == temp_project / "source.txt"

    path = setup._resolve_path("~/test.txt")
    assert path == Path.home() / "test.txt"


def test_create_default_file(temp_project: Path) -> None:
    """デフォルトファイル作成のテスト."""
    setup = LinkSetup(temp_project)

    link = LinkItem(
        id="test",
        name="テスト",
        type=LinkItemType.FILE,
        source="source.txt",
        target="~/target.txt",
        create_if_missing=True,
        default_content="test content",
    )

    path = temp_project / "source.txt"
    setup._create_default_file(path, link)

    assert path.exists()
    assert path.read_text(encoding="utf-8") == "test content"


def test_setup_interactive_skip_all(temp_project: Path) -> None:
    """スキップ動作のテスト."""
    setup = LinkSetup(temp_project)

    setup.setup_interactive(skip_all=True)

    source = temp_project / "source.txt"
    assert not source.exists()


def test_setup_interactive_dry_run_creates_nothing(
    temp_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """dry-run では何も作成しない."""
    setup = LinkSetup(temp_project)

    monkeypatch.setattr("aicli_config_bridge.setup.manager.Confirm.ask", lambda *_, **__: True)

    setup.setup_interactive(dry_run=True)

    source = temp_project / "source.txt"
    target = Path.home() / "target.txt"
    assert not source.exists()
    assert not target.exists()
