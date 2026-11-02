// OpenCode 2 adapter for docs/settings/cross-agent-settings-policy.md.
// The shared driver owns sfw and dangerous-command rules. No SDK dependency.
import { spawnSync } from "node:child_process";
import { realpathSync } from "node:fs";
import { basename, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const driver = resolve(
  dirname(realpathSync(fileURLToPath(import.meta.url))),
  "../../../../shared/hooks/agent_guard.py",
);

function check(command, cwd) {
  if (typeof command !== "string" || !command.trim()) {
    throw new Error("aicli guard: a shell command is required; execution stopped.");
  }
  const payload = JSON.stringify({tool_input: {command}, cwd});
  const result = spawnSync(process.platform === "win32" ? "python" : "python3",
    ["-X", "utf8", driver, "pre", "--agent", "opencode"], {
      input: payload, encoding: "utf8", timeout: 30_000, maxBuffer: 1_048_576, windowsHide: true,
    });
  if (result.error || result.status !== 0) {
    throw new Error("aicli guard failed; execution stopped. Check Python and hook deployment.");
  }
  let decision;
  try { decision = JSON.parse(result.stdout); }
  catch { throw new Error("aicli guard returned invalid JSON; execution stopped."); }
  if (!["allow", "ask", "deny"].includes(decision?.decision)) {
    throw new Error("aicli guard returned an invalid decision; execution stopped.");
  }
  return decision;
}

// V2 reads this definition directly; no V1 compatibility entrypoint is provided.
export default {
  id: "aicli-guardrails",
  async setup(ctx) {
    // Native evaluation is after personal rules, before a permission prompt or
    // action. Preserve existing ask/deny decisions when the shared guard allows.
    await ctx.permission.hook("evaluate", async (event) => {
      if (event.action !== "shell") return;
      try {
        if (!Array.isArray(event.resources) || event.resources.length === 0) {
          throw new Error("aicli guard: shell permission has no command resources.");
        }
        for (const command of event.resources) {
          const decision = check(command, ctx.location.directory);
          if (decision.decision === "deny") {
            event.effect = "deny";
            event.message = decision.reason;
            return;
          }
          if (decision.decision === "ask" && event.effect !== "deny") {
            event.effect = "ask";
            event.message = decision.reason;
          }
        }
      } catch (error) {
        event.effect = "deny";
        event.message = error.message;
      }
    });

    // Inspect the actual command again before optimization, using its actual
    // working directory. Dangerous-operation asks belong to native permissions
    // above; rejecting them here would also reject an explicitly approved ask.
    await ctx.shell.hook("create.before", async (event) => {
      const decision = check(event.command, event.cwd);
      if (decision.decision === "deny") {
        throw new Error(`aicli guard: ${decision.reason}. Execution stopped.`);
      }
      // RTK handles POSIX command syntax. Keep native PowerShell/cmd unchanged.
      const shellName = basename(event.shell.replaceAll("\\", "/")).replace(/\.exe$/iu, "");
      if (!["bash", "sh", "zsh"].includes(shellName.toLowerCase())) return;
      const optimized = spawnSync(process.platform === "win32" ? "rtk.exe" : "rtk",
        ["hook", "claude"], {
          input: JSON.stringify({tool_name: "Bash", tool_input: {command: event.command}, cwd: event.cwd}),
          encoding: "utf8", timeout: 30_000, maxBuffer: 1_048_576, windowsHide: true,
        });
      if (optimized.error || optimized.status !== 0) return;
      try {
        const lines = optimized.stdout.split(/\r?\n/u).filter((line) => line.trim());
        const rewritten = JSON.parse(lines.at(-1)).hookSpecificOutput?.updatedInput?.command;
        if (typeof rewritten === "string" && rewritten.trim()) event.command = rewritten;
      } catch {
        // RTK is optional compression; mandatory policy evaluation already ran.
      }
    });
  },
};
