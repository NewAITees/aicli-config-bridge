#!/usr/bin/env python3
"""Codex adapter for the shared guard; see docs/settings/cross-agent-settings-policy.md."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path
from typing import Callable, cast


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) == 2 else ""
    try:
        common = Path(__file__).resolve().parents[2] / "shared" / "hooks" / "agent_guard.py"
        functions = runpy.run_path(str(common))
        payload = json.load(sys.stdin)
        if mode == "pre":
            evaluate = cast(Callable[[object], dict[str, str]], functions["evaluate_pre"])
            result = evaluate(payload)
        elif mode == "stop":
            evaluate_stop = cast(
                Callable[[object, str], dict[str, str]], functions["evaluate_stop"]
            )
            result = evaluate_stop(payload, "codex")
        else:
            raise ValueError("expected pre or stop")
    except Exception as exc:
        result = {
            "decision": "deny",
            "reason": f"安全フックを評価できません: {type(exc).__name__}: {exc}",
        }
    if mode != "stop" and result["decision"] != "allow":
        reason = result["reason"]
        if result["decision"] == "ask":
            reason += (
                " CodexのPreToolUseはask未対応のため実行を拒否しました。"
                "フックを迂回しないでください。"
            )
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                },
                ensure_ascii=False,
            )
        )
    elif mode == "stop":
        output = (
            {"decision": "block", "reason": result["reason"]}
            if result["decision"] != "allow"
            else {"systemMessage": result["reason"]}
        )
        print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
