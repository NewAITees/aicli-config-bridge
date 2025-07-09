# aicli-config-bridge 使用ガイド

## 概要

`aicli-config-bridge` は AI CLI ツールの設定を統合管理するためのツールです。Claude Code や Gemini CLI などの設定をプロジェクトベースで管理し、シンボリックリンクを使って実際の設定場所に適用できます。

## インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd aicli-config-bridge

# 依存関係をインストール
uv sync

# 開発モードでインストール
uv pip install -e .
```

## 基本的な使用方法

### 1. プロジェクトの初期化

```bash
# 新しいプロジェクトを作成
uv run aicli-config-bridge init my-ai-project

# 既存ディレクトリで初期化
cd my-existing-project
uv run aicli-config-bridge init
```

### 2. 既存設定の検出

```bash
# システムにある AI CLI 設定を検出
uv run aicli-config-bridge detect-configs
```

出力例：
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                   検出された設定                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ツール      │ 設定ファイル                        │ 状態        │
├─────────────┼─────────────────────────────────────┼─────────────┤
│ claude-code │ /home/user/.claude/settings.json   │ ✅ 検出     │
│ gemini-cli  │ /home/user/.gemini/settings.json   │ ✅ 検出     │
└─────────────┴─────────────────────────────────────┴─────────────┘
```

### 3. 設定のインポート

```bash
# 特定のツールの設定をインポート
uv run aicli-config-bridge import-config --tool claude-code

# インタラクティブでツールを選択
uv run aicli-config-bridge import-config
```

### 4. 設定のリンク

```bash
# 特定のツールの設定をリンク
uv run aicli-config-bridge link --tool claude-code

# すべての設定をリンク
uv run aicli-config-bridge link-all
```

### 5. リンク状態の確認

```bash
uv run aicli-config-bridge status
```

出力例：
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                  設定リンク状態                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ツール      │ ステータス    │ 設定ファイル                │
├─────────────┼───────────────┼─────────────────────────────┤
│ claude-code │ ✅ リンク済み │ /home/user/.claude/settings.json │
│ gemini-cli  │ ❌ 未リンク   │ /home/user/.gemini/settings.json │
└─────────────┴───────────────┴─────────────────────────────┘
```

### 6. 設定の検証

```bash
uv run aicli-config-bridge validate
```

### 7. リンクの解除

```bash
# 特定のツールのリンクを解除
uv run aicli-config-bridge unlink --tool claude-code
```

## コンテキストファイルの管理

### CLAUDE.md / GEMINI.md のインポート

```bash
# Claude Code の CLAUDE.md をインポート
uv run aicli-config-bridge import-context --tool claude-code

# Gemini CLI の GEMINI.md をインポート
uv run aicli-config-bridge import-context --tool gemini-cli
```

### コンテキストファイルのリンク

```bash
# Claude Code の CLAUDE.md をリンク
uv run aicli-config-bridge link-context --tool claude-code
```

### デフォルトコンテキストファイルの作成

```bash
# デフォルトの CLAUDE.md を作成
uv run aicli-config-bridge create-context --tool claude-code
```

## サポートされるツール

### Claude Code
- **設定ファイル**: `~/.claude/settings.json`
- **プロジェクト設定**: `.claude/settings.json`, `.claude/settings.local.json`
- **コンテキストファイル**: `CLAUDE.md`

### Gemini CLI
- **設定ファイル**: `~/.gemini/settings.json`
- **プロジェクト設定**: `.gemini/settings.json`
- **コンテキストファイル**: `GEMINI.md`

## プラットフォーム対応

### Linux / macOS / WSL
- シンボリックリンクを使用
- 完全な双方向同期

### Windows (ネイティブ)
- ファイルコピーを使用
- 管理者権限不要

## 設定ファイルの構造

### プロジェクト設定ファイル (`config.json`)

```json
{
  "name": "my-project",
  "description": "プロジェクトの説明",
  "tools": {
    "claude-code": {
      "system_config_path": "/home/user/.claude/settings.json",
      "project_config_path": "./configs/claude-settings.json",
      "system_context_path": "/home/user/CLAUDE.md",
      "project_context_path": "./CLAUDE.md",
      "is_enabled": true
    },
    "gemini-cli": {
      "system_config_path": "/home/user/.gemini/settings.json", 
      "project_config_path": "./configs/gemini-settings.json",
      "system_context_path": "/home/user/GEMINI.md",
      "project_context_path": "./GEMINI.md",
      "is_enabled": true
    }
  }
}
```

### 環境変数の使用

設定ファイルでは環境変数を使用できます：

```json
{
  "api_key": "${CLAUDE_API_KEY}",
  "workspace": "${WORKSPACE_PATH:-./workspace}",
  "debug": "${DEBUG:-false}"
}
```

## トラブルシューティング

### よくある問題

1. **権限エラー**
   ```bash
   # WSL で実行を推奨
   # Windows の場合は管理者権限で実行
   ```

2. **設定ファイルが見つからない**
   ```bash
   # 設定ファイルの場所を確認
   uv run aicli-config-bridge detect-configs
   ```

3. **リンクが壊れている**
   ```bash
   # 設定を検証
   uv run aicli-config-bridge validate
   
   # リンクを再作成
   uv run aicli-config-bridge unlink --tool claude-code
   uv run aicli-config-bridge link --tool claude-code
   ```

### デバッグ

```bash
# 詳細なログを表示
export DEBUG=1
uv run aicli-config-bridge status
```

## 高度な使用方法

### 複数のプロジェクトでの使用

```bash
# プロジェクトA
cd /path/to/project-a
uv run aicli-config-bridge init project-a
uv run aicli-config-bridge import-config --tool claude-code
uv run aicli-config-bridge link --tool claude-code

# プロジェクトB
cd /path/to/project-b  
uv run aicli-config-bridge init project-b
uv run aicli-config-bridge import-config --tool claude-code
uv run aicli-config-bridge link --tool claude-code
```

### バックアップと復元

```bash
# 設定をバックアップ（自動で実行）
uv run aicli-config-bridge link --tool claude-code

# バックアップから復元
uv run aicli-config-bridge unlink --tool claude-code
```

## 開発者向け情報

### 新しいツールの追加

1. `src/aicli_config_bridge/tools/` にハンドラーを追加
2. `config/models.py` でツールタイプを定義
3. テストを作成

### 貢献

```bash
# テストを実行
uv run pytest

# コード品質チェック
uv run ruff check .
uv run ruff format .
uv run mypy .
```