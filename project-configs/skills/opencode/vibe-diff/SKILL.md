---
name: vibe-diff
description: 危険操作の対象・理由・影響・復旧可能性を平易な日本語で説明する。通常編集や読取操作では使わない。
---

# 危険操作の説明 / Vibe Diff

実行前ガードが危険操作を検出したら、対象、何が起こるか、危険な理由、影響範囲、復旧できるかとその方法を説明する。
askで確認可能な実行経路ではユーザー確認まで止める。denyはユーザーのyがあっても迂回・無効化・コマンド変形で再実行しない。
CodexのPreToolUseはask未対応のためdenyに変換される。OpenCode v2のpermission hookは危険操作をネイティブのaskで確認する。Claude専用のhookや確認画面が動いたとは報告しない。
検知ロジックは管理元 `project-configs/shared/hooks/agent_guard.py` と既存の危険操作ルールに委譲し、スキルへ複製しない。
