# Codex / Claude Setting Map

| Intent | Codex | Claude | Notes |
|---|---|---|---|
| モデル選択 | `config.toml` の `model` | `settings.json` の `model` | 管理面の責務が異なる |
| 推論強度 | `model_reasoning_effort` | `effortLevel` | モデルごとの対応値を別々に確認する |
| プロジェクト信頼 | `projects."<path>".trust_level` | `settings.local.json` の追加許可で近似 | 完全対応ではない |
| 追加書込先 | `sandbox.writable_roots` | `permissions.additionalDirectories` | どちらもローカル資産連携用 |
| プラグイン有効化 | `plugins."<name>".enabled` | `enabledPlugins` | 形式のみ異なる |
| MCP 設定 | `mcp_servers.<name>` | `mcpServers` | 名前空間は違うが概念は同じ |
| UI 表示設定 | `tui.*` | `theme`, `tui`, `statusLine` | Claude の方が UI 設定が多い |
| フック | `hooks.json` / `config.toml`のhooks | `hooks.*` | PreToolUse/Stopあり。askの対応は異なる |
| 通知・移行案内 | `notice.*` | なし | Codex 側特有 |

## Recommended Operating Model

1. 共通意図は `cross-agent-settings-policy.md` に書く
2. 具体値は各環境のネイティブ設定へ記述する
3. 差分が生じたら、まず「意図差」か「表現差」かを判定する

OpenCodeを含む現在の配置・ガードの対応は [横断方針](cross-agent-settings-policy.md) を参照。
