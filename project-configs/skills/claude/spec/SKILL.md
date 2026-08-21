---
name: spec
description: 実装前に要件を定義する。成功条件、失敗条件、エスカレーション条件、完了基準、前提条件、許容される判断を明確にし、Plan や実装手順より先に Spec を固める。
---

# Spec

共通仕様:
- `/home/perso/analysis/aicli-config-bridge/docs/skills/spec-common-spec.md`

## Claude 追加運用

- `tasks/todo.md` の未完了 `spec:` を先に確認する
- ユーザー承認前に実装しない
- 未確定の前提条件、成功条件、完了基準がある場合は、未確定のまま明示する
- 軽微な実装詳細まで毎回確認に戻さず、共通仕様の `Allowed Autonomy` に従って扱う
- `Judgment Stop Conditions` に当たる場合は、完了扱いにせず確認へ戻す

## Guardrails

- 承認前に実装しない
- `tasks/todo.md` の未完了 `spec:` を無視しない
- 完了基準が検証可能になるまで実装へ進まない
- 前提条件が曖昧なまま空気読みで補完しない
- 成功条件、失敗条件、エスカレーション条件を混同しない
