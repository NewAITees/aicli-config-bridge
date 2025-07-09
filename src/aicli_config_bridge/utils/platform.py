"""
プラットフォーム判定とWSL検出のユーティリティ

このモジュールは以下の機能を提供します：
- OS種別の判定 (Windows, Linux, macOS)
- WSL環境の検出
- プラットフォーム固有の処理の分岐

Usage:
    from aicli_config_bridge.utils.platform import is_wsl, get_platform_info
    
    if is_wsl():
        print("WSL環境で実行中")
    
    info = get_platform_info()
    print(f"Platform: {info.os_name}, WSL: {info.is_wsl}")
"""

import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PlatformInfo:
    """プラットフォーム情報."""

    os_name: str  # 'Windows', 'Linux', 'Darwin'
    is_wsl: bool  # WSL環境かどうか
    supports_symlinks: bool  # シンボリックリンクサポート
    home_path: Path  # ホームディレクトリ


def is_wsl() -> bool:
    """WSL環境で実行しているかを判定.
    
    Returns:
        bool: WSL環境の場合True
    """
    if os.name != "posix":
        return False

    # WSL環境の検出方法
    # 1. /proc/version に Microsoft が含まれる
    try:
        with open("/proc/version", "r") as f:
            version_info = f.read().lower()
            if "microsoft" in version_info:
                return True
    except (FileNotFoundError, PermissionError):
        pass

    # 2. 環境変数WSLの存在
    if os.environ.get("WSL_DISTRO_NAME"):
        return True

    # 3. /mnt/c の存在 (Windows Cドライブのマウント)
    if Path("/mnt/c").exists():
        return True

    return False


def get_platform_info() -> PlatformInfo:
    """プラットフォーム情報を取得.
    
    Returns:
        PlatformInfo: プラットフォーム情報
    """
    os_name = platform.system()
    is_wsl_env = is_wsl()

    # シンボリックリンクサポートの判定
    supports_symlinks = True
    if os_name == "Windows" and not is_wsl_env:
        # Windows ネイティブでは管理者権限が必要な場合がある
        supports_symlinks = False

    # ホームディレクトリの取得
    home_path = Path.home()

    return PlatformInfo(
        os_name=os_name,
        is_wsl=is_wsl_env,
        supports_symlinks=supports_symlinks,
        home_path=home_path,
    )


def get_config_directory(app_name: str) -> Path:
    """アプリケーション設定ディレクトリを取得.
    
    Args:
        app_name: アプリケーション名
    
    Returns:
        Path: 設定ディレクトリパス
    """
    platform_info = get_platform_info()

    if platform_info.os_name == "Windows" and not platform_info.is_wsl:
        # Windows ネイティブ
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / app_name
        return platform_info.home_path / "AppData" / "Roaming" / app_name
    else:
        # Unix系 (Linux, macOS, WSL)
        return platform_info.home_path / f".{app_name}"
