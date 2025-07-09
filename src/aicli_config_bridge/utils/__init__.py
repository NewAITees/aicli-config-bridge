"""
ユーティリティモジュール

このパッケージは以下のユーティリティを提供します：
- platform: プラットフォーム判定とWSL検出
"""

from .platform import PlatformInfo, get_platform_info, is_wsl

__all__ = ["PlatformInfo", "get_platform_info", "is_wsl"]
