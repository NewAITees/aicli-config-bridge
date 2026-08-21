---
name: architect
description: Refactor code structure and responsibilities.
---

# Architect

## Purpose

Improve code structure without changing intent.

## Use This Skill To

- Split long files or long functions
- Remove duplicated logic
- Reassign responsibility boundaries
- Make modules easier to reason about

## Checks

- Can each file be described in one sentence?
- Are there repeated patterns that should be centralized?
- Are unrelated responsibilities mixed together?
- Is a function doing too much?

## Process

1. Find the smallest structural problem worth fixing.
2. Change only the boundary that needs to move.
3. Keep behavior stable while reshaping the structure.
4. Re-run the relevant tests or checks.

## Guardrails

- Do not refactor everything at once.
- Do not change behavior just to make the code look different.
- Do not expand the scope beyond the structural issue being addressed.
- See `/home/perso/analysis/aicli-config-bridge/docs/skills/architect-common-spec.md` for the shared contract.
