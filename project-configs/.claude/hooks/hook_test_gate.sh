#!/bin/bash

# Stop hook for Claude Code: gates "done" on tests passing, when the current
# project has a recognizable test command. Silently no-ops when it can't
# tell how to test the project (Anthropic-recommended fallback: gate on lint
# only, or skip, rather than guessing).
#
# Running tests executes the project's own code, so the gate only runs in
# directories listed in the trust file (one directory per line, "#" comments,
# "~" allowed). The file lives outside any repository so a cloned project
# cannot trust itself. Default: ~/.claude/test_gate_trusted_dirs
# It also never installs or resolves dependencies: Python needs an existing
# .venv (uv --frozen --no-sync) and Node needs an existing node_modules.

TRUST_FILE="${CLAUDE_TEST_GATE_TRUST_FILE:-$HOME/.claude/test_gate_trusted_dirs}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT_DIR" || exit 0
PROJECT_REAL=$(pwd -P)

is_trusted() {
    [ -f "$TRUST_FILE" ] || return 1
    local line dir real
    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in
            '' | '#'*) continue ;;
        esac
        dir="${line/#\~/$HOME}"
        real=$(cd "$dir" 2>/dev/null && pwd -P) || continue
        [ "$real" = "$PROJECT_REAL" ] && return 0
    done < "$TRUST_FILE"
    return 1
}

is_trusted || exit 0

LOG=$(mktemp)

if [ -f "pyproject.toml" ] && [ -d ".venv" ] && command -v uv >/dev/null 2>&1; then
    if ! uv run --frozen --no-sync pytest > "$LOG" 2>&1; then
        echo "テストが失敗しています。修正してから完了報告してください。詳細: $LOG" >&2
        exit 2
    fi
elif [ -f "package.json" ] && [ -d "node_modules" ] && command -v npm >/dev/null 2>&1; then
    if ! npm test --silent > "$LOG" 2>&1; then
        echo "テストが失敗しています。修正してから完了報告してください。詳細: $LOG" >&2
        exit 2
    fi
fi

exit 0
