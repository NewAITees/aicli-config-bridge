# Spec Common Spec

## Goal

実装前に、ゴール・完了基準・スコープ・制約を最小限の質問で確定する。

## Use This Skill To

- 要求の背後にあるゴールを確認する
- 完了判定を検証可能な形にする
- スコープ内外を明確にする
- 不要な推測実装を防ぐ

## Shared Workflow

1. 未完了の `spec:` 項目があれば先に確認する
2. ゴールを確認する
3. 完了基準を確認する
4. 必要なら制約や対象ユーザーを確認する
5. 理解した内容を短く要約する
6. 承認を得てから実装に進む

## Shared Output

```text
Goal:
Success criteria:
Scope:
Out of scope:
Constraints:
```

## Guardrails

- ゴールが曖昧なまま実装しない
- 複数解釈がある場合は黙って選ばない
- スコープを勝手に広げない
