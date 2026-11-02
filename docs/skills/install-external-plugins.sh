#!/bin/bash
# install-external-plugins.sh — register the external Claude Code plugin
# marketplaces and install the plugins used by this project's harness
# (destructive-op guardrails, security review, spec-compliance auditing).
#
# vibe-diff / test-requirements are NOT installed by this script — they are
# managed as portable skills under project-configs/skills/claude/ and are
# distributed by `uv run aicli-config-bridge skills apply` instead (see
# docs/SETUP_GUIDE.md). This script only covers plugins that live outside
# this bridge's own file-linking system.
#
# Idempotent-ish: re-running is safe; `claude plugin` no-ops or errors
# harmlessly on already-registered marketplaces / already-installed plugins.
set -e

echo "== Registering marketplaces =="
claude plugin marketplace add anthropics/skills || true
claude plugin marketplace add trailofbits/skills || true
claude plugin marketplace add getsentry/plugin-claude || true
# claude-plugins-official ships pre-registered on most installs; add defensively.
claude plugin marketplace add anthropics/claude-plugins-official || true

echo "== Installing plugins =="
claude plugin install example-skills@anthropic-agent-skills -y
claude plugin install static-analysis@trailofbits -y
claude plugin install second-opinion@trailofbits -y
claude plugin install spec-to-code-compliance@trailofbits -y
claude plugin install audit-context-building@trailofbits -y
claude plugin install supply-chain-risk-auditor@trailofbits -y
claude plugin install security-guidance@claude-plugins-official -y
claude plugin install claude-security@claude-plugins-official -y
claude plugin install sentry@sentry-plugin-marketplace -y

echo "== Verifying =="
claude plugin list

cat <<'EOF'

Done. Notes:
- Marketplace names (anthropic-agent-skills / trailofbits / sentry-plugin-marketplace /
  claude-plugins-official) are assigned by `claude plugin marketplace add` from
  each repo's own marketplace.json — they should match, but if a name differs
  on this machine, run `claude plugin marketplace list` and fix the @marketplace
  suffixes above before re-running the install section.
- sentry@sentry-plugin-marketplace installs the plugin shell only. Actual use
  requires this machine's own Sentry account authorization (OAuth) — not
  something this script does or should do.
- After this script, run `uv run aicli-config-bridge skills apply` from this
  repo to link vibe-diff / test-requirements into ~/.claude/skills/.
EOF
