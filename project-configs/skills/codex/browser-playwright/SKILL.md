---
name: browser-playwright
description: Use when browser automation, UI testing, form filling, screenshots, accessibility snapshots, or page inspection are needed through Playwright MCP.
---

# Browser Playwright

Use Playwright MCP for browser tasks.

## Workflow

1. Open the target page.
2. Capture an accessibility snapshot and inspect refs.
3. Interact using refs from the snapshot.
4. Re-snapshot after significant page changes.
5. Use screenshot, console, or network tools when needed.

## Use Cases

- UI regression checks
- Form input and submission
- Page navigation checks
- Screenshot capture
- Console and network inspection

## Guidance

- Prefer accessibility snapshot refs over visual guessing.
- After clicks, submits, or navigation, re-snapshot before the next action.
- When debugging, inspect console and network before retrying blind actions.
- Keep the workflow deterministic and small-step.
- See `/home/perso/analysis/aicli-config-bridge/docs/skills/playwright-common-spec.md` for the shared contract.
