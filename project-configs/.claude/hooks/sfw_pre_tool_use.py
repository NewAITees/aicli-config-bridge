#!/usr/bin/env python3
"""Deny package-install commands that are not run through sfw (Socket Firewall)."""

from __future__ import annotations

import json
import re
import shlex
import sys

PUNCTUATION = set("();<>|&")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
SHELL_C_FLAGS = re.compile(r"^-[A-Za-z]*c[A-Za-z]*$")
PIP_NAME = re.compile(r"^pip\d*(\.\d+)?$")
PYTHON_NAME = re.compile(r"^python[\d.]*$")
TRUSTED_SFW = {"sfw", "/opt/homebrew/bin/sfw", "/usr/local/bin/sfw"}

# Wrapper commands and the options of each that consume the following token.
WRAPPERS: dict[str, set[str]] = {
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-R", "-T", "-U", "-r", "-t"},
    "env": {"-u", "-C", "-S"},
    "xargs": {"-I", "-n", "-P", "-L", "-s", "-d", "-E", "-a", "-J"},
    "nice": {"-n"},
    "exec": {"-a"},
    "time": set(),
    "nohup": set(),
    "command": set(),
    "timeout": {"-s", "-k"},
}

# Subcommands that fetch packages. poetry is excluded: sfw's TLS proxy breaks it.
GUARDED: dict[str, set[str]] = {
    "npm": {"install", "i", "add", "ci", "update", "up"},
    "pnpm": {"install", "i", "add", "update", "up"},
    "yarn": {"install", "add", "up", "upgrade"},
    "pip": {"install"},
    "cargo": {"add", "install"},
    "go": {"get", "install"},
    "gem": {"install"},
    "bundle": {"install"},
}
UV_DIRECT = {"add", "sync", "lock"}
UV_NESTED = {"pip": {"install", "sync", "compile"}, "tool": {"install"}}
NON_FETCHING_FIRST = {"run", "test", "exec", "list", "ls", "view", "show", "info", "outdated"}
SUBCOMMAND_WINDOW = 3

SUBSTITUTION = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
FALLBACK = re.compile(
    r"\b(npm|pnpm|yarn|pip\d*|uv|cargo|go|gem|bundle)\b[^\n;&|]*?"
    r"\b(install|add|ci|update|up|upgrade|get|sync|lock|compile)\b"
)


def split_segments(command: str) -> list[list[str]]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    segments: list[list[str]] = [[]]
    for token in lexer:
        if token and set(token) <= PUNCTUATION:
            segments.append([])
        else:
            segments[-1].append(token)
    return [segment for segment in segments if segment]


def strip_prefix(tokens: list[str]) -> list[str]:
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if "=" in token and not token.startswith("-") and token.split("=")[0].isidentifier():
            index += 1
        elif token in WRAPPERS:
            takes_value = WRAPPERS[token]
            index += 1
            while index < len(tokens) and tokens[index].startswith("-"):
                index += 2 if tokens[index] in takes_value else 1
            if token == "timeout":
                index += 1
        else:
            break
    return tokens[index:]


def uv_fetches(rest: list[str]) -> bool:
    for position, token in enumerate(rest[:SUBCOMMAND_WINDOW]):
        if token == "run":
            return False
        if token in UV_DIRECT:
            return True
        if token in UV_NESTED:
            window = rest[position + 1 : position + 1 + SUBCOMMAND_WINDOW]
            return any(item in UV_NESTED[token] for item in window)
    return False


def shell_script(tokens: list[str]) -> str | None:
    name = tokens[0].rsplit("/", 1)[-1]
    if name == "eval":
        return " ".join(tokens[1:])
    if name in SHELLS:
        for index, token in enumerate(tokens[1:-1], start=1):
            if SHELL_C_FLAGS.match(token):
                return tokens[index + 1]
    return None


def is_unguarded_install(tokens: list[str]) -> bool:
    tokens = strip_prefix(tokens)
    if not tokens:
        return False
    if tokens[0] in TRUSTED_SFW:
        return False
    script = shell_script(tokens)
    if script is not None:
        return find_unguarded(script)

    name = tokens[0].rsplit("/", 1)[-1]
    args = tokens[1:]
    if name == "sfw":
        return is_unguarded_install(args)
    if PYTHON_NAME.match(name) and "-m" in args[:-1]:
        module = args[args.index("-m") + 1]
        if not PIP_NAME.match(module):
            return False
        name, args = "pip", args[args.index("-m") + 2 :]
    elif PIP_NAME.match(name):
        name = "pip"
    rest = [token for token in args if not token.startswith("-")]

    if name == "yarn" and not args:
        return True
    if name == "uv":
        return uv_fetches(rest)
    if name not in GUARDED or not rest or rest[0] in NON_FETCHING_FIRST:
        return False
    return any(token in GUARDED[name] for token in rest[:SUBCOMMAND_WINDOW])


def find_unguarded(command: str) -> bool:
    for match in SUBSTITUTION.finditer(command):
        if find_unguarded(match.group(1) or match.group(2) or ""):
            return True
    try:
        return any(is_unguarded_install(segment) for segment in split_segments(command))
    except ValueError:
        return fails_closed(command)


def fails_closed(command: str) -> bool:
    """Unparseable commands are denied when they look like a package fetch."""
    match = FALLBACK.search(command)
    if match is None:
        return False
    return re.search(r"\bsfw\b[^;&|\n]*$", command[: match.start()]) is None


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
        "コマンドを解析できない場合も、パッケージ取得の可能性があれば拒否します。"
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
