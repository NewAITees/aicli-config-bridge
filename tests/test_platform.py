"""プラットフォーム判定ユーティリティのテスト."""

from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from aicli_config_bridge.utils import platform as platform_utils
from aicli_config_bridge.utils.platform import PlatformInfo, get_config_directory, get_platform_info


class _FakeFile:
    """open() 互換の簡易ファイルオブジェクト."""

    def __init__(self, text: str) -> None:
        self._text = text

    def read(self) -> str:
        return self._text

    def __enter__(self) -> "_FakeFile":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        return None


def test_is_wsl_false_on_non_posix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform_utils.os, "name", "nt", raising=False)
    assert platform_utils.is_wsl() is False


def test_is_wsl_true_on_proc_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform_utils.os, "name", "posix", raising=False)

    def fake_open(path: str, *_args: object, **_kwargs: object) -> _FakeFile:
        assert path == "/proc/version"
        return _FakeFile("Linux version 5.10.0 microsoft")

    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(Path, "exists", lambda self: False)

    assert platform_utils.is_wsl() is True


def test_is_wsl_true_on_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform_utils.os, "name", "posix", raising=False)

    def fake_open(*_args: object, **_kwargs: object) -> _FakeFile:
        raise FileNotFoundError

    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    monkeypatch.setattr(Path, "exists", lambda self: False)

    assert platform_utils.is_wsl() is True


def test_is_wsl_true_on_mnt_c(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform_utils.os, "name", "posix", raising=False)

    def fake_open(*_args: object, **_kwargs: object) -> _FakeFile:
        raise FileNotFoundError

    def fake_exists(self: Path) -> bool:
        return str(self) == "/mnt/c"

    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(Path, "exists", fake_exists)

    assert platform_utils.is_wsl() is True


def test_get_platform_info_windows_native(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform_utils.platform, "system", lambda: "Windows")
    monkeypatch.setattr(platform_utils, "is_wsl", lambda: False)

    info = get_platform_info()

    assert info.os_name == "Windows"
    assert info.is_wsl is False
    assert info.supports_symlinks is False


def test_get_platform_info_unix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform_utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(platform_utils, "is_wsl", lambda: False)

    info = get_platform_info()

    assert info.os_name == "Linux"
    assert info.is_wsl is False
    assert info.supports_symlinks is True


def test_get_config_directory_windows_appdata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    platform_info = PlatformInfo(
        os_name="Windows",
        is_wsl=False,
        supports_symlinks=False,
        home_path=tmp_path,
    )
    monkeypatch.setattr(platform_utils, "get_platform_info", lambda: platform_info)
    monkeypatch.setenv("APPDATA", "C:/Users/Test/AppData/Roaming")

    result = get_config_directory("myapp")

    assert result == Path("C:/Users/Test/AppData/Roaming") / "myapp"


def test_get_config_directory_unix(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    platform_info = PlatformInfo(
        os_name="Linux",
        is_wsl=False,
        supports_symlinks=True,
        home_path=tmp_path,
    )
    monkeypatch.setattr(platform_utils, "get_platform_info", lambda: platform_info)

    result = get_config_directory("myapp")

    assert result == tmp_path / ".myapp"
