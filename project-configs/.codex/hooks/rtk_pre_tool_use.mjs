#!/usr/bin/env node

import { spawnSync } from "node:child_process";

let hookInput = "";
process.stdin.setEncoding("utf8");
for await (const chunk of process.stdin) {
  hookInput += chunk;
}

const rtkCommand = process.env.RTK_BINARY || "rtk.exe";
const result = spawnSync(rtkCommand, ["hook", "claude"], {
  encoding: "utf8",
  input: hookInput,
  windowsHide: true,
});

if (result.error || result.status !== 0) {
  process.exit(0);
}

const lines = result.stdout
  .split(/\r?\n/u)
  .map((line) => line.trim())
  .filter(Boolean);

if (lines.length === 0) {
  process.exit(0);
}

let output;
try {
  output = JSON.parse(lines.at(-1));
} catch {
  process.exit(0);
}

const specific = output?.hookSpecificOutput;
if (specific?.updatedInput && typeof specific.updatedInput === "object") {
  specific.permissionDecision = "allow";
}

process.stdout.write(`${JSON.stringify(output)}\n`);
