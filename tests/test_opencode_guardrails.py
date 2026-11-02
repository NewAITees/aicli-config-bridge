"""OpenCode 2 native permission and shell hooks, without executing guarded commands."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

PLUGIN = (
    Path(__file__).parents[1] / "project-configs/.config/opencode/plugins/aicli-guardrails/index.js"
)


def exercise_plugin(scenario: dict[str, object]) -> dict[str, Any]:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required to exercise the OpenCode plugin")
    script = r"""
import { createRequire, syncBuiltinESMExports } from 'node:module';
const require = createRequire(import.meta.url);
const cp = require('node:child_process');
const scenario = JSON.parse(process.argv[1]);
const calls = [];
cp.spawnSync = (program, args, options) => {
  calls.push({program, args, input: options.input, shell: options.shell});
  if (args.includes('pre')) {
    if (scenario.guardCrash) return {status:1,stdout:'',stderr:'failed'};
    if (scenario.guardMalformed) return {status:0,stdout:'oops',stderr:''};
    return {status:0,stdout:JSON.stringify(scenario.guard ?? {decision:'allow'}),stderr:''};
  }
  if (scenario.rtkMissing) return {status:null,error:new Error('ENOENT'),stdout:''};
  return {status:0,stdout:scenario.rtkOutput ?? '',stderr:''};
};
syncBuiltinESMExports();
const module = await import(process.argv[2]);
const hooks = {};
await module.default.setup({
  location:{directory:scenario.directory ?? 'C:/project'},
  permission:{hook:async(name,callback)=>{hooks[`permission:${name}`]=callback;}},
  shell:{hook:async(name,callback)=>{hooks[`shell:${name}`]=callback;}},
});
const event = scenario.permission
  ? {action:scenario.action ?? 'shell',resources:scenario.resources ?? ['git status'],
     effect:scenario.effect ?? 'allow'}
  : {command:scenario.command ?? 'git status',cwd:scenario.cwd ?? 'C:/project',
     shell:scenario.shell ?? '/bin/bash',env:{},timeout:60000};
let error;
try { await hooks[scenario.permission ? 'permission:evaluate' : 'shell:create.before'](event); }
catch(caught) { error=caught.message; }
process.stdout.write(JSON.stringify({calls,event,error,exports:Object.keys(module),
  hooks:Object.keys(hooks),id:module.default.id}));
"""
    result = subprocess.run(
        [node, "--input-type=module", "-e", script, json.dumps(scenario), PLUGIN.as_uri()],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("decision", ["ask", "deny"])
def test_permission_decisions_use_native_effects(decision: str) -> None:
    result = exercise_plugin(
        {"permission": True, "guard": {"decision": decision, "reason": "dangerous"}}
    )
    assert "error" not in result
    assert result["event"]["effect"] == decision
    assert result["event"]["message"] == "dangerous"
    assert len(result["calls"]) == 1


@pytest.mark.parametrize("effect", ["ask", "deny"])
def test_safe_commands_do_not_weaken_personal_permissions(effect: str) -> None:
    result = exercise_plugin({"permission": True, "effect": effect})
    assert result["event"]["effect"] == effect


def test_danger_ask_does_not_override_an_existing_denial() -> None:
    result = exercise_plugin({"permission": True, "effect": "deny", "guard": {"decision": "ask"}})
    assert result["event"]["effect"] == "deny"


def test_deny_stops_actual_shell_before_rtk() -> None:
    result = exercise_plugin({"guard": {"decision": "deny", "reason": "sfw required"}})
    assert "sfw required" in result["error"]
    assert len(result["calls"]) == 1
    assert result["event"]["command"] == "git status"


@pytest.mark.parametrize("failure", ["guardCrash", "guardMalformed"])
@pytest.mark.parametrize("permission", [False, True])
def test_guard_failure_never_allows_execution(failure: str, permission: bool) -> None:
    result = exercise_plugin({failure: True, "permission": permission})
    if permission:
        assert result["event"]["effect"] == "deny"
    else:
        assert result["error"]
    assert len(result["calls"]) == 1


def test_original_command_checked_before_rtk_rewrite() -> None:
    result = exercise_plugin(
        {
            "cwd": "C:/work with spaces",
            "rtkOutput": json.dumps(
                {"hookSpecificOutput": {"updatedInput": {"command": "rtk git status"}}}
            ),
        }
    )
    assert "error" not in result
    assert len(result["calls"]) == 2
    payload = json.loads(result["calls"][0]["input"])
    assert payload["tool_input"]["command"] == "git status"
    assert payload["cwd"] == "C:/work with spaces"
    assert result["calls"][0]["args"][:2] == ["-X", "utf8"]
    assert result["calls"][0]["args"][-3:] == ["pre", "--agent", "opencode"]
    assert result["event"]["command"] == "rtk git status"
    assert result["event"]["cwd"] == "C:/work with spaces"
    assert not any(call.get("shell") for call in result["calls"])


@pytest.mark.parametrize("scenario", [{"rtkMissing": True}, {"rtkOutput": "malformed"}])
def test_optional_rtk_failure_preserves_checked_command(scenario: dict[str, object]) -> None:
    result = exercise_plugin(scenario)
    assert "error" not in result
    assert result["event"]["command"] == "git status"


def test_powershell_is_checked_without_bash_rewriting() -> None:
    result = exercise_plugin(
        {"shell": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"}
    )
    assert "error" not in result
    assert len(result["calls"]) == 1


def test_non_shell_permissions_are_unchanged() -> None:
    result = exercise_plugin({"permission": True, "action": "read"})
    assert result["calls"] == []
    assert result["event"]["effect"] == "allow"


def test_missing_shell_resources_are_denied() -> None:
    result = exercise_plugin({"permission": True, "resources": []})
    assert result["event"]["effect"] == "deny"


def test_v2_definition_and_no_fake_stop_gate() -> None:
    result = exercise_plugin({})
    assert result["exports"] == ["default"]
    assert result["id"] == "aicli-guardrails"
    assert result["hooks"] == ["permission:evaluate", "shell:create.before"]


@pytest.mark.parametrize(
    ("command", "effect"),
    [
        ("npm install left-pad", "deny"),
        ("env -S 'npm install left-pad'", "deny"),
        ("rm\t-rf\tbuild", "ask"),
        ("git push -uf origin main", "ask"),
    ],
)
def test_real_plugin_and_shared_guard_use_native_effects(command: str, effect: str) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required to exercise the OpenCode plugin")
    script = r"""
const module=await import(process.argv[1]);
const hooks={};
await module.default.setup({location:{directory:process.cwd()},
  permission:{hook:async(name,cb)=>{hooks.permission=cb;}},
  shell:{hook:async(name,cb)=>{hooks.shell=cb;}},
});
const event={action:'shell',resources:[process.argv[2]],effect:'allow'};
await hooks.permission(event);
process.stdout.write(JSON.stringify(event));
"""
    result = subprocess.run(
        [node, "--input-type=module", "-e", script, PLUGIN.as_uri(), command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    output = json.loads(result.stdout)
    assert output["effect"] == effect
    assert "guard failed" not in output["message"]
    assert "invalid JSON" not in output["message"]
    assert "\ufffd" not in output["message"]
