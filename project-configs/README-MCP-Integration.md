# MCP設定統合ガイド

## 概要
このディレクトリにはMCP（Model Context Protocol）サーバーの統合設定が含まれています。Claude DesktopとClaude Codeの両方で同じMCP設定を使用できるようにシンボリックリンクで管理されています。

## ファイル構成

### `mcp-servers-config.json`
- **目的**: 共有MCP設定ファイル
- **内容**: すべてのMCPサーバーの設定
- **使用場所**: Claude Desktop、Claude Code、その他のツール

### シンボリックリンク構成

```bash
# Claude Desktop設定
~/.config/Claude/claude_desktop_config.json -> ./mcp-servers-config.json

# Claude Code設定  
~/.claude/settings.json (mcpServers セクション同期済み)
```

## 設定されているMCPサーバー

### 1. filesystem
- **機能**: ファイルシステムアクセス
- **アクセス可能ディレクトリ**: Documents, Desktop, analysis

### 2. memory
- **機能**: メモリ機能
- **用途**: セッション間でのデータ保持

### 3. fetch
- **機能**: Webフェッチ機能
- **用途**: HTTP/HTTPS リクエスト

### 4. github
- **機能**: GitHub統合
- **要件**: GITHUB_PERSONAL_ACCESS_TOKEN環境変数

### 5. ollama-mcp-server
- **機能**: LLM統合
- **モデル**: deepseek-r1:14b

## 使用方法

### Claude Desktop
1. Claude Desktopを再起動
2. 右下にハンマーアイコンまたはツールアイコンが表示されることを確認

### Claude Code
1. 新しいClaude Codeセッションを開始
2. `claude mcp list` でサーバー一覧を確認

## 設定の更新

`mcp-servers-config.json` を編集すると、シンボリックリンクを通じて両方のツールに自動的に反映されます。

## 環境変数設定

GitHub統合を使用する場合：
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
```

## トラブルシューティング

### MCP接続エラー
1. Node.js/npm がインストールされていることを確認
2. 必要な環境変数が設定されていることを確認
3. ツールを完全に再起動

### シンボリックリンク問題
```bash
# リンクの再作成
ln -sf /home/perso/analysis/aicli-config-bridge/project-configs/mcp-servers-config.json ~/.config/Claude/claude_desktop_config.json
```