---
name: windows-shell-editing
description: "Prefer shell_command over apply_patch for file edits in Windows sandbox environments, especially when apply_patch fails with sandbox wrapper, restricted-token, or split writable root errors. Use when editing files on Windows and you need a repeatable shell-first workflow with explicit verification before and after changes."
---

# Windows Shell Editing

## Overview

Use `shell_command` as the default file editing path on Windows when `apply_patch` is unreliable in the current sandbox. Keep edits minimal, write through PowerShell, and verify the target file contents immediately after each change.

## Workflow

1. Confirm the target file path and the exact change before editing.
2. Prefer PowerShell content replacement or append operations through `shell_command`.
3. Keep temporary files inside the active workspace when possible.
4. Re-read the edited file immediately after writing.
5. Summarize the actual change, not just the intended change.

## Editing Rules

- Prefer `Set-Content`, `Add-Content`, or explicit read/replace/write flows in PowerShell.
- Avoid `apply_patch` when the environment is Windows and prior runs showed sandbox wrapper failures.
- Avoid broad rewrites when a scoped replacement is sufficient.
- Preserve UTF-8 text handling and existing line-ending conventions unless the task explicitly changes them.
- When editing multiple files, verify each file after its write step.

## Verification

- Read the edited file after every write.
- If relevant, run the smallest validation command that proves the edit is syntactically or behaviorally correct.
- If a shell-based edit is less precise than a patch would be, call that out and verify more aggressively.

## Known Failure Pattern

If `apply_patch` fails with messages involving `failed to prepare windows sandbox wrapper`, `restricted-token sandbox`, or `split writable root sets`, stay on the shell-first path for the rest of the task unless the environment is changed.
