# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`aicli-config-bridge` is a Python CLI tool that manages AI CLI tool configurations through symbolic linking. It provides centralized configuration management for tools like Claude Code and Gemini CLI, allowing configurations to be version-controlled and shared across development environments.

## Development Environment Setup

This project uses modern Python tooling with `uv` as the package manager.

### Initial Setup Commands

```bash
# Initialize uv project (if not already done)
uv init

# Install dependencies
uv sync

# Install development dependencies
uv add --dev pytest pytest-cov ruff mypy pre-commit

# Install the package in development mode
uv pip install -e .

# Setup pre-commit hooks
pre-commit install
```

### Common Development Commands

```bash
# Run the application
uv run aicli-config-bridge --help

# Run tests
uv run pytest
uv run pytest --cov=aicli_config_bridge --cov-report=term-missing

# Run single test
uv run pytest tests/test_specific_module.py::test_function_name

# Code quality checks
uv run ruff check .
uv run ruff format .
uv run mypy .

# Run all quality checks
uv run pre-commit run --all-files

# Install new package
uv add package-name

# Install new dev package
uv add --dev package-name
```

## Project Structure

The project follows a standard Python CLI application structure:

```
aicli-config-bridge/
├── src/
│   └── aicli_config_bridge/
│       ├── __init__.py
│       ├── cli.py              # Main CLI interface
│       ├── config/             # Configuration management
│       ├── linker/             # Symbolic link management
│       ├── tools/              # Tool-specific handlers
│       └── utils/              # Utility functions
├── tests/                      # Test suite
├── pyproject.toml             # Project configuration
└── README.md                  # Project documentation
```

## Key Architecture Components

### CLI Interface
- Built using Click or Typer for command-line interface
- Commands follow the pattern: `aicli-config-bridge <command> [options]`
- Main commands: init, import, link, unlink, status, validate

### Configuration Management
- Handles reading/writing JSON configuration files
- Supports environment variable substitution
- Manages profile-based configurations (development, production, etc.)

### Symbolic Link Management
- Cross-platform symbolic link creation and management
- Backup existing configurations before linking
- Validation of link integrity and status

### Tool Integration
- Modular design for supporting different AI CLI tools
- Tool-specific handlers for Claude Code and Gemini CLI
- Extensible architecture for adding new tools

## Supported AI CLI Tools

### Claude Code
- Settings: `~/.claude/settings.json`
- Local settings: `.claude/settings.json`, `.claude/settings.local.json`
- Custom commands: `.claude/commands/` directory
- MCP server configurations

### Gemini CLI
- User settings: `~/.gemini/settings.json`
- Project settings: `.gemini/settings.json`
- Environment files: `.env`
- Context files: `GEMINI.md`

## Development Guidelines

### Code Quality
- All code must pass ruff linting and formatting
- Type hints are required for all functions
- Tests are required for all new functionality
- Minimum 85% test coverage

### Testing Strategy
- Unit tests for individual functions and classes
- Integration tests for CLI commands
- Cross-platform compatibility testing
- Mock external dependencies (filesystem, symbolic links)

### Security Considerations
- Never store sensitive information in configuration files
- Use environment variables for API keys and tokens
- Validate all user inputs
- Secure handling of file permissions and symbolic links

## Common Development Tasks

### Adding a New AI CLI Tool
1. Create handler in `src/aicli_config_bridge/tools/`
2. Define configuration schema and locations
3. Implement import/export functionality
4. Add CLI commands for the tool
5. Write comprehensive tests

### Adding New CLI Commands
1. Define command in `src/aicli_config_bridge/cli.py`
2. Implement command logic in appropriate module
3. Add help text and parameter validation
4. Write tests for the command
5. Update documentation

### Environment Variable Substitution
- Use `${VAR_NAME}` syntax in configuration files
- Support default values: `${VAR_NAME:-default}`
- Validate environment variables during configuration loading