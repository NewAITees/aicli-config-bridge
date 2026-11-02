# エージェント横断の設定方針 / Cross Agent Settings Policy

同じ運用意図をClaude Code・Codex・OpenCodeのネイティブ形式へ写像する。モデル・認証・プロバイダー・MCP・個別permissionsは移植対象と混同しない。

| 意図 | Claude Code | Codex | OpenCode |
|---|---|---|---|
| グローバル指示 | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` | `~/.config/opencode/AGENTS.md` |
| スキル | `~/.claude/skills/` | `~/.codex/skills/` | `~/.config/opencode/skills/` |
| 実行前 | settings.jsonのPreToolUse | hooks.jsonのPreToolUse、matcher Bash（exec_commandを含む） | v2のpermission evaluate / shell create.before |
| sfwなしの取得 | deny | deny | 例外で拒否 |
| 危険操作 | ask | ask未対応につきdeny | ネイティブpermission ask |
| テストゲート | Stop | Stop、失敗はdecision block | 完了前の明示CLI実行。自動Stopとは呼ばない |
| Hookの有効化 | 設定の部分マージ | 部分マージ後に/hooksで定義を確認・信頼 | 個別ローカルpluginファイルを配置 |

共通実装は `project-configs/shared/hooks/agent_guard.py`。sfwパーサーと危険操作ルールは既存Claude版を参照する。Codex/OpenCodeアダプターはリンクの実体から管理リポジトリを解決するため、単体コピーせず管理リンクを使い、リポジトリ全体を保持する。

## 個人設定の保持 / Preserve Local Settings

- `settings.json`、`hooks.json`、`opencode.jsonc` はプロジェクト・マシン固有設定と共有設定が混在する。ファイル全体を上書き・リンクしない。
- Claudeの管理settings.jsonとCodexの管理hooks.jsonはマージ元のテンプレート。`aicli-links.json` の全ファイルリンクから除外する。既にある配置は自動削除しない。
- 必要なHook登録だけを重複なく追加する。既存のdeny、他Hook、プラグイン、プロバイダーは保持する。変更前は元の内容・リンク先をバックアップする。
- `test_gate_trusted_dirs` はAgentごとにホーム側で管理し、Git管理しない。プロジェクトが自分を信頼できないようにする。各行は実在する絶対パス、完全一致とする。子フォルダを自動的に信頼しない。
- Windows/WSLは独立に検証する。Windowsの更新だけでWSLへ反映済みとは言わない。MCP等のOS依存パスをコピーしない。
- Hookファイルの書込みや登録だけで有効とは判定しない。Codexは非管理Hook定義の信頼が必要で、更新後は再確認対象となる。信頼を迂回する起動フラグを使わない。

## 検証 / Verification

stdin JSON、拒否出力、Stop失敗継続、未信頼時の未実行、依存非導入を個別に確かめる。実行前に元コマンドを検査し、RTKの最適化成功を安全検査の成功と混同しない。実際のエージェント上で拒否を確認していなければ、その範囲は未検証と報告する。

一次情報（2026-11-02確認）: [Codex Hooks](https://learn.chatgpt.com/docs/hooks)、[OpenCode Plugins](https://opencode.ai/v2/docs/build/plugins/server/)、[Rules](https://opencode.ai/v2/docs/instructions/)、[Skills](https://opencode.ai/v2/docs/skills/)。

テストの内部タイムアウトは120秒、Codex側のHook timeoutは130秒。タイムアウトで直下プロセスは停止するが、テストが起動した子孫プロセスの停止までは保証しない。
