# aicli-config-bridge

A streamlined configuration management tool for AI CLI applications, enabling centralized and version-controlled configuration management through symbolic linking.

## Overview

`aicli-config-bridge` addresses the common challenge of managing AI CLI tool configurations that are typically scattered across system-specific locations. This tool allows developers to maintain all AI CLI configurations within a single project directory, making them easily portable, version-controllable, and shareable across development environments. Current releases focus on symlink-based management for macOS/Linux/WSL, with Windows native support handled as file copy when symlinks are unavailable.

## Features

- **Centralized Configuration Management**: Manage all AI CLI tool configurations from a single project directory
- **Symbolic Link Automation**: Automatically creates and manages symbolic links between project configurations and system locations (or file copy on Windows native)
- **Cross-Platform Compatibility**: Works on macOS, Linux, and Windows (WSL); Windows native uses copy in place of symlink
- **Backup and Restore**: Safely backup existing configurations before linking
- **Validation**: Verify configuration integrity and link status
- **Context File Management**: Import and link `CLAUDE.md` / `GEMINI.md` context files

## Supported AI CLI Tools

### Claude Code
- **Configuration Location**: `~/.claude/settings.json`, `~/.claude/settings.local.json`
- **Project Settings**: `configs/claude-code/settings.json`, `configs/claude-code/settings.local.json`
- **MCP Servers**: Model Context Protocol server configurations

### Gemini CLI
- **User Settings**: `~/.gemini/settings.json`
- **Project Settings**: `configs/gemini-cli/settings.json`
- **Context Files**: `GEMINI.md` project context files

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
├── aicli-links.json
├── configs/
│   ├── claude-code/
│   │   ├── settings.json
│   │   └── settings.local.json
│   ├── gemini-cli/
│   │   └── settings.json
├── backups/
├── aicli-config.json
├── CLAUDE.md
└── GEMINI.md
```

## Configuration Examples

### Claude Code Configuration

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  },
  "allowedTools": ["read", "write", "shell"],
  "theme": "dark"
}
```

### Gemini CLI Configuration

```json
{
  "theme": "Atom One",
  "autoAccept": false,
  "checkpointing": {
    "enabled": true
  },
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

## Commands Reference

```bash
# Initialize a new project and create aicli-links.json
aicli-config-bridge init [project-name]

# Run interactive setup based on aicli-links.json
aicli-config-bridge setup
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
