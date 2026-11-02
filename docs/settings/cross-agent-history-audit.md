# Claude中心変更の横展開監査 / Cross-Agent History Audit

調査日: 2026-11-02。対象: `C:/analysis2/aicli-config-bridge`、HEAD `d47475c`。
2026-10-01以降の22コミット（実変更20、マージ2）と必要な8月の前史を読み取り専用で確認した。

| コミット | 変更 | 監査時点の横展開状況・必要対応 |
|---|---|---|
| f55441c | 意図承認・5原則、文書と実装の優先順位、外部データ分離 | Codex反映済み。OpenCodeは管理対象なし |
| 3d799ca | sfw必須化Hook、リンク管理、テスト | Claude専用。両対象へ機械的ガードが必要 |
| 0bf4c2d | sfw解析の回避防止・解析不能時の拒否 | 最終版を共用する |
| fd9b227 | sfw解析の残る回避修正 | 最終版を共用する |
| 8f03c3d | スキル共通仕様参照を相対パス化 | Codexにも反映済み。OpenCode配布経路なし |
| c638240 | 対話・自律ループ分離、意図承認、手順のスキル委譲、プロンプト縮減 | Codexは旧長文。両対象へ意味保存とツール別適応が必要 |
| e7a338b | Stopテストゲートを信頼済みディレクトリ限定、依存自動導入禁止 | Claude専用。Codex指示の常時自動は実装と不一致 |
| fb31936 | 危険操作検出の空白・フラグ回避防止 | Claude専用。最終ルールを共用する |
| ac25276 | 危険操作検出のパス・エスケープ回避防止 | Claude専用。各ツールのask/deny契約へ適応する |
| 5b90099 | グローバルClaude設定とHook配線の管理 | CodexはRTKのみ。OpenCode設定なし。既存個人設定を保持する |
| 7adf51a | Windows jq由来CR除去 | Bash流用時に必要。同等のCRLFケースを検証する |
| 17175a6 | 実行ビット復元 | 共通資産反映済み。新規スクリプトでも保持 |
| aeeb22b | gitattributesとLF統一 | 共通資産反映済み。新規スクリプトでも保持 |
| 2726b1d | 正規化で失われた実行ビット復元 | 共通資産反映済み。新規スクリプトでも保持 |
| d9178dd | Bash位置・PATH区切りのOS依存修正 | 既存テスト反映済み。追加試験も踏襲 |
| c211fd2 | shutil.whichでBash解決 | 既存テスト反映済み。追加試験も踏襲 |
| d9993ee | Windows配置・移行の学び | 新規展開も配置先別検証とバックアップが必要 |
| d47475c | WSLの既存設定保持、部分マージの学び | 新規展開でも個人設定を丸ごと置換しない |
| 4cfcf78 | 古いWSL作業・CLAUDE縮減WIP保存、ログ整理 | WIPではなくマージ後HEADを採用 |
| 2ea532d | 未使用black削除、ruff統一 | 共通変更済み。独立したblack/isort導入は不要 |
| 3935278 | マージ | 独立展開対象なし。最終ツリーを確認 |
| b84e4bb | マージ | 独立展開対象なし。最終ツリーを確認 |

## 前史 / Earlier Origins

| コミット | 変更 | 必要対応 |
|---|---|---|
| 789fecd | Stopテストゲート新設 | Claude専用。対象のライフサイクル契約を確認する |
| f3a38f2 | コマンド事前Hookのstdin JSON修正 | 古い引数契約を再導入しない |
| 979800b | vibe-diff / test-requirements / 外部プラグイン導入スクリプト | スキルはClaude variantのみ。汎用手順を共有し、Claude外部プラグインの自動インストールを他ツールへコピーしない |
| 85a3962 | スキル発火・レビュー使い分け | Claude固有呼出しをツール別の実在能力へ写像 |
| aa82218 / cc72bcc | codex-implementとcodexプラグイン経由の委任 | ClaudeのCodex呼出しをCodex自己委任と混同しない |
| 54fe2e0 | スキル配布管理 | AGENTSと既定homesはCodex/Claudeのみ。OpenCode配布対応が必要 |

## 監査時点の文書・実装不一致 / Initial Discrepancies

1. `project-configs/.codex/AGENTS.md:714` はStop常時自動と記載するが、`project-configs/.codex/hooks.json` はRTK PreToolUseのみ。
2. 同AGENTSのvibe-diff/test-requirementsはClaude側にしか実体がない。Claude固有レビュー・委任呼出しも残る。
3. `docs/settings/codex-claude-setting-map.md:5-6` はClaudeのmodel/effort設定なしと記載するが、管理settingsにmodel/effortLevelが存在。Codexフックの説明も現行hooks.jsonと不一致。
4. `docs/settings/global-settings-migration-notes.md:119` はclaude-global-settingsをWindows専用とするが、設計図に通常targetもあり、LinkItemにOS除外はない。実装はWindows以外で通常targetを選ぶためWSL applyの対象となる。
5. グローバル指示のdocs/skills参照基準が他プロジェクトで不明確。管理元の実体基準を明示する。

## 実装後の対応 / Final Mapping

- 5原則・モード・意図承認・参照基準: Codex/OpenCodeのAGENTSへ反映。詳細なtasks形式はdocs/skills/project-records.mdへ移して参照。
- sfw・危険操作最終ルール: shared/hooks/agent_guard.pyから既存Claude正本を共用。Windows実行名・cmdラッパーも追加検証。
- Codex: hooks/guard.pyとhooks.jsonへPreToolUse/Stopを追加。ask未対応なので危険操作はdeny。RTK既存アダプターを保持。
- OpenCode 2: plugins/aicli-guardrailsのnative permission evaluateでask/deny、shell create.beforeで再検査とRTK。Stop同等は確認できず明示テスト。
- スキル: 配布先にOpenCodeを追加し、spec/feedback-loop/architect/commit-flow/skill-improve等と欠落していたvibe-diff/test-requirementsを展開。
- settings/hooks混在ファイル: 全体リンク対象から除外しCodex用部分マージを追加。個人情報・他Hookを保持。
- 改行: Python/JSONに加えてOpenCodeの.jsもLF対象。既存6件の実行ビット差分には触れていない。

## OpenCodeの実機との整合 / OpenCode Runtime Contract

旧ローカル@opencode-ai/plugin宣言は1.18.25、実機CLIは2.1.4で一致していなかった。
旧APIのtool.execute.beforeを採用せず、公式v2のdefault export id/setupと
ctx.permission.hook("evaluate") / ctx.shell.hook("create.before")へ合わせた。
依存追加なしのplugin directoryを隔離した2.1.4実機へ読み込ませ、active、
通常allow、危険ask、sfwなしdeny、シェル直前の実行停止を確認した。
Windowsホームへの31リンク配置とHookマージ、OpenCode live activeまで追加承認後に確認済み。Codex Hook信頼・guard有効化は別の明示承認待ち。WSL配置は未実施。

公式参照: [OpenCode 2 Server Plugins](https://opencode.ai/v2/docs/build/plugins/server/)、
[Plugin Discovery](https://opencode.ai/v2/docs/plugins/)、
[Instructions](https://opencode.ai/v2/docs/instructions/)、
[Skills](https://opencode.ai/v2/docs/skills/)、
[Codex Hooks](https://learn.chatgpt.com/docs/hooks)（2026-11-02確認）。
