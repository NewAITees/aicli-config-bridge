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

- [x] Skills: Codex・Claudeの自作スキルをshared/agent固有へ棚卸し
- [x] Skills: Git管理内の正本へ既存スキルを保存
- [x] Skills: status/apply/importと競合停止・バックアップを実装
- [x] Skills: 個別プロジェクトから登録した新規スキルを両Agentへ配置可能にする
- [x] Skills: システム・プラグイン・秘密情報を管理対象外として文書化
- [x] Codex AGENTS: 現行内容をリポジトリ内へ正本化
- [x] Codex AGENTS: WSL・Windows両配置先をリンク設計図へ追加
- [x] Codex AGENTS: 既存環境のリンク切替と別PC向け再現経路を検証
- [x] RTK: Windows Codex用NodeアダプターとcommandWindowsを追加
- [x] RTK: Windows Claude・Codex両方のHook配置を検証
- [x] RTK: Windows/WSL共通仕様とテストを更新
- [x] RTK: Linux版0.42.4をCodex・WSL ClaudeのPreToolUse Hookへ統合
- [x] RTK: Hook設定をaicli-config-bridgeの管理対象へ追加
- [x] RTK: 変換・二重適用・復旧経路を検証
- [x] alignment: Project Treeを中心とする共有構造の作成・保守規則をAGENTS.mdへ追加
- [x] alignment: 日本語 / English併記の視覚的な基本形式へtasks/alignment.mdを更新
- [x] alignment: lessonsとの責務分離とシンボリックリンク探索の学びを記録
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
- [x] `RTK.md` 参照の実体場所を確認し、参照切れをHook中心の共通仕様へ移行する
- [ ] `.gitignore` と生成物管理を確認し、`__pycache__` などの不要物が作業対象に混ざらないようにする

## ループエンジニアリング: 自律実行ガードレール整備（2026-08-31 承認・完了）

- [x] `hook_pre_commands.sh` のstdin JSON読み取りバグを修正（`$1`実質無効化を解消）
- [x] `hook_pre_commands_rules.json` を見直し（git commit/push全面禁止等の過剰ルールを削除、真に不可逆な操作のみ`ask`判定に）
- [x] `hook_test_gate.sh` を新規作成（Stopフックでpytest/npm testを実行、失敗時は完了をブロック）
- [x] `aicli-links.json` に `claude-hook-test-gate` を追加し `apply` でリンク作成
- [x] `~/.claude/settings.json` にStopフック配線を追加（事前バックアップ済み）
- [x] `project-configs/.claude/CLAUDE.md` の第1原則直下に、ユーザー承認による運用範囲緩和の条項を追記
- [x] `pytest` / `ruff check` / `mypy` 全通過を確認
- [ ] 別PC・別プロジェクトで `apply` 後にフックが実際に発火するか実環境で再検証する

## 外部プラグイン導入 + vibe-diff/test-requirements スキル追加(2026-08-31 承認・完了)

- [x] `claude plugin marketplace add` で anthropics/skills・trailofbits/skills・getsentry/plugin-claude を登録
- [x] 9プラグイン（example-skills, static-analysis, second-opinion, spec-to-code-compliance,
      audit-context-building, supply-chain-risk-auditor, security-guidance, claude-security, sentry）
      をこのマシンにインストールし `claude plugin list` で `enabled` を確認
- [x] `vibe-diff`・`test-requirements` を独自の配布機構ではなく、既存の `project-configs/skills/claude/`
      + `aicli-config-bridge skills apply` に統合して作成・配布
- [x] `docs/skills/install-external-plugins.sh` を新規作成（別PCでの外部プラグイン再現用、
      スキル自体は本ブリッジの既存機構でカバーするため対象外）
- [ ] `static-analysis` と `security-guidance` の役割分担（重複回避のためどちらをメインにするか）を決める
- [ ] Sentryプラグインは別途アカウント連携（OAuth等）が必要（未実施）

## マルチモデル実装委任: codex-implementスキル新規作成(2026-08-31 承認・完了)

- [x] ロードマップのステップ4・5(`claude-code-router`+Ollama+ChatGPT)を性能比較し不採用と判断
      （既存の`delegate`スキルの方が実装品質・実績で上回るため。詳細はセッション内比較）
- [x] `delegate`スキル(agent-wrapper)はダッシュボード承認前提で「普段使い」には重いとユーザーが判断
- [x] 軽量な代替として`codex-implement`スキルを新規作成（`codex exec -s workspace-write`の同期直接呼び出し、
      ダッシュボードなし）。project-configs/skills/claude/codex-implement/ に配置し`skills apply`で配布
- [x] Codexの役割は「実装後に変更内容を平易な日本語で説明する説明役」とし、レビューの正当性は
      Claude自身が`git diff`とテスト再実行で担保する設計にした
- [x] ステップ6(サブエージェント定義)は既存の`planner`/`implementer`/`code-reviewer`等を変更せず、
      新規スキルの追加のみで対応（変更範囲を限定）
- [ ] 実際のタスクで`codex-implement`スキルを使い、動作を検証する
- [x] `codex-implement`を自前の`codex exec`直接呼び出しから、既にインストール済みの
      `codex`プラグインの`/codex:rescue --write`(codex-companionランタイム)経由に修正
- [x] `project-configs/.claude/CLAUDE.md`（グローバル配布）にスキル・プラグインの発火ルールを追記。
      特にレビュー系（security-guidance/codex:review/second-opinion/static-analysis/
      claude-security/supply-chain-risk-auditor/spec-to-code-compliance）の使い分け表を作成し、
      `security-guidance`と`static-analysis`の役割分担の課題もここで解消
- [ ] `spec-to-code-compliance`用の`specs/`ディレクトリ運用は未整備（仕様書がある場合のみ使う設計）
