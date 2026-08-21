# Skill Reference

## Runtime Components

- FastAPI server: `inference/server.py`
- Vector store wrapper: `data/vector_store.py`
- LLM wrapper: `inference/llm.py`
- Spreading logic: `inference/spreading.py`
- Metabolism logic: `inference/metabolism.py`
- Automation helpers: `inference/automation.py`

## Ingest Memory Axes

`/ingest` で指定できる属性:
- `kind`
- `scope`
- `source_type`

代表値:
- `kind`: `knowledge`, `private_memory`, `episodic`, `entity`, `document_segment`, `moc`
- `scope`: `public_like`, `private`, `intimate`
- `source_type`: `upload`, `conversation`, `synthesis`, `entity_extraction`, `episodic_compression`

## Segmentation Settings

- `SEGMENT_ENABLED`
- `SEGMENT_MIN_CHARS`
- `SEGMENT_TARGET_CHARS`
- `SEGMENT_MAX_CHARS`
- `SEGMENT_HEADING_LEVELS`
- `SEGMENT_GENERATE_ROOT_SUMMARY`

## Retrieval Settings

- `RETRIEVAL_ACTIVE_NODE_LIMIT`
- `RETRIEVAL_SPREAD_LIMIT`
- `RETRIEVAL_SPREAD_DECAY`
- `RETRIEVAL_SPREAD_DEPTH`

## Metabolism Settings

- `METABOLISM_DECAY_RATE`
- `METABOLISM_REINFORCEMENT_BOOST`
- `METABOLISM_PROTECTION_SIMILARITY_THRESHOLD`
- `METABOLISM_GENERAL_SIMILARITY_THRESHOLD`
- `METABOLISM_DISTILLATION_SIMILARITY_THRESHOLD`
- `METABOLISM_DELETION_THRESHOLD`
- `METABOLISM_DELETION_GRACE_DAYS`
- `METABOLISM_PROTECTION_EXCLUDED_KINDS`
- `METABOLISM_DISTILLATION_EXCLUDED_KINDS`
- `METABOLISM_DELETION_EXCLUDED_KINDS`

## Automation Settings

- `AUTOMATION_INGEST_DIRECTORY`
- `AUTOMATION_INGEST_EXTENSIONS`
- `AUTOMATION_REGISTRY_PATH`
- `AUTOMATION_AUDIT_LOG_PATH`
- `AUTOMATION_SCHEDULER_STATE_PATH`
- `AUTOMATION_METABOLIZE_INTERVAL_HOURS`

## Recommended Operations

1. `.env` を設定する
2. `uv run python -m inference.server` を起動する
3. 実データを `/ingest` に入れる
4. `/search` と `/metabolize` を確認する
5. 安定運用では `inference.automation` を呼ぶラッパーを別途作る

## Not Yet Packaged

- watcher 常駐化
- Bridge Discovery
- Motivation / Attention 連携（読み取り専用の接続点のみ実装済み。エンジン本体は未実装）
