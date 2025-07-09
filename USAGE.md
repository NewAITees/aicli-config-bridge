# aicli-config-bridge 使用ガイド

## 概要

`aicli-config-bridge` は AI CLI ツールの設定を統合管理するためのツールです。Claude Code や Gemini CLI などの設定ファイル（CLAUDE.md、GEMINI.md、settings.json等）をシンボリックリンクで管理し、ユーザーが普段使い慣れた場所から編集できるようにします。

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

### 1. ユーザー設定ファイルのリンク作成

```bash
# CLAUDE.md をリンク
uv run aicli-config-bridge link-user claude-md

# GEMINI.md をリンク  
uv run aicli-config-bridge link-user gemini-md

# Claude Code の settings.json をリンク
uv run aicli-config-bridge link-user claude-settings

# Gemini CLI の settings.json をリンク
uv run aicli-config-bridge link-user gemini-settings
```

### 2. リンク状態の確認

```bash
uv run aicli-config-bridge status-user
```

出力例：
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                ユーザー設定リンク状態                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 対象        │ ユーザーパス          │ プロジェクトパス      │ ステータス │
├─────────────┼─────────────────────┼─────────────────────┼────────────┤
│ claude-md   │ /home/user/CLAUDE.md │ project-configs/...  │ ✅ 正常    │
│ gemini-md   │ /home/user/GEMINI.md │ project-configs/...  │ ✅ 正常    │
└─────────────┴─────────────────────┴─────────────────────┴────────────┘
```

### 3. ファイルの編集

```bash
# ユーザーホームから編集（普通の編集方法）
vim ~/CLAUDE.md
code ~/GEMINI.md
vim ~/.claude/settings.json

# プロジェクトディレクトリから編集（どちらでも同じファイル）
vim project-configs/CLAUDE.md
code project-configs/GEMINI.md
vim project-configs/claude_settings.json
```

### 4. リンクの解除

```bash
# 特定のリンクを解除
uv run aicli-config-bridge unlink-user claude-md
uv run aicli-config-bridge unlink-user gemini-md
```

## シンボリックリンクの仕組み

### ファイル構成

**リンク作成後の構成:**
```
ユーザーホーム:
~/CLAUDE.md                     # 実体ファイル（編集対象）
~/GEMINI.md                     # 実体ファイル（編集対象）
~/.claude/settings.json         # 実体ファイル（編集対象）
~/.gemini/settings.json         # 実体ファイル（編集対象）

プロジェクトディレクトリ:
project-configs/
├── CLAUDE.md → ~/CLAUDE.md               # シンボリックリンク
├── GEMINI.md → ~/GEMINI.md               # シンボリックリンク
├── claude_settings.json → ~/.claude/settings.json  # シンボリックリンク
└── gemini_settings.json → ~/.gemini/settings.json  # シンボリックリンク
```

### 双方向編集

シンボリックリンクのため、どちらの場所からでも同じファイルを編集できます：

```bash
# これらはすべて同じファイルを編集
vim ~/CLAUDE.md
vim project-configs/CLAUDE.md
code ~/CLAUDE.md
code project-configs/CLAUDE.md
```

### 利点

1. **使い慣れた場所での編集**: `~/CLAUDE.md` で普通にファイル編集
2. **プロジェクト内からもアクセス**: `project-configs/CLAUDE.md` からも編集可能
3. **自動同期**: 編集内容は即座に両方の場所に反映
4. **バージョン管理**: プロジェクトディレクトリをGitで管理可能

## サポートされるツール

### Claude Code
- **コンテキストファイル**: `~/CLAUDE.md` → `project-configs/CLAUDE.md`
- **設定ファイル**: `~/.claude/settings.json` → `project-configs/claude_settings.json`

### Gemini CLI
- **コンテキストファイル**: `~/GEMINI.md` → `project-configs/GEMINI.md`
- **設定ファイル**: `~/.gemini/settings.json` → `project-configs/gemini_settings.json`

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