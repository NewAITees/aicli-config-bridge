---
name: commit-flow
description: 実装完了後の変更を検証済みコミットにする。共通仕様に従い、Claude 側では実行順と staging ルールの補足を reference に持つ。
---

# Commit Flow

共通仕様:
- `../../../../docs/skills/commit-flow-common-spec.md`

Claude 追加運用:
- TODO: 実行順・stagingルールの補足referenceが、このリポジトリ（`project-configs/skills/claude/commit-flow/`）にまだ追加されていない。以前は特定マシンのローカルパスを指していたが、リポジトリ管理外のため他マシンから参照できず削除した。追加する場合はこのスキルフォルダ内に `references/commit-flow-reference.md` として置き、相対パスで参照する。
