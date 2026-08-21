#!/bin/bash

# Pre-command hook for Claude Code
# This script checks for forbidden commands before execution

RULES_FILE="$HOME/.claude/hooks/rules/hook_pre_commands_rules.json"

# Check if rules file exists
if [ ! -f "$RULES_FILE" ]; then
    echo "Rules file not found: $RULES_FILE"
    exit 0
fi

# Get the command from arguments
COMMAND="$1"

# Check for forbidden commands using jq
jq -r '.rules[] | select(.enabled == true) | .pattern' "$RULES_FILE" | while read -r pattern; do
    if echo "$COMMAND" | grep -qi "$pattern"; then
        MESSAGE=$(jq -r ".rules[] | select(.pattern == \"$pattern\") | .message" "$RULES_FILE")
        echo "❌ Forbidden command detected: $MESSAGE"
        exit 1
    fi
done

exit 0