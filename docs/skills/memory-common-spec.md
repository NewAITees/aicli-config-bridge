# Memory Skill Common Spec

## Goal

`codex` と `claude` の両方で、同じ判断基準で Yadorigi memory system を扱えるようにする。
この文書は共通仕様であり、各エージェント固有の呼び出し手順は各 `SKILL.md` に薄く持たせる。

## Use This Skill To

- メモや文書を `/ingest` に投入する
- `/search` で関連ノードを探索する
- `/metabolize` で保守運転を行う
- 自動 ingest / 定期 metabolize の最小運用を確認する

## Runtime Prerequisites

利用前に次を満たしていること:
- `uv` が使える
- Ollama が起動している
- Qdrant が設定 URL で到達可能
- 対象リポジトリの依存関係が導入済み

## Shared Workflow

1. 実行前提を確認する
2. サーバーを起動する
3. `/ingest` で必要なデータを投入する
4. `/search` で関連ノードを調べる
5. 必要なら `GET /nodes/{node_id}` で詳細確認する
6. 保守が必要なら `/metabolize` を実行する

## Ingest Contract

`/ingest` は `file` または `content` のどちらか一方だけを受け付ける。

主要フィールド:
- `file`
- `content`
- `filename`
- `kind`
- `scope`
- `source_type`

既定値:
- `kind=knowledge`
- `scope=public_like`
- `source_type=upload`

運用ルール:
- 手元に本文があるなら `content` を優先する
- 長文で見出しが弱い場合は、意味単位で自分で分割してから複数回 ingest する
- private 系メモリでは `kind` と `scope` を明示する

## Search Contract

`/search` はベクトル検索と activation spreading を行う。

主要フィールド:
- `query`
- `top_k`
- `spread_limit`
- `candidate_limit`
- `kind_include`
- `scope_exclude`

運用ルール:
- まず shallow な検索を打つ
- `summary` だけで relevance を判断する
- 必要なノードだけ `GET /nodes/{node_id}` で深掘りする
- `detail_ref` はファイル名であり、直接フェッチ可能な参照ではない

## Metabolize Contract

`/metabolize` は保守系操作を行う。

実装済み前提:
- decay
- reinforcement
- entropy protection
- one-to-one distillation
- forced deletion
- size constraint pruning

未実装扱い:
- watcher 常駐運用
- Bridge Discovery
- packaged plugin distribution

## Settings Surface

詳細な設定一覧は各環境の reference から参照するが、共通で意識する軸は次:
- segmentation
- retrieval
- metabolism
- automation

## Guardrails

- 実装されていない機能を利用可能と書かない
- `search` 前に relevance を決め打ちしない
- private データの検索では `scope_exclude` / `kind_include` を省略しない
- 各エージェント固有のコマンドや UI 前提をこの共通仕様に混ぜない
