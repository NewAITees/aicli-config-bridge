#!/usr/bin/env python3
"""
Cross-platform configuration link management script for AI CLI tools.

This script manages symbolic links, hard links, or file copies depending on
the environment capabilities and user preferences.
"""

import argparse
import json
import os
import platform
import shutil
import sys
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class LinkType(Enum):
    SYMLINK = "symlink"
    HARDLINK = "hardlink"
    COPY = "copy"


class ConfigSyncer:
    """Manages configuration synchronization across different environments."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).parent.parent
        self.project_configs = self.project_root / "project-configs"
        self.platform = platform.system().lower()
        self.is_wsl = self._detect_wsl()

    def _detect_wsl(self) -> bool:
        """Detect if running in WSL environment."""
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except (FileNotFoundError, OSError):
            return False

    def _get_supported_link_types(self) -> List[LinkType]:
        """Determine which link types are supported in current environment."""
        supported = []

        # Test symbolic link support
        if self._test_symlink_support():
            supported.append(LinkType.SYMLINK)

        # Test hard link support
        if self._test_hardlink_support():
            supported.append(LinkType.HARDLINK)

        # File copy is always supported
        supported.append(LinkType.COPY)

        return supported

    def _test_symlink_support(self) -> bool:
        """Test if symbolic links are supported."""
        test_file = self.project_configs / "test_symlink_source"
        test_link = self.project_configs / "test_symlink_target"

        try:
            test_file.write_text("test")
            os.symlink(test_file, test_link)
            test_link.unlink()
            test_file.unlink()
            return True
        except (OSError, NotImplementedError):
            # Clean up if partially created
            if test_file.exists():
                test_file.unlink()
            if test_link.exists():
                test_link.unlink()
            return False

    def _test_hardlink_support(self) -> bool:
        """Test if hard links are supported."""
        test_file = self.project_configs / "test_hardlink_source"
        test_link = self.project_configs / "test_hardlink_target"

        try:
            test_file.write_text("test")
            os.link(test_file, test_link)
            test_link.unlink()
            test_file.unlink()
            return True
        except (OSError, NotImplementedError):
            # Clean up if partially created
            if test_file.exists():
                test_file.unlink()
            if test_link.exists():
                test_link.unlink()
            return False

    def _get_config_mappings(self) -> Dict[str, Dict]:
        """Get configuration file mappings for different tools."""
        home = Path.home()

        mappings = {
            "claude_desktop": {
                "source": self.project_configs / "mcp-servers-config.json",
                "targets": [],
            },
            "claude_code_mcp": {
                "source": self.project_configs / "mcp-servers-config.json",
                "targets": [],
            },
            "claude_code_settings": {
                "source": self.project_configs / "claude-settings-actual.json",
                "targets": [home / ".claude" / "settings.json"],
            },
            "gemini_settings": {
                "source": self.project_configs / "gemini-settings-actual.json",
                "targets": [home / ".gemini" / "settings.json"],
            },
            "context_files": {
                "source": home / "CLAUDE.md",
                "targets": [self.project_configs / "CLAUDE.md"],
            },
        }

        # Platform-specific Claude Desktop paths
        if self.platform == "darwin":  # macOS
            mappings["claude_desktop"]["targets"].append(
                home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
            )
        elif self.platform == "windows":
            mappings["claude_desktop"]["targets"].append(
                Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
            )
        elif self.platform == "linux" or self.is_wsl:
            mappings["claude_desktop"]["targets"].append(
                home / ".config" / "Claude" / "claude_desktop_config.json"
            )

        return mappings

    def _create_default_source(self, source: Path, config_name: str) -> bool:
        """Create a default source file if it doesn't exist."""
        try:
            # Ensure source directory exists
            source.parent.mkdir(parents=True, exist_ok=True)

            # Get default content based on config type
            default_content = self._get_default_content(config_name)

            if default_content is not None:
                source.write_text(default_content)
                print(f"Created default source file: {source}")
                return True
            else:
                # Just create an empty file for unknown config types
                source.touch()
                print(f"Created empty source file: {source}")
                return True

        except Exception as e:
            print(f"Failed to create default source file {source}: {e}")
            return False

    def _get_default_content(self, config_name: str) -> str | None:
        """Get default content for different configuration types."""
        defaults = {
            "claude_desktop": """{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${HOME}/Documents",
        "${HOME}/Desktop"
      ]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}""",
            "claude_code_mcp": """{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${HOME}/Documents",
        "${HOME}/Desktop"
      ]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}""",
            "claude_code_settings": """{
  "model": "sonnet",
  "env": {
    "BASH_DEFAULT_TIMEOUT_MS": "900000"
  },
  "hooks": {},
  "permissions": {
    "allow": [],
    "deny": []
  },
  "mcpServers": {}
}""",
            "gemini_settings": """{
  "theme": "auto",
  "selectedAuthType": "oauth-personal"
}""",
            "context_files": """# AI運用ガイドライン・開発規約

このファイルは Claude Code がこのプロジェクトで作業する際のガイダンスを提供します。

## プロジェクト概要

[プロジェクトの概要を記述してください]

## 開発ガイドライン

[開発時の注意事項やルールを記述してください]
""",
        }

        return defaults.get(config_name)

    def _create_link(self, source: Path, target: Path, link_type: LinkType) -> bool:
        """Create a link of the specified type."""
        try:
            # Ensure target directory exists
            target.parent.mkdir(parents=True, exist_ok=True)

            # Remove existing target if it exists
            if target.exists() or target.is_symlink():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()

            if link_type == LinkType.SYMLINK:
                os.symlink(source, target)
            elif link_type == LinkType.HARDLINK:
                os.link(source, target)
            elif link_type == LinkType.COPY:
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)

            return True
        except Exception as e:
            print(f"Failed to create {link_type.value} from {source} to {target}: {e}")
            return False

    def sync_configurations(
        self, preferred_link_type: LinkType | None = None, dry_run: bool = False
    ) -> Dict:
        """Synchronize all configuration files."""
        supported_types = self._get_supported_link_types()

        if preferred_link_type and preferred_link_type not in supported_types:
            print(
                f"Warning: {preferred_link_type.value} not supported, "
                f"falling back to {supported_types[0].value}"
            )
            link_type = supported_types[0]
        else:
            link_type = preferred_link_type or supported_types[0]

        print(f"Using {link_type.value} for configuration synchronization")

        mappings = self._get_config_mappings()
        results = {}

        for config_name, config_info in mappings.items():
            source = Path(config_info["source"])
            targets = config_info["targets"]

            results[config_name] = {"success": [], "failed": []}

            if not source.exists():
                print(f"Source file {source} does not exist, creating default...")
                if not self._create_default_source(source, config_name):
                    print(f"Failed to create default source file, skipping {config_name}")
                    continue

            for target in targets:
                target = Path(target)
                print(f"{'[DRY RUN] ' if dry_run else ''}Linking {source} -> {target}")

                if not dry_run:
                    if self._create_link(source, target, link_type):
                        results[config_name]["success"].append(str(target))
                    else:
                        results[config_name]["failed"].append(str(target))
                else:
                    results[config_name]["success"].append(str(target))

        return results

    def status(self) -> Dict:
        """Check the status of all configuration links."""
        mappings = self._get_config_mappings()
        status_info = {}

        for config_name, config_info in mappings.items():
            source = Path(config_info["source"])
            targets = config_info["targets"]

            status_info[config_name] = {"source_exists": source.exists(), "targets": {}}

            for target in targets:
                target = Path(target)
                target_status = {
                    "exists": target.exists(),
                    "is_symlink": target.is_symlink(),
                    "is_hardlink": False,
                    "points_to_correct_source": False,
                }

                if target.exists():
                    # Check if it's a hard link
                    try:
                        target_status["is_hardlink"] = (
                            source.exists()
                            and target.stat().st_ino == source.stat().st_ino
                            and target.stat().st_dev == source.stat().st_dev
                        )
                    except (OSError, IOError):
                        pass

                    # Check if it points to correct source
                    if target.is_symlink():
                        try:
                            target_status["points_to_correct_source"] = (
                                target.resolve() == source.resolve()
                            )
                        except (OSError, IOError):
                            pass
                    elif target_status["is_hardlink"]:
                        target_status["points_to_correct_source"] = True

                status_info[config_name]["targets"][str(target)] = target_status

        return status_info


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync AI CLI configuration files")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without actually doing it"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show current status of configuration links"
    )
    parser.add_argument(
        "--link-type", choices=["symlink", "hardlink", "copy"], help="Preferred link type"
    )
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    syncer = ConfigSyncer(args.project_root)

    if args.status:
        status = syncer.status()
        print(json.dumps(status, indent=2))
        return

    link_type = LinkType(args.link_type) if args.link_type else None
    results = syncer.sync_configurations(link_type, args.dry_run)

    print("\nSynchronization Results:")
    for config_name, result in results.items():
        print(f"\n{config_name}:")
        if result["success"]:
            print(f"  ✅ Success: {len(result['success'])} targets")
            for target in result["success"]:
                print(f"    - {target}")
        if result["failed"]:
            print(f"  ❌ Failed: {len(result['failed'])} targets")
            for target in result["failed"]:
                print(f"    - {target}")


if __name__ == "__main__":
    main()
