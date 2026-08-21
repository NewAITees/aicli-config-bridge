#!/usr/bin/env bash
# Claude Code status line script
# Converts PS1 from ~/.bashrc: \[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$
# Colors are preserved; trailing "$" is removed per statusline rules.

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# PS1-derived segment: bold green user@host, bold blue cwd
printf '\033[01;32m%s@%s\033[00m:\033[01;34m%s\033[00m' \
    "$(whoami)" "$(hostname -s)" "$cwd"

# Model name
if [ -n "$model" ]; then
    printf ' \033[00;33m[%s]\033[00m' "$model"
fi

# Context usage percentage
if [ -n "$used" ]; then
    printf ' \033[00;36mctx:%.0f%%\033[00m' "$used"
fi
