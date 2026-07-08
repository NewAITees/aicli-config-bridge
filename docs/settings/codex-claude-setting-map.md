# Codex / Claude Setting Map

| Intent | Codex | Claude | Notes |
|---|---|---|---|
| モデル選択 | `config.toml` の `model` | 該当設定なし、アプリ側管理が中心 | 管理面の責務が異なる |
| 推論強度 | `model_reasoning_effort` | 該当設定なし | Claude 側はスキル・運用で補う |
| プロジェクト信頼 | `projects."<path>".trust_level` | `settings.local.json` の追加許可で近似 | 完全対応ではない |
| 追加書込先 | `sandbox.writable_roots` | `permissions.additionalDirectories` | どちらもローカル資産連携用 |
| プラグイン有効化 | `plugins."<name>".enabled` | `enabledPlugins` | 形式のみ異なる |
| MCP 設定 | `mcp_servers.<name>` | `mcpServers` | 名前空間は違うが概念は同じ |
| UI 表示設定 | `tui.*` | `theme`, `tui`, `statusLine` | Claude の方が UI 設定が多い |
| フック | 直接設定は薄い | `hooks.*` | Claude 側特有の差分 |
| 通知・移行案内 | `notice.*` | なし | Codex 側特有 |

## Recommended Operating Model

1. 共通意図は `cross-agent-settings-policy.md` に書く
2. 具体値は各環境のネイティブ設定へ記述する
3. 差分が生じたら、まず「意図差」か「表現差」かを判定する
