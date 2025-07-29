# Configuration Sync Scripts

このディレクトリにはAI CLI設定の同期とリンク管理用のスクリプトが含まれています。

## sync_config_links.py

クロスプラットフォーム対応の設定ファイル同期スクリプト。

### 機能

- **環境自動検出**: OS、WSL、ファイルシステムの制限を自動判定
- **リンクタイプ自動選択**: シンボリックリンク → ハードリンク → ファイルコピーの順で最適な方法を選択
- **設定ファイル管理**: Claude Desktop、Claude Code、Gemini CLIの設定を統合管理

### 使用方法

```bash
# 現在の設定状況を確認
uv run python scripts/sync_config_links.py --status

# ドライラン（実際の変更は行わない）
uv run python scripts/sync_config_links.py --dry-run

# 設定を同期実行
uv run python scripts/sync_config_links.py

# 特定のリンクタイプを指定
uv run python scripts/sync_config_links.py --link-type symlink
uv run python scripts/sync_config_links.py --link-type hardlink  
uv run python scripts/sync_config_links.py --link-type copy
```

### 対応プラットフォーム

- **Linux** (標準 + WSL)
- **macOS** 
- **Windows**

### 設定ファイルマッピング

| 設定 | ソース | ターゲット |
|------|--------|------------|
| Claude Desktop | `project-configs/mcp-servers-config.json` | `~/.config/Claude/claude_desktop_config.json` (Linux)<br>`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)<br>`%APPDATA%\Claude\claude_desktop_config.json` (Windows) |
| Claude Code | `project-configs/claude-settings-actual.json` | `~/.claude/settings.json` |
| Gemini CLI | `project-configs/gemini-settings-actual.json` | `~/.gemini/settings.json` |
| Context Files | `~/CLAUDE.md` | `project-configs/CLAUDE.md` |

### 環境制限対応

スクリプトは以下の環境制限に自動対応します：

1. **シンボリックリンク不可** → ハードリンクまたはコピーに自動切り替え
2. **ハードリンク不可**（異なるファイルシステム間） → コピーに自動切り替え  
3. **権限不足** → エラーメッセージと代替案を提示

### 出力例

```json
{
  "claude_desktop": {
    "source_exists": true,
    "targets": {
      "/home/user/.config/Claude/claude_desktop_config.json": {
        "exists": true,
        "is_symlink": true,
        "is_hardlink": false,
        "points_to_correct_source": true
      }
    }
  }
}
```

## トラブルシューティング

### 権限エラー
```bash
# 管理者権限で実行（Windows）
runas /user:Administrator "uv run python scripts/sync_config_links.py"

# sudoで実行（Linux/macOS、通常は不要）
sudo uv run python scripts/sync_config_links.py
```

### ファイルシステム制限
```bash
# コピーモードを強制使用
uv run python scripts/sync_config_links.py --link-type copy
```

### デバッグ情報
```bash
# 詳細な状況確認
uv run python scripts/sync_config_links.py --status | jq '.'
```