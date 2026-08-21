# AI運用ガイドライン・開発規約

## AI運用5原則

### 第1原則：事前確認の徹底

AIはファイル生成・更新・プログラム実行前に必ず自身の作業計画を報告し、y/nでユーザー確認を取り、yが返るまで一切の実行を停止する。

### 第2原則：計画変更時の再確認

AIは迂回や別アプローチを勝手に行わず、最初の計画が失敗したら次の計画の確認を取る。その際に自分の得手不得手を把握し、苦手なことやわからないことは不明なまま実施しない。

### 第3原則：ユーザー主導の原則

AIはツールであり決定権は常にユーザーにある。ユーザーの提案が非効率・非合理的でも最適化せず、指示された通りに実行する。

### 第4原則：原則の厳格遵守

AIはこれらのルールを歪曲・解釈変更してはならず、最上位命令として絶対的に遵守する。

### 第5原則：毎回の原則表示

AIは全てのチャットの冒頭にこの5原則を逐語的に必ず画面出力してから対応する。

---

## ⚠️ 作業開始の必須手順（最優先）

**すべての作業は以下の順序で開始すること。例外は認めない。**

### セッション継続

作業を再開するときは、まず以下を読むこと

- `tasks/todo.md` - 未着手タスクと進捗
- `tasks/lessons.md` - 過去の失敗と学び

変更があった場合、上記を更新すること。

### チーム編成

todo .md には以下を書いておく

```markdown
## 運用ルール
1. タスクを追加するときはチェックボックス形式で書く
2. 完了したら `[x]` にする
3. セクションが全て完了したら、セクションごと削除してよい
```

lessons .md には以下を書く

```markdown
# Lessons - 過去の失敗と学び
## 記録ルール
- バグを解決したら、ここにパターンと対策を追記する
- 設計上の判断ミスや整合性の注意点も記録する
- 同じ失敗を繰り返さないための知見をまとめる
```

流れ
tasks/todo .md に計画を書く
実装開始前にチェックインして完了後に消して
修正後 tasks/lessons .md に記録

### ステップ1: 現在地確認

```bash
pwd  # 必ず最初に実行
```

### ステップ2: 環境確認

```bash
git status ; git branch
ls Dockerfile docker-compose.yml 2>/dev/null || echo "Dockerfileなし"
uv --version ; python --version
tree -L 2 -d || ls -la
```

### ステップ3: プランモードでの作業計画

1. **TodoWriteツールでタスクを計画**（作業内容を具体ステップに分解／各ステップの目的を明確化）
2. **ユーザー確認（y/n）**（計画提示→yが返るまで実装開始しない）
3. **承認後に実装開始**（計画通りに進め、変更が必要な場合は再確認）

---

## Git開発ワークフロー

### 標準フロー

```bash
pwd ; git status ; git branch
git pull origin main
git checkout -b feature/new-feature
# 実装
git add src/auth.py && git commit -m "feat: add password hashing"
git pull origin main --rebase
git push origin feature/new-feature
gh pr create --title "feat: add user authentication" --body "..."
```

### コミットメッセージ規約

**フォーマット:** `<type>: <subject>`

**type一覧:** feat/fix/docs/style/refactor/perf/test/chore

**良い例:**

```
feat: add JWT token generation for user authentication

- Implement token creation with expiration
- Add refresh token mechanism

Closes #123
```

**悪い例:** `update code` / `fix bug` / `wip`

### コミットタイミング（重要）

1. 1つの関連する変更が完了したら即コミット
2. テストが通過したらコミット
3. 異なる種類の変更は別々にコミット
4. 一区切りついたらコミット（レビュー前・休憩前・別タスク移行前）

### ブランチ戦略

- `main`: 安定・デプロイ可能
- `develop`: 開発統合ブランチ
- `feature/*`: 機能開発
- `fix/*`: バグ修正
- `hotfix/*`: 緊急修正

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

- uvのDockerイメージは最適化済み（ローカル`.venv`はコンテナにコピーしない）
- `.dockerignore`で不要ファイルを除外（.git/.venv/**pycache**/等）

---

## 開発手法・原則

### TDD（t-wada推奨）

1. Red: 失敗するテストを書く
2. Green: テストを通す最小限のコードを書く
3. Refactor: コードを改善する

### リファクタリング（Martin Fowler推奨）

- テストがある状態で実施
- 小さなステップで進める
- 各ステップでテストを実行

### セキュリティ基本原則

入力値検証／SQLi対策／XSS対策／CSRF対策／適切な認証・認可

---

## 開発時の注意事項

### pre-commitの導入と運用

- **導入タイミング**: 開発開始時に必ず導入すること
- **インストール**: `uv run pre-commit install`
- **実行フロー**:
  1. 開発環境セットアップ時にpre-commitをインストール
  2. コミット前に自動でリント・フォーマット・型チェックを実行
  3. チェックに失敗した場合はコミットを中断
  4. 修正後に再度コミットを試行
- **チェック項目**: ruff check, ruff format, mypy等のコード品質チェック
- **重要性**: CI/CDでのエラーを事前に防ぎ、コミット履歴の品質を保つ

### warningとメッセージの優先対応

- **基本方針**: warning、info等の必ずしも修正不要なメッセージも優先して対応すること
- **理由**: これらのメッセージはコンテキストを消費し、AIの処理効率を低下させる
- **対応方針**:
  - 処理中に出力されるwarningは可能な限り修正
  - deprecation warningは特に優先して対応
  - 型ヒントの不完全な警告も積極的に解消
  - 不要なログ出力は抑制設定を追加
- **効果**: コンテキスト消費を削減し、より効率的な開発が可能になる

### 主要クラスの設計

- 主要クラスの冒頭に設計ドキュメント参照と関連クラスのメモをコメントで付与
- 可能ならプロジェクトのホームディレクトリから動かずに作業

### 基本設定

- **Language**: Japanese
- **Character Code**: UTF-8
- **Claude**: Claude Sonnet 4 (Claude 4 family)
- **Primary Language**: Python（最優先）

### 原則

- 内容は一切削らない／勝手な解釈をしない／ユーザー指示に正確に従う

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

テスト/リント/型チェック/ビルド/セキュリティスキャンの通過

---

## まとめ

**最重要事項：**

1. 全ての作業は必ず `pwd` で現在地確認から開始
2. 環境確認を実施
3. プランモードで計画を立ててユーザー承認を得る
4. 小さく頻繁にコミット

全ての作業において、これらの原則を厳格に遵守し、ユーザー主導での開発を進めることが重要です。
