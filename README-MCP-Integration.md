# MCP設定統合ガイド

このドキュメントでは、Claude CodeとClaude DesktopでMCP設定を共有する方法について説明します。

## 概要

Claude CodeとClaude Desktopは異なる設定ファイル形式を使用していますが、シンボリックリンクを使用して設定を統合できます。

## 設定ファイルの場所

### Claude Code
- `~/.claude/settings.json` - ユーザー設定（hooks、permissions、mcpServers含む）
- `~/.claude.json` - MCPサーバー専用設定（推奨）
- `.claude/settings.local.json` - プロジェクト固有設定
- `.mcp.json` - プロジェクトスコープのMCPサーバー

### Claude Desktop
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: Claude Desktopは通常利用不可

## 統合方法

### 方法1: 共通MCPファイルの作成

1. プロジェクト内に共通のMCP設定ファイルを作成
```bash
# プロジェクト内に作成
touch project-configs/mcp-shared-config.json
```

2. Claude Code用のシンボリックリンク
```bash
# Claude Codeが参照するMCP設定
ln -s /path/to/project/project-configs/mcp-shared-config.json ~/.claude.json
```

3. Claude Desktop用のシンボリックリンク
```bash
# Claude Desktop用（macOS）
ln -s /path/to/project/project-configs/mcp-shared-config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 方法2: settings.jsonへのMCP統合

Claude Codeの`~/.claude/settings.json`にMCP設定を直接含める場合：

```json
{
  "model": "sonnet",
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/Documents"]
    }
  },
  "hooks": {
    // 既存のhooks設定
  },
  "permissions": {
    // 既存のpermissions設定
  }
}
```

## 推奨設定

### 共通MCP設定例

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${HOME}/Documents", "${HOME}/Desktop"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "environment": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## 環境変数の使用

両方のクライアントで環境変数を使用できます：
- `${HOME}` - ホームディレクトリ
- `${GITHUB_TOKEN}` - GitHubアクセストークン
- その他のカスタム環境変数

## トラブルシューティング

### Claude Desktopで設定が反映されない
1. Claude Desktopを完全に再起動
2. 設定ファイルのJSON構文を確認
3. ファイルパーミッションを確認

### シンボリックリンクが機能しない
1. リンク先ファイルが存在することを確認
2. 絶対パスを使用
3. ファイルパーミッションを確認

### 環境変数が展開されない
1. 環境変数が正しく設定されていることを確認
2. シェルを再起動
3. アプリケーションを再起動

## 注意事項

- Claude Desktopの設定変更後は必ず再起動が必要
- プロジェクトスコープ設定（`.mcp.json`）はバージョン管理に含めることを推奨
- 機密情報（APIキーなど）は環境変数を使用