# AI運用ガイドライン・開発規約

## AI運用5原則

### 第1原則：事前確認の徹底

AIはファイル生成・更新・プログラム実行前に、必ず自身の作業計画を報告し、y/nでユーザー確認を取ること。  
yが返るまで、一切の実行を停止すること。

### 第2原則：計画変更時の再確認

AIは迂回や別アプローチを勝手に行ってはならない。  
最初の計画が失敗した場合は、次の計画を提示し、再度ユーザー確認を取ること。  
その際、自分の得手不得手を把握し、苦手なことやわからないことは、不明なまま実施してはならない。

### 第3原則：ユーザー主導の原則

AIはツールであり、決定権は常にユーザーにある。  
ユーザーの提案が非効率・非合理的であっても、AIは勝手に最適化せず、指示された通りに実行すること。

### 第4原則：原則の厳格遵守

AIはこれらのルールを歪曲・解釈変更してはならない。  
本規約は最上位命令として、絶対的に遵守すること。

### 第5原則：毎回の原則表示

AIは全てのチャットの冒頭に、この5原則を逐語的に必ず画面出力してから対応すること。

---

## 作業開始の必須手順（最優先）

すべての作業は、以下の順序で開始すること。  
例外は認めない。

### tasks/ ディレクトリの初回作成

`tasks/` ディレクトリが存在しない場合は、作業開始前に以下を実行して作成すること。

```bash
mkdir -p tasks
touch tasks/todo.md tasks/lessons.md
```

作成後、それぞれのファイルに後述の基本形式を書き込んでから作業を開始すること。

### セッション継続

作業再開時は、まず以下を確認すること。

- `tasks/todo.md` - 未着手タスクと進捗
- `tasks/lessons.md` - 過去の失敗と学び

変更があった場合は更新すること。

### タスク管理ファイルの基本形式

`tasks/todo.md` には以下を書くこと。

```markdown
## 運用ルール
1. タスクを追加するときはチェックボックス形式で書く
2. 完了したら [x] にする
3. セクションが全て完了したら、セクションごと削除してよい
```

`tasks/lessons.md` には以下を書くこと。

```markdown
# Lessons - 過去の失敗と学び

## INDEX（追記・修正のたびに必ず更新すること）
| カテゴリ     | 説明                          | 開始行 | 件数 |
|--------------|-------------------------------|--------|------|
| meta         | AIとの協働ルール              | -      | 0    |
| boundary     | データ型・変換・境界契約      | -      | 0    |
| architecture | 設計・責務・config            | -      | 0    |
| quality      | テスト・CI/CD・品質保証       | -      | 0    |
| ui           | フロントエンド・デザイン・VRM | -      | 0    |

---

## meta — AIとの協働ルール
### [タイトル（キーワードを含む1行）]
- **症状**: 
- **原因**: 
- **対策**: 

## boundary — データ型・変換・境界契約
### [サブカテゴリ: タイトル]

## architecture — 設計・責務・config
### [サブカテゴリ: タイトル]

## quality — テスト・CI/CD・品質保証
### [サブカテゴリ: タイトル]

## ui — フロントエンド・デザイン・VRM
### [サブカテゴリ: タイトル]
```

### 作業開始フロー

1. `pwd` で現在地を確認する
2. 環境確認を実施する
3. `tasks/todo.md` に作業計画を書く
4. 作業を具体的なステップに分解する
5. ユーザーに計画を提示し、y/n確認を取る
6. yが返るまで実装を開始しない
7. 承認後に実装を開始する
8. 計画変更が必要になった場合は再確認を取る
9. 完了後に `tasks/todo.md` を更新する
10. 学びを `tasks/lessons.md` に記録する

### 現在地確認

```bash
pwd
```

### 環境確認

```bash
git status ; git branch
ls Dockerfile docker-compose.yml 2>/dev/null || echo "Dockerfileなし"
uv --version ; python --version
tree -L 2 -d || ls -la
```

---

## Git開発ワークフロー

### 標準フロー

```bash
pwd ; git status ; git branch
git pull origin main

# 新規リポジトリの場合：.gitattributes を配置して改行コードを統一する
# .gitattributes がなければ作成し、git add --renormalize . を実行すること
git add --renormalize .
git commit -m "chore: normalize line endings"

# 実装・コミット
git add src/auth.py && git commit -m "feat: add password hashing"
git push origin main
```

### コミットメッセージ規約

以下の形式を使うこと。

```text
<type>: <subject>
```

使用可能な `type` は以下とする。

```text
feat / fix / docs / style / refactor / perf / test / chore
```

良い例：

```text
feat: add JWT token generation for user authentication

- Implement token creation with expiration
- Add refresh token mechanism

Closes #123
```

悪い例：

```text
update code
fix bug
wip
```

### コミットルール

以下のいずれかの条件を満たした時点でコミットすること。

- 1つの関数・クラス・モジュールの実装が完了した
- テストが1件以上追加・修正され、通過した
- リファクタリングの1ステップが完了し、テストが通過した
- バグ修正が1件完結した

異なる種類の変更は別コミットに分けること。テストが通過していない状態でコミットしてはならない。

### ブランチ戦略

| ブランチ | 用途 |
|---|---|
| `main` | 安定・デプロイ可能 |
| `develop` | 開発統合ブランチ |
| `feature/*` | 機能開発 |
| `fix/*` | バグ修正 |
| `hotfix/*` | 緊急修正 |

---

## Security Rules

### socket firewall free（sfw）について

`sfw` は Socket が提供するオープンソースのサプライチェーン攻撃対策ファイアウォールツールである。
パッケージインストール時のネットワーク通信を監視・制御し、悪意あるパッケージのインストールを防ぐ。

### 使用ルール

- パッケージのインストールは必ず `sfw` を介して実行する
- AIが提案するインストールコマンドにも必ず `sfw` を付与する
- 新規パッケージ追加前に、実在し広く使われていることを確認する
- 馴染みの薄いパッケージを提案する場合は説明を付ける
- 依存関係は必ず exact version で固定する
- `^`, `>=`, `~`, `latest` を使ってはならない
- lockfile は必ずコミットする

```bash
# Python (uv)
sfw uv add package-name==1.2.3
sfw uv add --dev package-name==1.2.3
sfw uv sync

# Node.js (npm / pnpm / yarn)
sfw npm install package-name@1.2.3
sfw pnpm add package-name@1.2.3
sfw yarn add package-name@1.2.3

# その他
sfw pip install package-name==1.2.3
```

---

## 改行コード統一（.gitattributes）

リポジトリ作成時に必ず `.gitattributes` を配置し、改行コードをリポジトリ側で統一すること。個人の `core.autocrlf` 設定に依存させてはならない。

### 標準テンプレート

```gitattributes
* text=auto
*.py   text eol=lf
*.md   text eol=lf
*.json text eol=lf
*.yml  text eol=lf
*.yaml text eol=lf
*.sh   text eol=lf
```

`text=auto` は Git がテキスト／バイナリを自動判定する設定。`eol=lf` を明示したファイルは、チェックアウト・コミット時に問答無用で LF に統一される。画像・アーカイブ等のバイナリには `text` を付けない。

### 既存リポジトリへの適用

`.gitattributes` を追加しただけでは既存ファイルの改行は即座に変わらない。以下を実行して正規化すること。

```bash
git add --renormalize .
git commit -m "chore: normalize line endings"
```

### mixed-line-ending について

1ファイル内に LF と CRLF が混在している状態を mixed-line-ending と呼ぶ。`pre-commit` や CI で検出・拒否するか、保存時に自動修正する方針をリポジトリとして決めること。`eol=lf` を `.gitattributes` で指定していれば、コミット時に Git 側で吸収されるケースが多い。

---

## Docker/uv環境構築

### Dockerfile（推奨）

```dockerfile
FROM ghcr.io/astral-sh/uv:0.9.2-python3.12-bookworm-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
CMD ["uv","run","python","app.py"]
```

### docker-compose.yml

```yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    volumes: [".:/app"]
    environment: ["PYTHONUNBUFFERED=1"]
    command: uv run python app.py
```

### 重要事項

- uvのDockerイメージは最適化済みである
- ローカルの `.venv` はコンテナにコピーしないこと
- `.dockerignore` で不要ファイルを除外すること

---

## 開発手法・原則

### TDD

1. Red: 失敗するテストを先に書く
2. Green: テストを通す最小限のコードを書く
3. Refactor: コードを改善する

### リファクタリング

- テストがある状態で実施する
- 小さなステップで進める
- 各ステップでテストを実行する

### セキュリティ基本原則

入力値検証、SQLi対策、XSS対策、CSRF対策、適切な認証・認可を守ること。

---

## 開発時の注意事項

### pre-commitの導入と運用

- 開発開始時に必ず導入すること
- インストールは `uv run pre-commit install` を使うこと
- コミット前に自動でリント、フォーマット、型チェックを実行すること
- チェックに失敗した場合はコミットを中断すること
- 修正後に再度コミットを試行すること
- チェック項目には `ruff check`, `ruff format`, `mypy` 等を含めること

### レビューとテストの実施

- 実装後は必ず自分でコードレビューを行うこと
- テストは関連テストだけでなく、できるだけ包括的に全テストを実行すること
- `uv run pytest` で全テストを実行し、`uv run ruff check .` `uv run mypy .` も合わせて確認すること
- `uv run pytest` で全テストを実行し、`uv run ruff check .` `uv run mypy .` も合わせて確認すること

### warningとメッセージの優先対応

- warning、info 等のメッセージも優先して対応すること
- deprecation warning、型ヒント警告、不要なログ出力を放置しないこと

### 主要クラスの設計

- 主要クラスの冒頭には、設計ドキュメント参照と関連クラスのメモをコメントで付与すること
- 可能であれば、プロジェクトのホームディレクトリから動かずに作業すること

### 基本設定

- Language: Japanese
- Character Code: UTF-8
- Primary Language: Python（最優先）

### 実装前の確認

- 前提を明示すること。不確かなら聞くこと
- 複数の解釈がある場合は提示し、黙って選ばないこと
- よりシンプルな方法があれば指摘すること
- 混乱している場合は止まって名前をつけて聞くこと

### シンプルさの維持

- 要求された以上の機能を追加しないこと
- 単一用途のコードに抽象化を持ち込まないこと
- 要求されていない「柔軟性」「設定可能性」を加えないこと
- 200行で書けるところを50行で書けるなら書き直すこと

### 変更範囲の限定

- 必要な箇所だけ触ること。隣接するコードを「改善」しないこと
- 自分の変更が生み出した未使用のimport・変数・関数は削除すること
- 既存の未使用コードは指摘にとどめ、削除しないこと
- すべての変更行がユーザーの要求に直接紐づくこと

### 目標駆動の実行

- タスクを検証可能な形に変換してから実装すること
  - 「バグを直す」→「再現テストを書き、通過させる」
  - 「リファクタする」→「前後でテストが通ることを確認する」
- 複数ステップのタスクは計画を提示してから実行すること

### 解釈に関する原則

- 内容は一切削らないこと
- ユーザー指示に正確に従うこと


---

## CI/CD運用

### GitHub Actions（例）

```yaml
name: CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v2
      - name: Set up Python
        run: uv python install 3.12
      - name: Install dependencies
        run: uv sync
      - name: Run tests
        run: uv run pytest
      - name: Run linter
        run: uv run ruff check .
      - name: Run type checker
        run: uv run mypy .
```

### CI/CDチェック項目

- テスト
- リント
- 型チェック
- ビルド
- セキュリティスキャン

---

## まとめ

### 最重要事項

1. 全ての作業は必ず `pwd` で現在地確認から開始する
2. 環境確認を実施する
3. プランモードで計画を立て、ユーザー承認を得る
4. コミットは論理的な完了単位（関数・テスト・バグ修正）ごとに行う

- fallbackを使わないこと
- 後方互換性を維持しないこと
- テストを適当に結果を歪ませることでうまくいったように見せかけないこと

全ての作業において、これらの原則を厳格に遵守し、ユーザー主導で開発を進めること。

@RTK.md
