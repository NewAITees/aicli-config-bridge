# RTK Hook 共通仕様 / RTK Hook Common Specification

## 目的 / Purpose

RTK（Rust Token Killer）は、AIエージェントが実行するシェルコマンドを透過的に書き換え、冗長な出力を圧縮する。
エージェントが毎回RTKを思い出す運用ではなく、`PreToolUse` Hookによって機械的に適用する。

## 管理構造 / Managed Structure

```text
aicli-config-bridge
├─ project-configs/.codex/hooks.json
│  └─ Codex PreToolUse Hook
├─ project-configs/.codex/hooks/rtk_pre_tool_use.py
│  └─ WSL Codex: RTKのClaude形式をCodex形式へ変換
├─ project-configs/.codex/hooks/rtk_pre_tool_use.mjs
│  └─ Windows Codex: RTKのClaude形式をCodex形式へ変換
└─ aicli-links.json
   └─ ~/.codex/ への配置を追跡

WSLユーザー環境
├─ ~/.cargo/bin/rtk
│  └─ Linux版 RTK 0.42.4
├─ ~/.local/bin/rtk
│  └─ Linux版へのリンク
├─ ~/.local/bin/rtk.windows-backup
│  └─ 以前のWindows版へのリンク（復旧用）
└─ ~/.claude/settings.json
   └─ Claude PreToolUse Hook

Windowsユーザー環境
├─ C:\Users\perso\.local\bin\rtk.exe
├─ C:\Users\perso\.codex\hooks.json
├─ C:\Users\perso\.codex\hooks\rtk_pre_tool_use.mjs
└─ C:\Users\perso\.claude\settings.json
   └─ Claude PreToolUse Hook
```

## エージェント別動作 / Agent-specific Behavior

### Codex

Codexは`updatedInput`と同時に`permissionDecision: allow`を要求する。
WSLの`rtk_pre_tool_use.py`とWindowsの`rtk_pre_tool_use.mjs`は、`rtk hook claude`の結果にこのフィールドだけを追加し、コマンド内容やRTKの判断は変更しない。
`hooks.json`は`command`でWSL用Pythonアダプター、`commandWindows`でWindows用Nodeアダプターを選択する。

### Claude

WSL・Windowsともに、Claudeは`rtk hook claude`を直接`PreToolUse`へ登録する。

## 利用規則 / Usage Rules

- エージェントは通常のシェルコマンドを発行する。手動で`rtk`を付ける必要はない。
- 既に`rtk`が付いたコマンドはHookで再変換しない。
- RTKが未導入または失敗した場合、Codexアダプターは元のコマンドを妨げず終了する。
- プロジェクト固有フィルターは、内容を確認して`rtk trust`するまで適用しない。

## 確認 / Verification

```bash
rtk --version
rtk gain
uv run aicli-config-bridge status --json
```

Codexでは新規セッション開始時に`/hooks`を開き、Hook定義を確認・信頼する。

WindowsネイティブではPowerShellから次を確認する。

```powershell
rtk.exe --version
Get-Content "$env:USERPROFILE\.codex\hooks.json" | ConvertFrom-Json
node --check "$env:USERPROFILE\.codex\hooks\rtk_pre_tool_use.mjs"
```

## 復旧 / Rollback

1. Codexでは`~/.codex/hooks.json`を無効化または管理リンクを解除する。
2. Claudeでは`~/.claude/settings.json`からRTKの`PreToolUse` Hookを外す。
3. Linux版へのリンクを外し、`~/.local/bin/rtk.windows-backup`を`~/.local/bin/rtk`へ戻す。

復旧時も、現在のファイルとリンク先を確認してから操作する。
