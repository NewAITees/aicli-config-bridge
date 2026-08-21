---
name: yadorigi-memory-system
description: Yadorigi memory system を運用するスキル。`/ingest`、`/search`、`/metabolize` の判断基準を Codex 側と揃えたまま、Claude から同じ運用を行うために使う。
---

# Yadorigi Memory System

このスキルは既存の Yadorigi memory system を運用するためのもの。
新規設計ではなく、現在の実装に対する操作ガイドとして使う。

## 何に使うか

- メモや文書を `/ingest` に投入する
- `/search` で関連ノードを調べる
- 必要なノードだけ `GET /nodes/{node_id}` で深掘りする
- `GET /nodes` で直近ノードを時系列（created_at降順）に取得する
- `DELETE /nodes/{node_id}` で不要ノード（テストデータ等）を物理削除する
- `scripts/ingest_lessons.py` で `tasks/lessons.md` を教訓単位で取り込む
- `/metabolize` で保守を行う
- 自動 ingest / 定期 metabolize の最小運用を確認する

## 前提: 想起はhookが自動注入する（2026-07-10〜）

SessionStart hook（直近episodic＋作業ディレクトリ関連の教訓）と UserPromptSubmit hook
（プロンプト内容での `/search`、5分スロットル）が summary を自動注入するため、
起点となる手動 search は不要。手動でAPIを呼ぶのは「注入されたsummaryの深掘り」
「hookが拾わない観点の検索」「時系列の想起」のときだけでよい。

## 基本フロー

1. 実行前提を確認する
2. FastAPI サーバーを起動する（通常はSessionStart hookが自動起動済み）
3. `/ingest` で必要な情報を投入する
4. hookが注入したsummary、または shallow な `/search` で relevance を確認する
5. 必要なノードだけ詳細取得する
6. 必要に応じて `/metabolize` か automation helper を使う

## 共通仕様

以下を先に参照すること:
- `/home/perso/analysis/aicli-config-bridge/docs/skills/memory-common-spec.md`
  - WSL内のパスのため、Windowsセッションでは `wsl -e bash -c 'cat <パス>'` で読むこと。
- `references/skill-reference.md`（実体: `/mnt/c/Users/perso/.claude/skills/yadorigi-memory-system/references/skill-reference.md`）

## 実行前提

次を満たしていること:
- `uv` が使える
- Ollama API `http://127.0.0.1:11436` が起動している
- Qdrant が設定 URL で到達可能
- 対象リポジトリの依存関係が導入済み

## サーバー起動

```bash
uv run python -m inference.server
```

主要 endpoint:
- `GET /health`
- `POST /ingest`
- `POST /search`
- `GET /nodes`（kind / since / limit / active_only、created_at降順）
- `GET /nodes/{node_id}`
- `DELETE /nodes/{node_id}`
- `POST /metabolize`
- `POST /metabolize/review-ack`

## Claude 向けメモ

- `search` 前に relevance を決め打ちしない
- `summary` だけで十分なら詳細取得しない
- `detail_ref` は取得 API ではない
- private な探索では filter を省略しない

## Guardrails

- 実装されていない機能を available と書かない
- watcher 常駐運用や Bridge Discovery を既実装扱いしない
- 既存 endpoint と helper を使い、新しい入口を勝手に作らない
