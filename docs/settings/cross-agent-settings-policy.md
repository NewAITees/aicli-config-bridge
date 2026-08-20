# Cross Agent Settings Policy

## Goal

`codex` と `claude` の設定を同一ファイルに統一するのではなく、同じ運用意図を別形式へ写像できる状態にする。

## Shared Intent

両環境で共通化したい意図:
- 危険コマンドを制限する
- 必要なプロジェクトだけ trusted にする
- ブラウザ操作や MCP を必要最小限で有効化する
- ローカル補助設定を本体設定から分離する

## Mapping Areas

### Permissions

- `claude`: `settings.json` / `settings.local.json` の `permissions`
- `codex`: 実行環境側の sandbox 設定 + trust 設定 + 承認フロー

### Hooks / Lifecycle

- `claude`: `hooks.SessionStart`, `PreToolUse`, `Stop`
- `codex`: 明示的な hook 設定よりも、スキルと実行ポリシーで代替される箇所が多い

### Plugins / MCP

- `claude`: `enabledPlugins`, `extraKnownMarketplaces`, `mcpServers`
- `codex`: `plugins.*`, `mcp_servers.*`

### Project Trust

- `claude`: 明示的な project trust というより、permissions と local override の組み合わせ
- `codex`: `projects."<path>".trust_level`

## Policy Rules

1. まず「許可したい理由」を決め、その後に環境ごとの書式へ落とす
2. ローカル一時調整は `claude/settings.local.json` のような override 層へ分離する
3. `codex` 側では永続 trust と一時承認を混同しない
4. Playwright や memory 系の設定は、スキル本文ではなく設定ポリシーか reference に集約する

## Current Gaps

- `claude` は hook 駆動が強い
- `codex` は project trust と機能フラグが強い
- 同じ意図でも設定の置き場所が違うため、対応表が必要

## WSL / Windows Policy

- Claudeは同一のWindows側設定をWSLから参照するため、`/mnt/c/Users/perso/.claude/` と `C:\Users\perso\.claude\` の対応を併記する。
- CodexはWSLとWindowsで `config.toml` が分かれるため、各環境のネイティブパスで同じtrust意図を記述する。
- WindowsからWSLのリポジトリをtrustする場合は `\\wsl.localhost\Ubuntu\...` を使い、WSLからWindows側の作業領域をtrustする場合は `/mnt/c/...` を使う。
- MCPの実行ファイルやランナーはOS依存のため、同じ設定をコピーせず、環境ごとの実体パスを維持する。
