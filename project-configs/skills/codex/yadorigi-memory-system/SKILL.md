---
name: yadorigi-memory-system
description: Operate the Yadorigi local knowledge-metabolism system built on FastAPI, Qdrant, and Ollama. Use when Codex needs to ingest notes, segment long documents, search with memory filters, run metabolize cycles, or operate the minimal automation helpers for directory scan, processed file registry, scheduler, and audit log.
---

# Yadorigi Memory System

Use this skill to operate the existing Yadorigi memory system in this repository.
Treat it as an operations guide for the current implementation, not as a design spec.

## Use This Skill To

- ingest notes and documents
- search existing memory nodes
- inspect relevant nodes in depth
- run metabolize maintenance
- operate the minimal automation helpers

## Workflow

1. Confirm runtime prerequisites.
2. Start the FastAPI server.
3. Use `/ingest` for new material.
4. Use `/search` for broad retrieval first.
5. Use `GET /nodes/{node_id}` only for relevant nodes.
6. Use `/metabolize` or automation helpers when maintenance is needed.

## Shared Rules

Follow the common operating contract in:
- `/home/perso/analysis/aicli-config-bridge/docs/skills/memory-common-spec.md`
- `references/skill-reference.md`（実体: `/mnt/c/Users/perso/.codex/skills/yadorigi-memory-system/references/skill-reference.md`）

## Runtime Prerequisites

Require all of the following before relying on the system:
- `uv` is available
- Ollama API is available at `http://127.0.0.1:11436`
- Qdrant is reachable at the configured URL, currently expected to be `http://localhost:6333`
- dependencies are installed for this repo

## Server Entry Point

Start the server with:

```powershell
uv run python -m inference.server
```

Main endpoints:
- `GET /health`
- `POST /ingest`
- `POST /search`
- `GET /nodes` (kind / since / limit / active_only filters, created_at descending)
- `GET /nodes/{node_id}`
- `DELETE /nodes/{node_id}` (physical delete; 404 for missing or non-UUID ids)
- `GET /research-threads`
- `POST /research-threads`
- `GET /research-threads/{thread_id}`
- `POST /research-threads/{thread_id}/append`
- `GET /research-threads/summary`
- `GET /purpose-profile/summary`
- `POST /metabolize`
- `POST /metabolize/review-ack`

## Ingest

Use `/ingest` with the shared contract from the common spec.
Codex-specific reminder:
- prefer `content` when the text is already in the session
- split heading-poor long text semantically before ingest
- set `kind/scope/source_type` explicitly for private memory

## Search

Use `/search` for vector retrieval plus activation spreading.
Codex-specific reminder:
- start shallow, then deep-dive
- judge from `summary` first
- `detail_ref` is not a fetchable handle
- `GET /nodes/{node_id}` returns 404 both for missing ids and invalid UUIDs
- `GET /nodes?kind=episodic&limit=N` returns recent nodes in created_at descending order (use for "what happened recently" instead of vector search)

## Lessons Ingest Batch

`scripts/ingest_lessons.py` ingests a project's `tasks/lessons.md` per `###` heading
as `kind=knowledge` nodes:

```powershell
uv run python scripts/ingest_lessons.py <path/to/tasks/lessons.md> [--url http://127.0.0.1:54217]
```

Re-running does not duplicate nodes: the script deletes existing nodes with the same
`detail_ref` before ingesting (replace semantics). Note consult-before-write alone does
NOT guarantee this — LLM summaries vary between runs, so identical source text can fall
below the similarity threshold and create duplicates. Run the script after adding new
lessons so they become recallable by memory-injection hooks.

## Memory Injection Hooks (Claude Code side)

Claude Code sessions get automatic memory injection since 2026-07-10: a SessionStart hook
injects recent episodic nodes plus cwd-related knowledge, and a UserPromptSubmit hook
searches per prompt (5-min throttle). Repo copies live in `C:/analysis2/yadorigi/hooks/`;
deployed copies in `~/.claude/hooks/`. Codex sessions do not have these hooks — search
manually as described above.

## Metabolize

Use `/metabolize` for maintenance.
Keep descriptions aligned to implemented behavior only. Do not describe Bridge Discovery as implemented.

## Automation

Use the helpers in `inference/automation.py` for the minimal recurring workflow.

Available helpers:
- `scan_ingest_directory`
- `ProcessedFileRegistry`
- `AuditLogger`
- `MetabolizeScheduler`
- `run_auto_ingest`
- `run_scheduled_metabolize`

Current scope:
- directory scan batch
- processed file registry
- audit log writing
- interval-based scheduler state

Not yet included:
- long-running watcher
- service wrapper
- explicit ingest queue process

`ProcessedFileRegistry` and `MetabolizeScheduler` serialize reads/writes of their JSON state files
with an OS-level advisory lock (`flock`/`msvcrt.locking`), so multiple processes (e.g. this Codex
session and a concurrent Claude Code session) touching the same state files will not lose updates.

## Settings

Read `references/skill-reference.md` when you need the setting catalog.
Use the repo `.env` values as the source of truth for runtime configuration.

## References

Read these files as needed:
- `/home/perso/analysis/aicli-config-bridge/docs/skills/memory-common-spec.md` for the shared contract
- `references/skill-reference.md` for settings and runtime map
- `C:/analysis2/yadorigi/docs/segmentation_spec.md` / WSL `/mnt/c/analysis2/yadorigi/docs/segmentation_spec.md` for segmentation details
- `C:/analysis2/yadorigi/docs/next_spec.md` / WSL `/mnt/c/analysis2/yadorigi/docs/next_spec.md` for next-phase status
- `C:/analysis2/yadorigi/docs/node_schema.md` / WSL `/mnt/c/analysis2/yadorigi/docs/node_schema.md` for node payload shape

## Guardrails

Keep descriptions aligned to implemented behavior.
Do not claim watcher-based automation, Bridge Discovery, or packaged plugin distribution as available.
Use the existing endpoints and helper functions instead of inventing new entry points.
