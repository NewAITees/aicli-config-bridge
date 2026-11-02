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

### 開発レビュー・段階的コミット（2026-11-02 意図承認済み）

- [x] spec: 既存開発履歴と未コミット差分をレビューし、必要な修正・検証後に論理単位でローカルコミットする
- [x] 境界: 個人設定の再配置、Hook信頼・有効化、WSL配置、push、既存6件の実行ビット差分は対象外
- [x] 独立レビュー: 共通ガード・設定マージ・スキル配布を分担し、主担当が検証する
- [x] 個人Hookの誤削除・PowerShell削除エイリアス漏れ・Windowsテスト準備を修正
- [x] 全テスト・整形・lint・型・構文・差分を検証する（277 passed、警告なし）
- [x] 実装、設定マージ、スキル、文書の単位で段階的コミットし、残差分を報告する（レビュー詳細: docs/settings/development-review-2026-11-02.md）


### Claude変更のCodex/OpenCode横展開（2026-11-02 意図承認済み）

- [x] spec: 直近1か月の全22コミットと必要な前史を棚卸しし、指示・スキル・Hook・配置を両ツールへ展開する
- [x] 完了条件: 変更ごとの対応表、ネイティブ形式、既存個人設定保持、敵対的入力の検証、実配置確認を揃える
- [x] 境界: 既存6件の実行ビット差分を保持。秘密情報・認証・課金・公開・無関係なsync要件は対象外
- [x] 失敗条件: ask未対応を有効と偽る、未信頼プロジェクトのテスト実行、既存設定の全置換、未実行の実機試験を成功と報告すること
- [x] 停止条件: 危険操作Hookのask/deny、目的の拡大、既存変更との衝突。手順変更だけでは再承認しない
- [x] 共通指示の意味を保ちCodex/OpenCode固有の呼出し・制限へ適応
- [x] OpenCodeのスキル配置定義、欠落しているvibe-diff/test-requirementsを整備
- [x] sfw・危険コマンド・信頼限定テストゲートを共用し管理設定へ配線
- [x] 対応表・設定マージ方針・配置手順・alignmentを更新
- [x] TDD・独立した敵対的レビュー・全テスト・静的解析とOpenCode隔離実機を検証。Windows既存4失敗を記録
- [x] Windowsホームへ31管理リンクとCodex Hookマージを適用（追加承認OK後、旧14リンクと旧Hook JSONを退避）
- [x] 31リンク・46ファイルのSHA一致、旧14対象退避、Hook再マージ無変更を独立確認
- [x] OpenCodeサービス再読込後のプラグインactiveを確認
- [ ] Codex正式 /hooksで3定義を信頼し、危険操作guardも有効化する（自動承認レビューが別途明示承認を要求）
- [ ] Codex信頼後の実行経路で阻止を確認。WSL配置は別途未実施


### Windows Codex/Claude 管理リンク修復（2026-09-01 承認済み）

- [x] spec: 4対象の旧ファイルを復元可能に保存し、Windows側から正本を読める管理リンクへ修復する
- [x] Windowsネイティブのリンク作成条件と正本パスの到達性を確認
- [x] 4対象をバックアップ後に正本へのリンクへ置換
- [x] Windows/WSL両側でリンク実体・内容・ハッシュを検証（4件すべて`SymbolicLink`・正本とSHA-256一致）
- [x] todo / lessons / alignment を実状に合わせて更新

### Windows Codex AGENTS.md 反映不備の診断（2026-09-01 承認済み）

- [x] spec: Windows Codexが読む旧文面の所在とリンク不成立の原因を、変更なしで特定する
- [x] リポジトリ正本とWindows/WSL配置先のパス・リンク・内容を照合
- [x] リンク設計図とCLIの状態判定を照合
- [x] 根本原因と影響範囲を報告（Windows側は通常ファイル、WSL実行では`target_windows`が対象外）

### OpenCode 導入確認・更新（2026-09-01 承認済み）

- [x] spec: 導入有無・導入経路・更新可否と停止条件を定義
- [x] OpenCode の実行パスと現在バージョンを確認（`~/.opencode/bin/opencode` v1.18.25）
- [x] 導入経路に合わせて更新可否を判定し、npm版を `sfw` 経由で v1.18.25 へ更新
- [x] 更新後のバージョンと起動を検証（優先バイナリ・npm版とも v1.18.25）
- [x] 作業結果を todo / lessons に反映

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

- [x] ~~ロードマップのステップ4・5(`claude-code-router`+Ollama+ChatGPT)を性能比較し不採用と判断~~
      **【2026-08-31 ユーザーにより訂正】** この「不採用」判断は誤り。(a)比較基準が
      ロードマップ文書の仮モデル`qwen2.5-coder:14b`のままで、実際に導入済みの
      `qwen3.8:27b`(性能向上済み)を確認していなかった、(b)目的を取り違えた
      ——本来は「Codexのハーネスが使えない場面のための別ハーネス確保」が焦点で、
      delegateは大きめのタスク向けで気軽に使えないため、routerは軽量な並列選択肢
      として**共存**させる設計だった(排他選択ではない)。router+Ollama導入は
      別タスクとして再検討する（[[feedback_comparison_baseline_and_framing]]参照）
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

## レビュー体制の指摘反映（2026-08-31 承認・完了、トークンコスト最小の修正のみ）

- [x] 棚卸し順序: 外部マーケットプレイスより先に`project-configs/skills/`・`.claude/agents/`を
      確認するルールをCLAUDE.mdの発火ルール冒頭に追記
- [x] レビュー系重複: `second-opinion`⇄`/codex:review`の二重呼び出し禁止、
      `security-guidance`⇄`claude-security`の同一ループ内併用禁止をレビュー表の直後に追記
- [x] バージョンピン留め: `claude plugin install`はCLIレベルの`@version`指定に非対応と判明。
      `install-external-plugins.sh`にインストール後の既知バージョン照合(WARN出力)を追加し、
      方針(exact version固定)とCLI制約の矛盾を明文化・部分的に補完
- [x] vibe-diff/test-requirementsのSKILL.mdを確認 — 既に実態(hook委任・evals/なし)と一致しており
      修正不要（乖離があったのは実体化しなかった別文書側のみ）
- [x] 常時発火フックの累積コスト計測: `security-guidance`のStop hookが実測1.8kトークン超
      （Agent SDK経由のLLMレビュー、PostToolUse/Bash(git commit・push)/Stopの全部で発火）と
      判明したため`claude plugin disable security-guidance@claude-plugins-official`で無効化。
      CLAUDE.mdのレビュー使い分け表・併用禁止の記述も実態に合わせて修正
