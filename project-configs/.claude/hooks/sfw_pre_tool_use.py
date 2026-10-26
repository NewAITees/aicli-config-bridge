#!/usr/bin/env python3
"""Deny package-install commands that are not run through sfw (Socket Firewall)."""

from __future__ import annotations

import json
import shlex
import sys

OPERATORS = {"&&", "||", ";", "|", "&", "\n"}
WRAPPERS = {"sudo", "env", "time", "nohup", "command", "exec"}
SHELLS = {"bash", "sh", "zsh"}

# Subcommands that fetch packages. poetry is excluded: sfw's TLS proxy breaks it.
GUARDED: dict[str, set[str]] = {
    "npm": {"install", "i", "add", "ci", "update", "up"},
    "pnpm": {"install", "i", "add", "update", "up"},
    "yarn": {"install", "add", "up", "upgrade"},
    "pip": {"install"},
    "uv": {"add", "sync", "lock"},
    "cargo": {"add", "install"},
    "go": {"get", "install"},
    "gem": {"install"},
    "bundle": {"install"},
}
UV_SECOND_LEVEL: dict[str, set[str]] = {
    "pip": {"install", "sync", "compile"},
    "tool": {"install"},
}


def split_segments(command: str) -> list[list[str]]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    segments: list[list[str]] = [[]]
    for token in lexer:
        if token in OPERATORS:
            segments.append([])
        else:
            segments[-1].append(token)
    return [segment for segment in segments if segment]


def strip_prefix(tokens: list[str]) -> list[str]:
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in WRAPPERS or (
            "=" in token and not token.startswith("-") and token.split("=")[0].isidentifier()
        ):
            index += 1
            continue
        break
    return tokens[index:]


def is_unguarded_install(tokens: list[str]) -> bool:
    tokens = strip_prefix(tokens)
    if not tokens:
        return False
    name = tokens[0].rsplit("/", 1)[-1]
    if name == "sfw":
        return False
    if name in SHELLS and "-c" in tokens[1:-1]:
        return any(
            is_unguarded_install(segment)
            for segment in split_segments(tokens[tokens.index("-c") + 1])
        )
    if name.startswith("python") and tokens[1:3] == ["-m", "pip"]:
        name, tokens = "pip", ["pip", *tokens[3:]]
    rest = [token for token in tokens[1:] if not token.startswith("-")]
    if name not in GUARDED or not rest:
        return False
    if name == "uv" and rest[0] in UV_SECOND_LEVEL:
        return len(rest) > 1 and rest[1] in UV_SECOND_LEVEL[rest[0]]
    return rest[0] in GUARDED[name]


def find_unguarded(command: str) -> bool:
    try:
        return any(is_unguarded_install(segment) for segment in split_segments(command))
    except ValueError:
        return False


def main() -> int:
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool_input = hook_input.get("tool_input") if isinstance(hook_input, dict) else None
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not find_unguarded(command):
        return 0

    reason = (
        "パッケージの取得・更新は sfw 経由で実行してください。"
        "例: `sfw npm install pkg@1.2.3` / `sfw uv add pkg==1.2.3`。"
        "バージョンは exact 固定にしてください。"
    )
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    sys.stdout.write(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
