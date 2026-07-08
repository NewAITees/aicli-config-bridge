# Commit Flow Common Spec

## Goal

実装完了後の変更を、検証済みで意図の明確なコミットにする。

## Use This Skill To

- 最終 diff を見直す
- 必要な検証を通す
- 意図したファイルだけを stage する
- 説明可能な commit message を書く

## Shared Workflow

1. `git diff` と `git diff --staged` を確認する
2. accidental change や debug 残骸を除く
3. 関連テストと静的解析を実行する
4. 意図したファイルだけを stage する
5. Conventional Commits で commit する

## Commit Rules

- 1コミット1論理変更を優先する
- failing code を commit しない
- `--no-verify` を使わない
- unrelated files を混ぜない

## Guardrails

- 検証失敗時は先に修正する
- diff が広すぎる場合は分割する
- commit message が変更理由を説明できない場合は書き直す
