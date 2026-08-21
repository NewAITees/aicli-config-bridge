---
name: commit-flow
description: Validate, stage, and commit finished changes.
---

# Commit Flow

## Purpose

Turn a completed change into a clean commit.

## Use This Skill To

- Review the final diff
- Run the relevant checks before committing
- Stage only intended files
- Write a clear conventional commit message

## Process

1. Review `git diff` and `git diff --staged`.
2. Remove accidental edits or debug leftovers.
3. Run the relevant tests or checks.
4. Stage only the intended files.
5. Commit with a short conventional message.

## Commit Rules

- Prefer one logical change per commit.
- Do not commit failing code.
- Do not use `--no-verify` to bypass checks.
- Do not stage unrelated files.

## Guardrails

- If validation fails, fix it before committing.
- If the diff is wider than intended, split the work.
- If the commit message cannot explain the change, rewrite it.
- See `/home/perso/analysis/aicli-config-bridge/docs/skills/commit-flow-common-spec.md` for the shared contract.