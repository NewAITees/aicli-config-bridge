# Spec Skill Sync Notes

## Goal

`docs/skills/spec-common-spec.md` の更新内容を、`codex` と `claude` の実体 `SKILL.md` に反映するときの差分方針を残す。

## Current State

### Codex

- 実体: `/mnt/c/Users/perso/.codex/skills/spec/SKILL.md`
- 状態: 単体で完結した薄い説明を持っている
- 問題:
  - Spec を「goal clarification」中心に説明している
  - `Completion criteria` と `Preconditions` の優先度が低い
  - `Spec / Plan / Code` の分離がない
  - 高リスク領域でのみ手順制約を Spec に入れる考え方がない

### Claude

- 実体: `/mnt/c/Users/perso/.claude/skills/spec/SKILL.md`
- 状態: 共通仕様参照型
- 問題:
  - 参照している `references/spec-reference.md` が実体上見つからない
  - 共通仕様更新後の追加運用が未定義

## Required Sync

### Codex `SKILL.md`

- Purpose / Use This Skill To / Process / Output / Guardrails を、共通仕様の内容に合わせて更新する
- 少なくとも以下の軸を明記する
  - 手順ではなく要件を定義する
  - 完了基準を先に定義する
  - AI は空気読みせず前提条件を確認する
  - 実装手順は制約でない限り先に固定しない
  - 高リスク領域ではプロセス制約を Spec に含めてよい
  - 出力は要件文書として構造化する

### Claude `SKILL.md`

- 共通仕様参照のままでよい
- ただし `references/spec-reference.md` を使うなら実体を作る必要がある
- 追加 reference を置かないなら、その参照行は削除した方がよい

## Recommended Claude Reference Content

Claude 側に追加運用を残すなら、共通仕様の焼き直しではなく、次だけを書く。

- `tasks/todo.md` の未完了 `spec:` を優先確認する
- ユーザー承認前に実装しない
- Spec の未確定点がある場合は、未確定として明示する

## Suggested Minimal Codex Shape

```text
Purpose:
- Define requirements before implementation.

Use This Skill To:
- Turn ambiguous requests into a concrete spec.
- Confirm completion criteria and preconditions.
- Separate spec from plan and code.

Process:
1. Check unfinished `spec:` items.
2. Clarify background and purpose.
3. Clarify completion criteria.
4. Clarify required behaviors, constraints, out-of-scope items, and preconditions.
5. Summarize as a spec.
6. Wait for approval before implementation.
```

## Follow-Up

- このリポジトリでは共通仕様が正本
- 実体 `SKILL.md` の更新は、外部パスへの書き込み権限がある環境で別途行う
