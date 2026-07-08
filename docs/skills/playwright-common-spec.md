# Playwright Common Spec

## Goal

Playwright MCP を使うブラウザ操作を、両エージェントで同じ順序と判断基準で行えるようにする。

## Use This Skill To

- ページを開く
- snapshot を取り ref を確認する
- ref ベースで操作する
- screenshot / console / network を確認する

## Shared Workflow

1. 対象ページを開く
2. accessibility snapshot を取得する
3. ref を使って操作する
4. 画面変化後は再 snapshot する
5. 必要なら screenshot / console / network を見る

## Guardrails

- 見た目の推測だけで要素操作しない
- クリックや遷移の後に古い ref を使い回さない
- デバッグ時は盲目的に再試行せず console / network を先に見る
