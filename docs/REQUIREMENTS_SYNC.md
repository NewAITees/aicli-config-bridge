# 要件定義: AI CLIツール間の機能同期コマンド

## 概要

Claude Code / Codex / Gemini CLI の設定ディレクトリ間で、`skills` / `hooks` / `mcp` / `subagent` をコピー・同期できるCLIを提供する。
初期版では「ツール間同期」と「明示パス同期」に絞る。`project` というショートハンドは採用しない。

## 対象ツールと機能

| ツール | 設定ディレクトリ | 対応機能 |
|--------|----------------|----------|
| Claude Code | `~/.claude/` | skills, hooks, mcp |
| Codex | `~/.codex/` | skills, hooks, mcp, subagent |
| Gemini CLI | `~/.gemini/` | hooks, mcp |

補足:
- Gemini CLI の skills は将来的な検討対象とする（初期版では対象外）。
- MCP はディレクトリ形式のみ対応。`settings.json` 内の JSON マージは初期版で行わない。

## 同期対象の概要

### skills

- ディレクトリ階層が深い
- `public` などサブディレクトリ単位の同期ニーズがある

### hooks

- シェルスクリプト + JSON の組み合わせ
- 実行権限を維持する必要がある
- スクリプト内のパスは基本そのままコピー（自動置換はしない）

### mcp

- ディレクトリ形式のみ対象
- JSON 形式は対象外（手動対応）

### subagent

- Codex 固有の YAML 定義

## 同期モード

`--mode` の選択で挙動を切り替える。

- `clean`:
  - 先にコピー先を削除してからコピー
  - 危険度が高いので `--backup` 推奨
- `overwrite`:
  - 同名ファイルは上書き
  - コピー元にないファイルは残る
- `sync`:
  - 差分同期（コピー元にないファイルは削除）
  - 推奨デフォルト

`--dry-run` は常に最優先。実際の変更は行わない。

## コマンド仕様

```bash
aicli-config-bridge sync \
  --type <skills|hooks|mcp|subagent> \
  --from <claude|codex|gemini|パス> \
  --to <claude|codex|gemini|パス> \
  [--mode <clean|overwrite|sync>] \
  [--subdir <サブディレクトリ>] \
  [--backup] \
  [--dry-run]
```

ショートハンド:
- `claude` -> `~/.claude/`
- `codex` -> `~/.codex/`
- `gemini` -> `~/.gemini/`

`project` は初期版で採用しない。

## 対話モード

`sync` サブコマンドを対話的に実行できるようにする。
選択項目に `mode` を含める（`clean` / `overwrite` / `sync`）。

## 実装上の注意

- パーミッション維持: `shutil.copy2` を基本にする。
- hooks のパス置換: 初期版では行わない（必要なら手動で修正）。
- Windows で削除に失敗する場合があるため、失敗一覧を表示して終了コードを非ゼロにする。
- `--dry-run` ではバックアップを含めた一切の副作用を禁止する。

## 未決定事項

- デフォルト `--mode` の最終決定（現状は `sync` 想定）。
- 失敗時のログフォーマットと終了コードの統一ルール。

