# aicli-config-bridge

A streamlined configuration management tool for AI CLI applications, enabling centralized and version-controlled configuration management through symbolic linking.

## Overview

`aicli-config-bridge` addresses the common challenge of managing AI CLI tool configurations that are typically scattered across system-specific locations. This tool allows developers to maintain all AI CLI configurations within a single project directory, making them easily portable, version-controllable, and shareable across development environments.

## Features

- **Centralized Configuration Management**: Manage all AI CLI tool configurations from a single project directory
- **Symbolic Link Automation**: Automatically creates and manages symbolic links between project configurations and system locations
- **Multiple Profile Support**: Support for different configuration profiles (development, production, personal, team)
- **Cross-Platform Compatibility**: Works on macOS, Linux, and Windows (WSL)
- **Backup and Restore**: Safely backup existing configurations before linking
- **Validation**: Verify configuration integrity and link status

## Supported AI CLI Tools

### Claude Code
- **Configuration Location**: `~/.claude/settings.json`
- **Project Settings**: `.claude/settings.json`, `.claude/settings.local.json`
- **MCP Servers**: Model Context Protocol server configurations
- **Custom Commands**: `.claude/commands/` directory management

### Gemini CLI
- **User Settings**: `~/.gemini/settings.json`
- **Project Settings**: `.gemini/settings.json`
- **Environment Variables**: `.env` file management
- **Context Files**: `GEMINI.md` project context files

## Installation

### Prerequisites

- Python 3.8 or higher
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

### Initialize a New Configuration Project

```bash
# Create a new configuration project
aicli-config-bridge init my-ai-configs
cd my-ai-configs

# Setup configurations for your tools
aicli-config-bridge detect-configs
aicli-config-bridge link-all
```

### Import Existing Configurations

```bash
# Import existing configurations from system locations
aicli-config-bridge import --tool claude-code
aicli-config-bridge import --tool gemini-cli

# Link configurations to system locations
aicli-config-bridge link --tool claude-code
aicli-config-bridge link --tool gemini-cli
```

## Directory Structure

```
my-ai-configs/
├── configs/
│   ├── claude-code/
│   │   ├── settings.json
│   │   ├── settings.local.json
│   │   └── commands/
│   │       └── custom-command.md
│   ├── gemini-cli/
│   │   ├── settings.json
│   │   ├── .env
│   │   └── GEMINI.md
│   └── profiles/
│       ├── development/
│       ├── production/
│       └── personal/
├── scripts/
│   ├── setup.py
│   ├── validate.py
│   └── backup.py
├── backups/
│   └── [timestamp]/
├── aicli-config.json
└── README.md
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

### Initialization and Setup

```bash
# Initialize new configuration project
aicli-config-bridge init [project-name]

# Detect existing configurations
aicli-config-bridge detect-configs

# Import configurations from system
aicli-config-bridge import --tool [tool-name]
```

### Linking Management

```bash
# Link all configurations
aicli-config-bridge link-all

# Link specific tool
aicli-config-bridge link --tool [tool-name]

# Unlink configurations
aicli-config-bridge unlink --tool [tool-name]

# Check link status
aicli-config-bridge status
```

### Profile Management

```bash
# Create new profile
aicli-config-bridge profile create [profile-name]

# Switch to profile
aicli-config-bridge profile switch [profile-name]

# List available profiles
aicli-config-bridge profile list
```

### Backup and Restore

```bash
# Create backup
aicli-config-bridge backup

# Restore from backup
aicli-config-bridge restore [backup-timestamp]

# List available backups
aicli-config-bridge backup list
```

## Advanced Usage

### Environment Variable Management

The tool supports environment variable substitution in configuration files:

```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Team Configuration Sharing

```bash
# Export configuration for sharing
aicli-config-bridge export --profile team

# Import shared configuration
aicli-config-bridge import --from-file team-config.json
```

### Validation and Health Checks

```bash
# Validate all configurations
aicli-config-bridge validate

# Health check for specific tool
aicli-config-bridge health --tool claude-code
```

## Security Considerations

- **API Keys**: Store sensitive information in environment variables, not in configuration files
- **Backup Security**: Backups may contain sensitive configuration data
- **Link Permissions**: Ensure proper file permissions on linked configurations
- **Version Control**: Use `.gitignore` for sensitive files and local configurations

## Troubleshooting

### Common Issues

**Broken Symbolic Links**
```bash
aicli-config-bridge repair --tool [tool-name]
```

**Permission Errors**
```bash
# Fix file permissions
aicli-config-bridge fix-permissions
```

**Configuration Validation Errors**
```bash
# Validate and show detailed errors
aicli-config-bridge validate --verbose
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/aicli-config-bridge.git
cd aicli-config-bridge
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/
pytest --cov=aicli_config_bridge tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) by Google
- [Model Context Protocol](https://modelcontextprotocol.io/) community

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Note**: This tool manages symbolic links to system configuration files. Always backup your existing configurations before using this too
