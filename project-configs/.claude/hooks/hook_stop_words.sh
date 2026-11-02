#!/bin/bash

# Stop words hook for Claude Code
# This script checks for forbidden words in Claude's responses

RULES_FILE="$HOME/.claude/hooks/rules/hook_stop_words_rules.json"

# Check if rules file exists
if [ ! -f "$RULES_FILE" ]; then
    echo "Rules file not found: $RULES_FILE"
    exit 0
fi

# Read input from stdin
INPUT=$(cat)

# Check for forbidden words using jq
# A native Windows jq.exe writes CRLF; `read` keeps the stray \r on
# $pattern, which then stops matching anything. Strip it so this works
# the same on jq.exe (Windows) and jq (WSL/Linux).
jq -r '.rules[] | select(.enabled == true) | .pattern' "$RULES_FILE" | while read -r pattern; do
    pattern="${pattern%$'\r'}"
    if echo "$INPUT" | grep -qi "$pattern"; then
        MESSAGE=$(jq -r ".rules[] | select(.pattern == \"$pattern\") | .message" "$RULES_FILE")
        echo "❌ Forbidden word detected: $MESSAGE"
        exit 1
    fi
done

exit 0