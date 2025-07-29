# CLAUDE.md

このファイルは Claude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

`aicli-config-bridge` は、シンボリックリンクを通じて AI CLI ツールの設定を管理する Python CLI ツールです。Claude Code や Gemini CLI などのツール用の集中設定管理を提供し、設定をバージョン管理し、開発環境間で共有できます。

## 開発環境セットアップ

このプロジェクトは `uv` をパッケージマネージャーとして使用する現代的な Python ツールチェーンを使用しています。

### 初期セットアップコマンド

```bash
# 依存関係をインストール
uv sync

# 開発モードでパッケージをインストール
uv pip install -e .

# プリコミットフックをセットアップ
uv run pre-commit install
```

### よく使用する開発コマンド

```bash
# アプリケーションを実行
uv run aicli-config-bridge --help

# テストを実行
uv run pytest
uv run pytest --cov=aicli_config_bridge --cov-report=term-missing

# 単一テストを実行
uv run pytest tests/test_specific_module.py::test_function_name

# コード品質チェック
uv run ruff check .
uv run ruff format .
uv run mypy .

# すべての品質チェックを実行
uv run pre-commit run --all-files

# 新しいパッケージをインストール
uv add package-name

# 新しい開発依存関係をインストール
uv add --dev package-name
```

## プロジェクト構造

```
aicli-config-bridge/
├── .devcontainer/              # Dev Container設定
│   └── devcontainer.json
├── src/
│   └── aicli_config_bridge/
│       ├── cli.py              # メインCLIインターフェース（Typer使用）
│       ├── config/             # 設定管理
│       │   ├── manager.py      # 設定マネージャー
│       │   └── models.py       # Pydanticモデル
│       ├── linker/             # シンボリックリンク管理
│       │   └── manager.py      # リンクマネージャー
│       ├── tools/              # ツール固有ハンドラー
│       │   ├── claude_code.py  # Claude Code統合
│       │   ├── gemini_cli.py   # Gemini CLI統合
│       │   ├── markdown_handler.py # コンテキストファイル管理
│       │   └── mcp_handler.py  # MCP設定処理
│       └── utils/              # ユーティリティ
│           └── platform.py     # プラットフォーム検出（WSL対応）
├── tests/                      # テストスイート
├── project-configs/            # プロジェクト設定ファイル
├── pyproject.toml             # プロジェクト設定
└── README.md                  # プロジェクトドキュメント
```

## 主要アーキテクチャコンポーネント

### CLIインターフェース（cli.py）
- Typerを使用したコマンドラインインターフェース
- メインコマンド: init, detect-configs, import-config, link, link-all, unlink, status, validate
- ユーザーファイル管理: link-user, unlink-user, status-user
- コンテキスト管理: import-context, link-context, create-context

### 設定管理（config/）
- JSON設定ファイルの読み書き
- 環境変数の置換（`${VAR_NAME}` 形式）
- Pydantic を使用した設定の検証

### シンボリックリンク管理（linker/）
- プラットフォーム間のシンボリックリンク作成と管理
- リンク前の既存設定のバックアップ
- リンクの整合性とステータス検証

### ツール統合（tools/）
- Claude Code と Gemini CLI 用のハンドラー
- コンテキストファイル（CLAUDE.md, GEMINI.md）管理
- MCP サーバー設定処理

## サポートされているAI CLIツール

### Claude Code
- 設定ファイル: `~/.claude/settings.json`
- プロジェクト設定: `.claude/settings.json`
- コンテキストファイル: `CLAUDE.md`

### Gemini CLI
- ユーザー設定: `~/.gemini/settings.json`
- プロジェクト設定: `.gemini/settings.json`
- コンテキストファイル: `GEMINI.md`

## 開発ガイドライン

### コード品質要件
- すべてのコードはruffリンティングとフォーマットを通す
- すべての関数に型ヒントが必要
- 新機能にはテストが必要
- 現在のテストカバレッジは約20%（改善が必要）

### ruff設定ガイドライン

日本語プロジェクトでは文字コードエラーが頻発するため、以下のruff設定を推奨します：

#### pyproject.tomlの推奨設定
```toml
[tool.ruff.lint]
ignore = [
    "RUF002", # docstring内の全角文字エラーを無視
    "RUF003", # comment内の全角文字エラーを無視
    "E501",   # 行長制限（日本語では超過しやすい場合のみ）
]
```

#### よくある日本語文字コードエラー
- `RUF002`: docstring内の全角コロン（：）、括弧（（））
- `RUF003`: コメント内の全角文字
- `E501`: 日本語文字列による行長超過

これらのエラーは品質に影響しないため、ignoreに追加することを推奨します。

#### コード内での対応
- 英語docstringを使用する場合は、半角文字を使用
- 日本語ドキュメントを保持したい場合は、上記ignore設定を使用
- CI/CDで確実にチェックが通過するよう設定を統一

### 実装状況

#### 完了済み機能 ✅
- Typerを使用したCLIインターフェース
- 設定の検出とインポート
- 基本的なシンボリックリンク管理
- Claude Code と Gemini CLI のハンドラー
- コンテキストファイル管理
- ユーザーファイルのシンボリックリンク管理
- 環境変数の置換
- 基本テストスイート（14テストが通過）
- WSL対応のプラットフォーム検出
- Dev Container設定

#### 既知の問題 ❌
- 低いテストカバレッジ（20%、CLIインターフェースはテストなし）
- プロファイル機能は未実装
- Windows完全対応は未実装

#### 解決済み問題 ✅
- ~~mypyタイプエラーが25個あり（主にモデルの不整合）~~
- ~~ruffリンティングエラーが91個あり（コメントの全角文字、行長など）~~ → ruff設定で解決

### 開発時の注意事項
- 日本語ドキュメントを使用する場合は、上記ruff設定ガイドラインに従う
- CLIコマンドは広範囲にテストされていない
- 型定義の一貫性を保つ必要がある
- CI/CDパイプラインですべてのチェックが通過することを確認

## 新しいプロジェクトでのruff設定テンプレート

新規日本語プロジェクトを開始する際は、以下の設定をpyproject.tomlに追加することを推奨：

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "ANN",  # type annotation
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    "RUF",  # ruff specific rules
    "W",    # pycodestyle warnings
]
ignore = [
    "F401",  # unused import
    "F841",  # unused variable
    "RUF002", # ambiguous unicode character in docstring
    "RUF003", # ambiguous unicode character in comment
]
unfixable = ["F401", "F841"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["ANN"]
```

このテンプレートを使用することで、日本語プロジェクトでのruffエラーを予防できます。
