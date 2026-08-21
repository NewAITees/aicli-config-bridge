# aicli-config-bridge

A streamlined configuration management tool for AI CLI applications, enabling centralized and version-controlled configuration management through symbolic linking.

## Overview

`aicli-config-bridge` addresses the common challenge of managing AI CLI tool configurations that are typically scattered across system-specific locations. This tool allows developers to maintain all AI CLI configurations within a single project directory, making them easily portable, version-controllable, and shareable across development environments. Current releases focus on symlink-based management for macOS/Linux/WSL. Windows native paths can be declared per link (`target_windows`), but link creation still requires symlink support (copy-based sync is not implemented).

## Features

- **Centralized Configuration Management**: Manage all AI CLI tool configurations from a single project directory
- **Link Blueprint**: Declare all links in `aicli-links.json` and apply them interactively (`setup`) or non-interactively (`apply`)
- **Cross-Platform Paths**: Works on macOS, Linux, and Windows (WSL); per-link `target_windows` paths for Windows
- **Backup**: Existing target files are backed up to `.aicli-backup/` before linking
- **Status & Repair**: Verify link status (`status --json` for scripts) and repair broken links

## Portable Skills

Custom skills are stored under `project-configs/skills/` and deployed to Codex and Claude as
per-skill symbolic links. System skills, plugin caches, secrets, and runtime history are excluded.

```bash
uv run aicli-config-bridge skills status
uv run aicli-config-bridge skills apply --on-conflict backup
uv run aicli-config-bridge skills import /path/to/my-skill
```

Shared skills live in `project-configs/skills/shared/`. Agent-specific variants live in the
`codex/` and `claude/` directories. Source edits are immediately visible to linked agents on the
same machine. Other machines receive changes after Git synchronization and `skills apply`.

## How It Works

Links are declared in a blueprint file `aicli-links.json` at the project root.
Each entry maps a project-managed source file (e.g. `project-configs/.claude/CLAUDE.md`)
to a system location (e.g. `~/.claude/CLAUDE.md`). The CLI creates and verifies
symbolic links according to this blueprint. Any AI CLI tool whose configuration
lives in files (Claude Code, Gemini CLI, Codex, ...) can be managed this way.

## Installation

### Prerequisites

- Python 3.12 or higher
- Node.js 18+ (for AI CLI tools)
- Git (recommended for version control)

### Install from PyPI

```bash
pip install aicli-config-bridge
```

### Install from Source

```bash
git clone https://github.com/yourusername/aicli-config-bridge.git
cd aicli-config-bridge
pip install -e .
```

## Quick Start

### For New Contributors

```bash
# Install dependencies
uv sync

# Setup symbolic links interactively
uv run aicli-config-bridge setup
```

The setup tool will guide you through creating all necessary links.
See `docs/SETUP_GUIDE.md` for details.

### Initialize a New Configuration Project

```bash
# Create a new configuration project
aicli-config-bridge init my-ai-configs
cd my-ai-configs
```

## Directory Structure

```
my-ai-configs/
├── aicli-links.json            # Link blueprint
└── project-configs/            # Project-managed source files
    └── .claude/
        └── CLAUDE.md
```

Backups of pre-existing target files are stored next to each target in an
`.aicli-backup/` directory.

## Link Blueprint Example (aicli-links.json)

```json
{
  "version": "0.2.0",
  "description": "AI CLI configuration links",
  "links": [
    {
      "id": "claude-global-md",
      "name": "Claude global context (CLAUDE.md)",
      "type": "file",
      "source": "project-configs/.claude/CLAUDE.md",
      "target": "~/.claude/CLAUDE.md",
      "target_windows": "%USERPROFILE%\\.claude\\CLAUDE.md",
      "create_if_missing": false
    }
  ]
}
```

## Commands Reference

```bash
# Initialize a new project and create aicli-links.json
aicli-config-bridge init [project-name]

# Run interactive setup based on aicli-links.json
aicli-config-bridge setup [--dry-run]

# Apply links non-interactively (AI/script friendly)
aicli-config-bridge apply [--dry-run] [--on-conflict backup|overwrite|skip] [--id <link-id>]

# Show link status (add --json for machine-readable output)
aicli-config-bridge status [--json]

# Run without a subcommand for an interactive menu (setup / status / unlink)
aicli-config-bridge
```

## Security Considerations

- **API Keys**: Store sensitive information in environment variables, not in configuration files
- **Backup Security**: Backups may contain sensitive configuration data
- **Link Permissions**: Ensure proper file permissions on linked configurations
- **Version Control**: Use `.gitignore` for sensitive files and local configurations

## Development Setup

```bash
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/
pytest --cov=aicli_config_bridge tests/
```

---

**Note**: This tool manages symbolic links to system configuration files. Always back up existing configurations before using it.
