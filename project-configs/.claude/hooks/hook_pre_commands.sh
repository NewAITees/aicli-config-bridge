#!/bin/bash

# Pre-command hook for Claude Code (PreToolUse, matcher: Bash)
# Claude Code passes the tool call as JSON on stdin, not as $1.
# Destructive/hard-to-reverse commands trigger an "ask" decision instead of
# a silent allow, so routine work proceeds without confirmation while risky
# operations still stop for a human.

RULES_FILE="$HOME/.claude/hooks/rules/hook_pre_commands_rules.json"

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ] || [ ! -f "$RULES_FILE" ]; then
    exit 0
fi

# Newlines separate commands like ";" does; collapse other whitespace so that
# spacing tricks (tabs, repeated spaces) cannot dodge the patterns.
COMMAND=$(printf '%s' "$COMMAND" | tr '\n' ';' | tr -s '[:space:]' ' ')

MATCHED_MESSAGE=""
while IFS= read -r pattern; do
    # A native Windows jq.exe writes CRLF, which `read` only splits on the
    # trailing \n, leaving a stray \r stuck to $pattern. That \r then
    # becomes a required literal character at the end of the regex, so
    # every rule silently stops matching. Strip it so the hook works the
    # same whether jq.exe (Windows) or jq (WSL/Linux) produced the line.
    pattern="${pattern%$'\r'}"
    if printf '%s' "$COMMAND" | grep -qiE -- "$pattern"; then
        MATCHED_MESSAGE=$(jq -r --arg p "$pattern" '.rules[] | select(.pattern == $p) | .message' "$RULES_FILE")
        MATCHED_MESSAGE="${MATCHED_MESSAGE%$'\r'}"
        break
    fi
done < <(jq -r '.rules[] | select(.enabled == true) | .pattern' "$RULES_FILE")

if [ -n "$MATCHED_MESSAGE" ]; then
    jq -n --arg reason "$MATCHED_MESSAGE" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "ask",
        permissionDecisionReason: $reason
      }
    }'
fi

exit 0
