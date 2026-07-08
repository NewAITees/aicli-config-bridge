# Feedback Loop Common Spec

## Goal

小さな変更と小さな検証を繰り返し、実装の不確実性を早く潰す。

## Use This Skill To

- 失敗する検証から始める
- 最小変更で通す
- 安定後にのみ整理する
- 検証結果に基づいて次手を決める

## Shared Workflow

1. Red: 失敗するテストか smoke check を定義する
2. Green: 最小変更で通す
3. Refactor: 安定後に整理する
4. 各ステップ後に関連する検証を再実行する

## Validation Order

1. 焦点の絞られたテストまたは smoke check
2. リスクに応じた広いテスト
3. repo が使っている静的解析

## Guardrails

- 小変更でも検証を省略しない
- 不安定な段階で unrelated cleanup を混ぜない
- warning や error が原因説明になっている間は先に進まない
