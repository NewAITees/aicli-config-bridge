# CLAUDE.md

このファイルは Claude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

`aicli-config-bridge` は、シンボリックリンクを通じて AI CLI ツールの設定を管理する Python CLI ツールです。リンク設計図（`aicli-links.json`）に基づいて、プロジェクト内の設定ファイルをシステム上の配置場所（`~/.claude/` など）へリンクします。設定をバージョン管理し、開発環境間で共有できます。

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
│       ├── cli.py              # CLIインターフェース（Typer使用）
│       └── setup/              # リンクセットアップ
│           ├── manager.py      # LinkSetup（リンク作成・状態判定・修復・解除）
│           └── models.py       # Pydanticモデル（LinkItem, LinksConfig, LinkStatus）
├── tests/                      # テストスイート
├── project-configs/            # リンク元となるプロジェクト管理の設定ファイル
├── symbolicLink/               # ホームディレクトリ実体への参照用シンボリックリンク集
├── aicli-links.json            # リンク設計図（リポジトリルートに配置）
├── docs/                       # セットアップガイド・要件定義・スキル共通仕様
├── pyproject.toml              # プロジェクト設定
└── README.md                   # プロジェクトドキュメント
```

## 主要アーキテクチャコンポーネント

### CLIインターフェース（cli.py）
- Typerを使用したコマンドラインインターフェース
- コマンド: `setup`（対話的セットアップ）, `apply`（非対話適用、AI向け）, `status`（状態表示、`--json` 対応）, `init`（設計図の新規作成）
- 引数なし起動で対話メニュー（setup / status / unlink / exit）を表示

### リンクセットアップ（setup/）
- `aicli-links.json`（リンク設計図）を Pydantic モデル（`LinksConfig` / `LinkItem`）で読み込み・検証
- リンク状態判定: `linked` / `missing_target` / `broken_link` / `wrong_link` / `existing_file` / `missing_source`
- 既存ターゲットの競合処理: backup / overwrite / skip（バックアップ先はターゲット親ディレクトリの `.aicli-backup/`）
- 壊れたリンクの修復（repair）とリンク解除（unlink）
- プラットフォーム検出（windows / wsl / darwin / linux）と `target_windows` によるWindows用パス指定
- パス解決: `~` および `%USERPROFILE%` を展開

## リンク設計図（aicli-links.json）

各リンクは以下のフィールドを持つ:

- `id`: 一意識別子
- `name`: 人間が読める説明
- `type`: `file` / `directory`
- `source`: プロジェクト内のソースパス（相対パス）
- `target`: リンク先パス（`~` 使用可、Linux/Mac/WSL共通）
- `target_windows`: Windowsネイティブ用パス（省略可、`%USERPROFILE%` 使用可）
- `create_if_missing`: ソースがない場合に作成するか
- `default_content`: 作成時のデフォルト内容

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
- Typerを使用したCLIインターフェース（setup / apply / status / init / 対話メニュー）
- リンク設計図（aicli-links.json）に基づくシンボリックリンク作成
- リンク状態判定・修復・解除
- 既存ファイルのバックアップ（`.aicli-backup/`）
- dry-run 対応
- WSL対応のプラットフォーム検出
- Dev Container設定

#### 未実装 ❌
- Windowsネイティブでのコピー運用（`_create_link` は常にシンボリックリンクを作成）
- ツール間設定同期コマンド（`sync`、要件定義は `docs/REQUIREMENTS_SYNC.md`）
- CLIインターフェースのテスト（テストは setup/manager.py が中心）

### ドキュメント同期ルール

- ドキュメント（本ファイル・README）は実装に従属する。実装を変えたら同じ変更内でドキュメントを更新すること
- 実装されていない機能をドキュメントに「ある」と書かないこと。将来計画は `docs/REQUIREMENTS_SYNC.md` のような要件定義ファイルに分離すること

### 開発時の注意事項
- 日本語ドキュメントを使用する場合は、上記ruff設定ガイドラインに従う
- CLIコマンドは広範囲にテストされていない
- 型定義の一貫性を保つ必要がある
- CI/CDパイプラインですべてのチェックが通過することを確認

## 人間の関与と許可設計

人間の承認は操作監視ではなく、目的・影響範囲・リスク・復旧方法に関する意思決定のために使う。細かい確認を繰り返すと、承認が形式化して重要な判断を見落としやすくなる。

### 承認単位

第1原則の事前確認は、すべてのファイル変更やコマンドを個別に許可するという意味ではない。AIは、意味のある作業計画を提示し、その計画全体について一度承認を得る。計画が承認された後は、承認範囲内のファイル編集、コマンド実行、テスト、差分確認を個別に再確認せず進める。

第2原則は、承認済み計画の範囲を超える場合に適用する。目的、変更対象、影響範囲、費用、外部送信先、公開範囲、復旧方法のいずれかが変わる場合は、作業を止めて変更後の計画を提示し、再承認を得る。

### 許可レベル

#### 個別承認を省略できる操作

隔離された開発環境で実行され、差分確認・破棄・復元が容易な場合は、次の操作を個別に確認しない。

- ファイルの閲覧、検索、ログや差分の確認
- ドラフト、メモ、一時ファイルの作成
- 新しいブランチ内でのコード編集
- テスト、静的解析、フォーマット、プレビュー
- 元データを残した状態での変換やローカル試作

#### 作業単位で承認する操作

複数ファイルの変更、依存関係、設定、権限、外部連携など、影響範囲が広い操作は、個別のコマンドではなく作業計画単位で承認を得る。計画には目的、変更対象、影響範囲、主なリスク、復旧方法、完了条件を含める。

- 複数ファイルにまたがる変更
- 依存パッケージの追加・更新
- アプリケーション設定やデータベーススキーマの変更
- ブランチのマージ
- 外部APIへのデータ送信
- セキュリティや権限に関する変更
- 開発環境以外へのデプロイ

承認された範囲内では、ファイルごと・コマンドごと・ツールごとの再確認を求めずに実行する。

#### 実行直前に明示承認する操作

事前に計画を承認していても、次の操作は実行直前に対象と結果を明示して確認する。

- 支払い、購入、契約
- メール、メッセージ、SNS、公開ウェブへの送信・投稿
- 本番環境への公開
- 本番データの削除・上書き
- アカウントや権限の削除
- 法的・人事的な意思決定
- 機密情報の外部送信

### 作業フロー

1. 調査、読み取り、検索、分析は、細かい許可を求めずに行う。
2. 実装前に、目的、変更範囲、影響、リスク、復旧方法、完了条件を作業計画として提示する。
3. 計画が承認されたら、承認範囲内の操作を自律的に進める。
4. 計画外の重大な問題、範囲拡大、復旧不能、外部影響、不可逆操作が必要になった場合は停止して再確認する。
5. 完了後に、実行内容、差分、検証結果、残存リスクを報告する。

人間が承認するのはAIのキーストロークではなく、AIが引き起こす結果である。承認後に変更対象、外部送信先、費用、公開範囲を拡大してはならない。

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

### Any封じ込めルール（境界限定）

6. **`Any` の利用範囲を境界に限定する**
   `json.loads`、`**kwargs`、スタブ未整備ライブラリなど、外部との境界でのみ `Any` を許容する。
7. **境界直後に型へ変換する**
   `isinstance` / `cast` / Pydantic `model_validate` を使って、`dict[str, object]` や明示モデルに即時変換する。
8. **内部ロジックに `Any` を持ち込まない**
   services / orchestrator / repository の業務ロジック層では `Any` のまま受け渡ししない。
9. **境界処理を関数へ局所化する**
   `parse_*` / `from_external_*` などの関数に集約し、`Any` の扱いを1箇所で完結させる。

---

### データ中心主義と型設計の原則

設計の前提として**データ中心主義**を取り入れる。
処理の流れより「どんなデータが存在するか」を先に定義し、型はそのデータの契約として機能させる。

#### 型を作るべき境界

| 境界 | 理由 |
|---|---|
| 外部入力 | バリデーションが必要 |
| ドメインの核 | ビジネスロジックの中心 |
| 外部出力 | 下流との契約 |

内部の計算途中（中間処理）は `dict` / `tuple` / `dataclass` で十分なことが多い。

#### 変換回数を減らす設計

```python
# 悪い例：変換が多すぎる
RawText → TokenizedText → NormalizedText → ScoredText → RankedText

# 良い例：意味のある境界だけ型にする
RawInput → DocumentChunk → AnalysisResult
          (内部処理はまとめて一関数)
```

パイプラインの「入口・出口・分岐点」だけ型を作る。関数1本の中の処理は型なしでよい。

#### 型の安定性ルール

- 一度作った型のフィールドを後から変えない（下流が全部壊れる）
- 複数の関数が同じ型を受け取る場合は特に慎重に変更する
- 型を変えるときは新しい型名を作って移行する（古い型を壊さない）

```python
# 型を変えたいとき
class AnalysisResultV2(BaseModel):  # V1を壊さず並存させる
    ...
```

#### 型の数のサイン

型の数 ≒ 関数の数 になってきたら「型を作りすぎ」のサイン。
型はコントラクト（契約）であり、多すぎると変更コストが上がる。

---

## .claudeignore の作成ルール

プロジェクト作成時に必ず `.claudeignore` を配置し、Claude Code の自動スキャンによる不要なトークン消費を防ぐこと。

### 標準テンプレート

```
# 依存関係
node_modules/
.venv/
venv/
__pycache__/
*.pyc
*.pyo
.eggs/
*.egg-info/
dist/
build/

# ビルド成果物
*.o
*.so
*.dll
*.class
target/
out/
.next/
.nuxt/

# ログ・一時ファイル
*.log
logs/
tmp/
temp/
.tmp/
*.bak
*.swp
*.DS_Store

# テストカバレッジ
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# 環境・秘密情報
.env
.env.*
*.pem
*.key

# IDE・エディタ
.idea/
.vscode/
*.iml
```

### 運用ルール

- 新規プロジェクト作成時に `.claudeignore` を必ず作成する
- `node_modules/`、`.venv/`、ビルド成果物、ログは必ず除外する
- プロジェクト固有の不要ディレクトリは追記して管理する
- `.gitignore` と重複してよい（目的が異なる：Gitはバージョン管理、claudeignoreはスキャン除外）
