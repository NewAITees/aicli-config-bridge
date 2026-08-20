#!/usr/bin/env python3
"""Adapt RTK's Claude hook output to the Codex PreToolUse schema."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


def main() -> int:
    hook_input = sys.stdin.read()
    rtk = shutil.which("rtk")
    if rtk is None:
        return 0

    result = subprocess.run(
        [rtk, "hook", "claude"],
        input=hook_input,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return 0

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return 0

    try:
        output = json.loads(lines[-1])
    except json.JSONDecodeError:
        return 0

    specific = output.get("hookSpecificOutput")
    if isinstance(specific, dict) and isinstance(specific.get("updatedInput"), dict):
        specific["permissionDecision"] = "allow"

    json.dump(output, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
