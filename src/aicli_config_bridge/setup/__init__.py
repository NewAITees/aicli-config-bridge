"""Setup module."""

from .manager import LinkSetup
from .models import LinkItem, LinkItemType, LinksConfig

__all__ = ["LinkItem", "LinkItemType", "LinkSetup", "LinksConfig"]
