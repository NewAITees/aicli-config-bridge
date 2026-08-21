---
name: feedback-loop
description: Implement and validate changes in small steps.
---

# Feedback Loop

## Purpose

Keep implementation tight, testable, and grounded in evidence.

## Use This Skill To

- Write the smallest code change that could work
- Add or run the most relevant validation first
- Iterate based on actual results, not assumptions
- Catch warnings, regressions, and edge cases early

## Process

1. Red: write or identify a failing check that represents the goal.
2. Green: make the smallest change that passes that check.
3. Refactor: clean up only after behavior is stable.
4. Re-run the relevant validation after each meaningful step.

## Validation Priority

- First: focused test or smoke check
- Then: broader test coverage if the change is risky
- Then: static checks if the repo uses them

## Guardrails

- Do not skip validation because the change looks small.
- Do not add unrelated cleanup while the behavior is still unstable.
- Do not move on while warnings or errors still explain the problem.
- See `/home/perso/analysis/aicli-config-bridge/docs/skills/feedback-loop-common-spec.md` for the shared contract.
