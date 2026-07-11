## 運用ルール
1. タスクを追加するときはチェックボックス形式で書く
2. 完了したら [x] にする
3. セクションが全て完了したら、セクションごと削除してよい

## ドキュメント・仕様を実装に同期（2026-07-11 承認済み）

- [x] USAGE.md（2026-02-05の旧開発計画、未実装フェーズ群）を削除
- [x] agent.md（symbolicLink/CLAUDE.md へのリンク切れ）を削除
- [x] CLAUDE.md の構造・コマンド・実装状況を現行実装（cli.py + setup/、setup/apply/status/init）に書き直し
- [x] README.md のディレクトリ構造・コマンド説明を現行実装に修正
- [x] aicli-links.json の gemini-md エントリ（missing_source かつ GEMINI.md→settings.json の誤マッピング）を削除
- [x] pytest / ruff / mypy で検証（19 passed / ruff OK / mypy OK）
- [x] lessons.md に学びを記録

## 現在のタスク

- [x] tasks/ ディレクトリ作成
- [x] spec: spec スキルを Spec中心開発向けに再定義
- [x] spec: codex / claude 実体反映用の差分案を整理
- [x] spec: 成功条件・失敗条件・停止条件の観点を共通仕様へ追加
- [x] spec: 成功条件・失敗条件・停止条件を実体 SKILL に同期
- [ ] Codex-maxxing記事の分析・CLAUDE.md取り入れ検討
- [x] codex と claude の skills / setting.json 差分調査
- [x] spec: codex / claude 共通 skill 運用整備 — 完了基準: `git diff -- docs symbolicLink/.codex symbolicLink/.claude`
- [x] 共通 memory skill 仕様の作成
- [x] codex / claude の memory skill 整備
- [x] 設定ポリシーと対応表の作成
- [x] playwright / spec / feedback-loop / commit-flow / architect の共通仕様整備

## 現状分析からのTODO候補（2026-07-11）

- [x] spec: `claude-global-md` の `wrong_link` をどう正とするか決める（リポジトリ管理へ戻す）
- [ ] spec: `sync` コマンド実装に着手するか、未実装要件として凍結するか決める（要件元: `docs/REQUIREMENTS_SYNC.md`）
- [x] CLI レベルのテスト方針を決める（`status --json` / `apply --id` / 引数なし起動の対話分岐）
- [ ] CLI テストを追加して `src/aicli_config_bridge/cli.py` の主要コマンドを検証する
- [ ] `pyproject.toml` の依存バージョン指定を運用規約と整合させるか判断する（現状は `>=` 指定）
- [ ] `python --version` が壊れている原因を切り分け、開発環境前提を README かセットアップ手順に反映する
- [ ] `RTK.md` 参照の実体場所を確認し、参照切れなら運用文書側を修正する
- [ ] `.gitignore` と生成物管理を確認し、`__pycache__` などの不要物が作業対象に混ざらないようにする
