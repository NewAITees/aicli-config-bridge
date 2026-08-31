#!/bin/bash

# Stop hook for Claude Code: gates "done" on tests passing, when the current
# project has a recognizable test command. Silently no-ops when it can't
# tell how to test the project (Anthropic-recommended fallback: gate on lint
# only, or skip, rather than guessing).

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT_DIR" || exit 0

LOG=$(mktemp)

if [ -f "pyproject.toml" ] && command -v uv >/dev/null 2>&1; then
    if ! uv run pytest > "$LOG" 2>&1; then
        echo "テストが失敗しています。修正してから完了報告してください。詳細: $LOG" >&2
        exit 2
    fi
elif [ -f "package.json" ] && command -v npm >/dev/null 2>&1; then
    if ! npm test --silent > "$LOG" 2>&1; then
        echo "テストが失敗しています。修正してから完了報告してください。詳細: $LOG" >&2
        exit 2
    fi
fi

exit 0
