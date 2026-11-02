# Claude変更のCodex・OpenCode横展開（2026-11-02）

リポジトリ内の実装と、Windowsホームへの31管理リンク・Codex Hookマージの適用は完了。31リンク・46ファイルのSHA-256一致と、既存14対象の退避を独立確認した。OpenCodeは稼働中サービスでactive。Codexは配置・読込まで完了し、3Hookの信頼と危険操作ガードの有効化が承認待ち。

対象リポジトリ: `C:\analysis2\aicli-config-bridge`。調査時HEAD: `d47475c`。
ユーザーの承認範囲: CLAUDE.mdだけでなく、直近の複数コミットの関連変更を洗い出してCodex・OpenCodeへ展開する。

## 確認した履歴

2026-10-01以降の22コミット（実変更20・マージ2）を全件確認し、必要な8月の前史も確認した。
コミットごとの表はリポジトリの `docs/settings/cross-agent-history-audit.md` に記録した。

| 変更のまとまり | 主なコミット | 今回の対応 |
|---|---|---|
| 5原則・意図承認・モード分離・指示の整理 | f55441c / c638240 / 4cfcf78 | Codex/OpenCodeのAGENTSへ反映。共通の詳細テンプレートは参照文書へ分離 |
| sfwの強制・解析回避の防止 | 3d799ca / 0bf4c2d / fd9b227 | Claudeの最終Pythonパーサーを共通ドライバーから再利用 |
| 危険操作の空白・フラグ・パス変種 | fb31936 / ac25276 | 既存ルールをPythonで読込。POSIX文字クラスを変換。Windowsの実行名・cmd経由も検証 |
| 信頼済みフォルダ限定のテストゲート | e7a338b（前史789fecd） | Codex Stopへ移植。OpenCodeは完了前の明示実行 |
| Hook実配線と個人設定保持 | 5b90099 / d9993ee / d47475c | Codex Hookの部分マージを実装。混在JSONの全体リンクを設計図から除外 |
| CRLF・Windowsパス・Bash解決 | 7adf51a / d9178dd / c211fd2 | 新ガードはjq/bashに依存しない。UTF-8実行とLFを明示 |
| 改行統一・実行ビット | aeeb22b / 17175a6 / 2726b1d | 新しい.jsもLF対象。作業前からある6件の実行ビット差分を保持 |
| スキル参照・配布 | 8f03c3d（前史54fe2e0 / 979800b / 85a3962） | OpenCode配布を追加。vibe-diff/test-requirementsの欠落を補完 |
| ruff統一 | 2ea532d | 共通変更済みと確認。別のblack導入は追加しない |
| マージ | 3935278 / b84e4bb | マージ後の最終ツリーを確認 |

## 実装したもの

| 領域 | 管理ファイル |
|---|---|
| Codexの最新指示 | `project-configs/.codex/AGENTS.md` |
| OpenCode 2の最新指示 | `project-configs/.config/opencode/AGENTS.md` |
| sfw・危険操作・テストの共通実装 | `project-configs/shared/hooks/agent_guard.py` |
| Codex出力形式への変換 | `project-configs/.codex/hooks/guard.py` |
| Codex PreToolUse/Stop配線 | `project-configs/.codex/hooks.json` |
| OpenCode 2ネイティブプラグイン | `project-configs/.config/opencode/plugins/aicli-guardrails/` |
| 既存Codex Hookを保持したマージ | `docs/settings/merge-codex-hooks.py` |
| OpenCodeのスキル配布 | `src/aicli_config_bridge/skills.py` / `project-configs/skills/opencode/` |
| 欠落スキルの補完 | `project-configs/skills/{codex,opencode}/{vibe-diff,test-requirements}/` |
| 共通方針・差異・参照基準 | `docs/settings/cross-agent-settings-policy.md` |
| tasksの詳細形式 | `docs/skills/project-records.md` |

Windowsから読めない既存スキルリンクは、状態表示を落とさず `inaccessible` と報告する。`skills apply` はそのリンクを勝手に上書きせず停止する。

## ツール固有の差

- CodexのPreToolUseはdenyに対応するがaskは未対応。askを返すとエラー後に実行が続くため、危険操作の共通ask判定をdenyに変換する。別コマンドや無効化で迂回しない。
- CodexにはStopがあり、失敗時は `decision: block` で継続を要求する。テストはホーム側の信頼リストと絶対パスが完全一致するプロジェクトだけ。未実行は合格と報告しない。
- Codexの非管理Hookは現在の定義を `/hooks` で確認・信頼するまで実行されない。配置と有効化は別。
- OpenCode実機は2.1.4。旧ローカルプラグイン型1.18.25を流用せず、v2のpermission evaluateでask/deny、shell create.beforeで再検査とRTKを実装した。
- OpenCodeにStop相当の完了阻止契約は確認できない。session.idleを代用せず、完了前に共通テストドライバーを明示実行する。
- 既存のRTKアダプターは保持。Codexの複数command hookは並行実行されるので、配列順だけで直列実行を保証したとはしない。

## 横展開時点の検証結果（レビュー前の履歴）

| 確認 | 結果 |
|---|---|
| Windowsの新規・関連テストと既存sfw | 180 passed |
| WSLでWindows側の変更済みチェックアウトを全体試験 | 229 passed / 21 skipped |
| Windows全体（この実行だけGit Bash・UTF-8を指定） | 246 passed / 4 failed |
| ruff check | 通過 |
| ruff formatの対象19ファイル | 通過 |
| mypy | 18 source files通過 |
| OpenCodeプラグインのNode構文確認 | 通過 |
| 変更した12スキルの形式検証 | 通過 |
| git diff --check | 通過 |
| 独立した敵対的入力レビュー | 実施。Windows大文字実行名、exe/cmd、引用パス、cmd /c等の漏れを再現して修正 |

WSLの21 skippedはNodeが存在しない環境でのOpenCodeプラグイン試験。該当21件はWindowsで実行して通過した。

OpenCode 2.1.4の隔離実機でプラグインactive、通常allow、sfwなしdeny、危険askを確認した。実シェル作成前にもsfwで停止し、無害なnpmスタブの実行マーカーが作られないことを確認。外部モデル・実npm導入・個人設定の変更は行っていない。
証拠: このチャットの作業フォルダ `work/opencode-runtime/native-smoke.json`。

Windowsの既存4失敗は以下。変更前の標準環境では48件失敗し、Bash探索順と文字コードを実行内で整えると4件まで絞れた。テストの削除・緩和は行っていない。

1. `test_trusted_project_runs_frozen_without_sync`: Bash側へ渡すWindowsの信頼パスが一致せず、実行記録が作られない。
2. `test_failing_tests_block_completion`: 同じ信頼パス問題でテストが実行されず、想定の失敗終了にならない。
3. `test_windows_node_adapter_adds_codex_allow_decision`: シェルスクリプトをfakeの`.exe`として作り、Windows Nodeから実行できない。
4. `test_resolve_path_userprofile`: WindowsPathの結果にPOSIXの区切り文字列を期待する。

横展開作業時点ではテスト自体を変更せず、全テスト通過とは報告していない。以降の開発レビューでWindows fixtureを修正した結果は下記に分けて記録する。pushは未実施。pre-commitの登録は横展開時点で実施済み。

## 見つかった文書と実装の食い違い

| 食い違い | 対応 |
|---|---|
| Codex指示はStopが常時有効と記載、実配線はRTKだけ | PreToolUse/Stopテンプレートとアダプターを追加し、信頼・配置未完了を明示 |
| Codex指示のvibe-diff/test-requirementsの実体がClaudeにしかない | Codex/OpenCode variantを追加 |
| Claude固有のレビュー・委任コマンドがCodex指示に残存 | 実在能力を選ぶネイティブの運用へ置換 |
| 設定対応表がClaudeのmodel/effort設定なし、Codex Hookは薄いと記載 | model/effortLevelと現行PreToolUse/Stopの対応へ修正 |
| Claude settingsリンクはWindows限定という説明だが設計図はWSLも対象 | 混在設定の全体リンクを除外し、部分マージ方針へ修正 |
| グローバル指示の相対参照基準が不明 | 指示・スキルのリンク実体から管理元を解決するルールを追加 |
| OpenCodeのローカル型宣言が実機の版と不一致 | v2公式仕様と隔離実機で確認 |
| 管理元更新だけでWindowsへ反映されるとは限らない | Codexの現リンクはWSLの別チェックアウトを指していると確認。今回の適用でWindows管理元へリンクを切り替え済み |

既存の依存範囲指定（`>=`）とexact固定規約の不一致は以前からtodoにあり、依存更新は今回の範囲に含めていない。

## 残っている適用と復元

ホーム内のリンク差し替えは当初自動承認レビューに止められたが、ユーザーの追加承認「OK」後、固定31対象を適用した。Codex hooks.jsonも元内容と旧リンク情報を保存し、通常JSONへ部分マージした。旧WSLリンク先は変更していない。

正式なCodex /hooks画面からの信頼操作は、別の自動承認レビューで停止された。「配置・レビューの承認はあるが、Hookを信頼して継続的な実行権限を与える明示承認がない」という理由。迂回せず画面を閉じた。

今回適用したWindows対象は合計31管理リンクとCodexのHook部分マージ。

- Codex: AGENTS、共通guardアダプター、既存RTKアダプター2ファイル、管理スキル14件。
- OpenCode: AGENTS、v2プラグイン1ディレクトリ、管理スキル11件。
- Codexのhooks.json: 他Hook・個人設定を保持して管理Hook3件を部分マージ。
- `.system`、プラグインキャッシュ、Claudeの既存スキル・設定、認証、モデル、プロバイダー、MCPは対象外。

既存の14リンクは削除せず、対象親の `.aicli-backup/` へ葉だけを退避してから新しい管理リンクを作成した。inode・mtime・sizeの保持を独立確認済み。Codex hooksは元内容とリンク情報を保存してから配置先だけを置換し、元のリンク先は変更していない。

配置先アダプターの4確認（通常入力・sfwなし取得・危険操作・未信頼プロジェクトStop）が通過。Codex Hookマージの再確認はchanged=falseで、重複・再変更なし。OpenCodeのサービス再読込後にプラグインactiveを確認。

Codex正式hooks/list APIの現在状態:

| Hook | 読込 | 有効フラグ | 信頼 |
|---|---|---|---|
| 危険操作・sfwガード PreToolUse | 認識済み | false | modified |
| RTK PreToolUse | 認識済み | true | untrusted |
| テストゲート Stop | 認識済み | true | untrusted |

したがってCodexの機械的な保護が有効になったとは報告しない。次に必要なのは、今回の3定義を正式 /hooks で信頼し、ガードも有効にする明示承認。

復元は保存した元リンク／元JSONを対象へ戻す。管理元の変更前ファイルもこのチャットの `work/before-main/` と `work/before-final/` に保存している。

WSL側ホームへの適用は未実施。WSLでテストしたこととWSLへの配置完了は区別する。CodexのHook信頼登録・ガード有効化と、その後のCodex実行経路での阻止確認が残っている。

## 一次情報

- [Codex Hooks](https://learn.chatgpt.com/docs/hooks)
- [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [OpenCode 2 Server Plugins](https://opencode.ai/v2/docs/build/plugins/server/)
- [OpenCode 2 Plugin Discovery](https://opencode.ai/v2/docs/plugins/)
- [OpenCode 2 Instructions](https://opencode.ai/v2/docs/instructions/)
- [OpenCode 2 Skills](https://opencode.ai/v2/docs/skills/)

公式仕様はAPI契約の根拠として参照し、ユーザーからの指示とは分けて扱った。実行未確認の箇所は上記の通り明示した。

## 開発レビュー後の結果（2026-11-02）

独立レビューで個人Hookの誤削除とWindows削除エイリアス漏れを修正し、Windowsテストのfixtureを整備した。全277テストが警告なしで通過。lint・整形・型・構文も通過した。段階的なローカルコミットを実施し、pushや個人設定の再配置は行っていない。詳細は [開発レビュー記録](development-review-2026-11-02.md) を参照。上記の配置・Hook信頼状態は横展開時点の記録であり、今回再検証していない。
