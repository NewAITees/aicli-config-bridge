# 開発計画書（aicli-config-bridge）

最終更新: 2026-02-05

## 目的

- WSL と Windows のユーザー環境を分離して管理できるようにする
- Windows はシンボリックリンク非依存で「管理しやすい」運用を実現する
- アプリ起動後に人が選択しながら進められる操作体験を提供する

## 背景と課題

- 現在の運用は WSL 前提で、Windows ネイティブはコピー運用のみ
- 既存ドキュメントは現状の実装と乖離しており再利用しづらい
- 一括コマンド前提の UI は人間の操作に向いていない

## 方針（要件1）

### 環境分離

- `symbolicLink/` を `symbolicLink/wsl/` と `symbolicLink/windows/` に分割
- WSL/Windows で同一の構成・同一のファイル名を維持
- どちらも「プロジェクト内管理」を基本とする

### Windows 管理方式（シンボリックリンク無し）

- Windows はコピー運用を基本とする
- 同期状態を `aicli-state.json` に記録し、差分を検知する
- 同期方向は人が選ぶ（勝手に上書きしない）
- 破損・差分・未管理を明示的に表示する

## 詳細計画

## 方向性レビュー（要点）

### 良い点

- WSL/Windows の環境分離方針は妥当
- 状態管理と差分検知の導入はコピー運用に必須
- 対話型 UI は安全性の面で有効

### 懸念点と改善案（採用方針）

1. **設定ファイルの二重管理**
   - 同一内容が `symbolicLink/wsl` と `symbolicLink/windows` に並ぶと保守負荷が高い
   - **採用案**: 共通ベース + 環境差分（override）方式

```
configs/
├── base/              # 共通設定（バージョン管理対象）
│   ├── CLAUDE.md
│   └── claude_settings.json
└── overrides/         # 環境固有の上書き（gitignore推奨）
    ├── wsl/
    └── windows/

targets/
├── wsl/               # WSL 用のリンク配置
└── windows/           # Windows 用のコピー先
```

2. **状態管理の粒度**
   - 方向固定の `direction` だけでは双方向同期に弱い
   - **採用案**: project/target それぞれの hash と mtime を保存し、競合を判定

3. **Windows 側の正本**
   - **採用方針**: 両方向同期を許可。ただし競合時は必ず人に確認

4. **対話型 UI の操作フロー**
   - 既定動作を用意し、手動メニューは必要時に限定
   - **採用案**: `status` と `sync` を中心に設計

```
status: 破壊的操作なしで差分表示
sync --interactive: 手動選択
sync --auto: 自動判定 + 競合時のみ確認
```

5. **テスト戦略**
   - 優先度は状態管理・ファイル操作を最上位に
   - CLI 表示は後回しでよい

## 詳細計画（更新版）

### フェーズ 1: 基盤整備（破壊的変更なし）

1. テストカバレッジを 40% 以上に引き上げ
2. 既存機能のドキュメント更新（現状と一致させる）
3. WSL/Windows 判定ロジックの整理とテスト追加

### フェーズ 2: 状態管理の導入

1. `aicli-state.json` のスキーマ設計
2. ハッシュ計算・差分検知ロジックの実装
3. 状態管理のテスト（この段階で 60% 目標）

### フェーズ 3: Windows 対応強化

1. コピー同期ロジックの実装
2. 競合検知と解決フロー
3. Windows 環境での E2E テスト

### フェーズ 4: ディレクトリ再設計

1. 共通設定ベース方式の実装（`configs/base` + `overrides`）
2. 既存ファイルの移行ツール作成
3. 移行ガイド作成

### フェーズ 5: 対話型 UI

1. 選択式メニューの実装
2. 差分表示の改善
3. 実行結果の視覚化

### フェーズ 6: 既存機能の統合

1. 新旧コマンドの互換レイヤ
2. 段階的な移行パス提供
3. 最終的なドキュメント整備

## 仕様メモ（暫定）

### aicli-config.json（拡張案）

```json
{
  "targets": {
    "wsl": {
      "mode": "symlink",
      "base_dir": "./symbolicLink/wsl"
    },
    "windows": {
      "mode": "copy",
      "base_dir": "./symbolicLink/windows"
    }
  }
}
```

### aicli-state.json（新規・更新案）

```json
{
  "items": [
    {
      "id": "claude-md",
      "target": "windows",
      "path": "C:/Users/.../CLAUDE.md",
      "project_hash": "sha256:...",
      "project_mtime": "2026-02-04T12:34:56Z",
      "target_hash": "sha256:...",
      "target_mtime": "2026-02-04T13:00:00Z",
      "conflict": false,
      "last_sync_direction": "project_to_target"
    }
  ]
}
```

## 非目標

- WSL/Windows 間の自動同期（自動上書き）は行わない
- 既存の一括コマンドを完全に廃止することは当面しない

## 次の決定事項

1. Windows 側の変更をどこまで許可するか（競合時の UX 方針）
2. 既存の `link-user` を残すか段階的に置換するか
3. `configs/` + `targets/` 構成への移行タイミング
