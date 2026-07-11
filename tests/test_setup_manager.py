"""セットアップマネージャーのテスト."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from aicli_config_bridge.setup.manager import LinkSetup, _detect_platform
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


def test_detect_platform_windows() -> None:
    with patch("sys.platform", "win32"):
        assert _detect_platform() == "windows"


def test_detect_platform_darwin() -> None:
    with patch("sys.platform", "darwin"):
        assert _detect_platform() == "darwin"


def test_detect_platform_wsl(tmp_path: Path) -> None:
    proc = tmp_path / "version"
    proc.write_text("Linux version 5.15 microsoft-standard-WSL2", encoding="utf-8")
    with (
        patch("sys.platform", "linux"),
        patch(
            "aicli_config_bridge.setup.manager.Path",
            side_effect=lambda p: proc if str(p) == "/proc/version" else Path(p),
        ),
    ):
        assert _detect_platform() == "wsl"


def test_detect_platform_linux() -> None:
    with patch("sys.platform", "linux"), patch("pathlib.Path.read_text", side_effect=OSError):
        assert _detect_platform() == "linux"


def test_get_target_str_uses_target_windows_on_windows(temp_project: Path) -> None:
    setup = LinkSetup(temp_project)
    link = LinkItem(
        id="t",
        name="test",
        type=LinkItemType.FILE,
        source="src.txt",
        target="~/.config/file",
        target_windows="%USERPROFILE%\\.config\\file",
    )
    with patch("aicli_config_bridge.setup.manager._detect_platform", return_value="windows"):
        assert setup._get_target_str(link) == "%USERPROFILE%\\.config\\file"


def test_get_target_str_uses_target_on_linux(temp_project: Path) -> None:
    setup = LinkSetup(temp_project)
    link = LinkItem(
        id="t",
        name="test",
        type=LinkItemType.FILE,
        source="src.txt",
        target="~/.config/file",
        target_windows="%USERPROFILE%\\.config\\file",
    )
    with patch("aicli_config_bridge.setup.manager._detect_platform", return_value="linux"):
        assert setup._get_target_str(link) == "~/.config/file"


def test_resolve_path_userprofile(temp_project: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USERPROFILE", "/tmp/winuser")
    setup = LinkSetup(temp_project)
    result = setup._resolve_path("%USERPROFILE%/.claude/CLAUDE.md")
    assert "/tmp/winuser" in str(result)


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


def test_get_link_status_linked(temp_project: Path) -> None:
    """リンク状態の判定."""
    setup = LinkSetup(temp_project)
    source = temp_project / "source.txt"
    source.write_text("x", encoding="utf-8")
    target = Path.home() / "target.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(source)

    link = setup.list_links()[0]
    status = setup.get_link_status(link)

    assert status["status"] == "linked"


def test_apply_links_creates_link(temp_project: Path) -> None:
    """apply_links がリンクを作成する."""
    setup = LinkSetup(temp_project)
    source = temp_project / "source.txt"
    source.write_text("x", encoding="utf-8")

    result = setup.apply_links()

    target = Path.home() / "target.txt"
    assert target.is_symlink()
    assert "test-file" in result["linked"]


def test_apply_links_dry_run_creates_nothing(temp_project: Path) -> None:
    """dry-run では何も作成しない."""
    setup = LinkSetup(temp_project)
    source = temp_project / "source.txt"
    source.write_text("x", encoding="utf-8")

    setup.apply_links(dry_run=True)

    target = Path.home() / "target.txt"
    assert not target.exists()


def test_apply_links_skip_on_conflict(temp_project: Path) -> None:
    """on_conflict=skip では既存ファイルをスキップ."""
    setup = LinkSetup(temp_project)
    source = temp_project / "source.txt"
    source.write_text("x", encoding="utf-8")
    target = Path.home() / "target.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("existing", encoding="utf-8")

    result = setup.apply_links(conflict_strategy="skip")

    assert "test-file" in result["skipped"]
    assert target.read_text(encoding="utf-8") == "existing"


def test_apply_links_already_linked_is_skipped(temp_project: Path) -> None:
    """既にリンク済みの場合はスキップ."""
    setup = LinkSetup(temp_project)
    source = temp_project / "source.txt"
    source.write_text("x", encoding="utf-8")
    target = Path.home() / "target.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(source)

    result = setup.apply_links()

    assert "test-file" in result["skipped"]


def test_apply_links_filter_by_id(temp_project: Path) -> None:
    """IDフィルタで対象を絞れる."""
    setup = LinkSetup(temp_project)
    source = temp_project / "source.txt"
    source.write_text("x", encoding="utf-8")

    result = setup.apply_links(ids=["unknown-id"])

    assert result["linked"] == []


def test_unlink_links_removes_symlink(temp_project: Path) -> None:
    """リンク解除がシンボリックリンクを削除."""
    setup = LinkSetup(temp_project)
    source = temp_project / "source.txt"
    source.write_text("x", encoding="utf-8")
    target = Path.home() / "target.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(source)

    result = setup.unlink_links(["test-file"], dry_run=False)

    assert "test-file" in result["removed"]
    assert not target.exists()


def test_unlink_links_does_not_remove_wrong_symlink(temp_project: Path) -> None:
    """管理対象外のシンボリックリンクを削除しない."""
    setup = LinkSetup(temp_project)
    target = Path.home() / "target.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    unrelated = temp_project / "unrelated.txt"
    unrelated.write_text("keep", encoding="utf-8")
    target.symlink_to(unrelated)

    result = setup.unlink_links(["test-file"], dry_run=False)

    assert "test-file" in result["skipped"]
    assert target.is_symlink()


def test_apply_links_rejects_unknown_conflict_strategy(temp_project: Path) -> None:
    """不明な競合戦略を受け付けない."""
    setup = LinkSetup(temp_project)

    with pytest.raises(ValueError, match="競合戦略"):
        setup.apply_links(conflict_strategy="unknown")
