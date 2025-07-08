"""基本的なテストファイル."""

import pytest

from aicli_config_bridge import __version__


def test_basic() -> None:
    """基本的なテスト."""
    assert True


def test_import() -> None:
    """インポートテスト."""
    assert __version__ == "0.1.0"


def test_version_type() -> None:
    """バージョンの型テスト."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0
