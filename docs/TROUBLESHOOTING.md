# トラブルシューティング（2026-02-05 時点の修正内容）

このドキュメントは、現在の作業ツリーにある修正内容を「何が変わったか」「どこを見れば問題切り分けできるか」の観点で整理した記録です。

## CLI の対話メニュー追加

- サブコマンド無しで起動すると対話メニューを表示するようになった。
- 対話メニューの選択肢: `setup` / `status` / `unlink` / `exit`
- オプション追加:
  - `--project-root` / `-p`: プロジェクトルートを明示指定
  - `--dry-run`: 実際の変更は行わず予定のみ表示
- 該当ファイル: `src/aicli_config_bridge/cli.py`

切り分けポイント:
- `aicli-config-bridge` を引数無しで実行した場合にメニューが出るか。
- `status` 実行でテーブルが表示されるか。
- `status` 実行時に不整合があれば修復確認が出るか。
- `unlink` で `all` または `id1,id2` が解釈されるか。

## リンク状態の判定と表示

- `LinkStatus` を追加:
  - `linked` / `missing_target` / `broken_link` / `wrong_link` / `existing_file` / `missing_source`
- `get_link_status()` でリンク状態判定
- `show_status_table()` でテーブル表示
- 該当ファイル: `src/aicli_config_bridge/setup/models.py`, `src/aicli_config_bridge/setup/manager.py`

切り分けポイント:
- `source` が存在しない場合は `missing_source`
- `target` がシンボリックリンクの場合:
  - `target -> source` かつ `source` 存在で `linked`
  - `target` が指す先が存在しない場合 `broken_link`
  - `target` が別の先を指す場合 `wrong_link`
- `target` が通常ファイル/ディレクトリで存在する場合 `existing_file`
- どれでもなければ `missing_target`

## 修復（repair）の挙動

- `status` で不整合がある場合、確認後に `repair_links()` を実行。
- `source` が無いものは修復対象から除外。
- `target` に既存ファイル/リンクがある場合は既存処理で扱う（スキップされる場合あり）。
- `--dry-run` は「修復予定」のみ出力。
- 該当ファイル: `src/aicli_config_bridge/setup/manager.py`

切り分けポイント:
- `source` があるのに修復されない場合、`target` の既存処理が影響していないか確認。
- `dry-run` の表示が出るか、実際のファイル操作が抑止されるか。

## リンク解除（unlink）の挙動

- `unlink_links()` で指定 ID のリンク解除。
- シンボリックリンクは削除対象。通常ファイル/ディレクトリは確認後に削除。
- `--dry-run` では削除せず予定のみ表示。
- 該当ファイル: `src/aicli_config_bridge/setup/manager.py`

切り分けポイント:
- 指定 ID が `aicli-links.json` に存在するか。
- `target` が通常ファイルの場合は削除確認が出るか。

## パス解決の変更

- `_resolve_path()` が `resolve()` から `absolute()` に変更。
  - シンボリックリンク先の解決を行わず、絶対パス化のみ実施。
- 該当ファイル: `src/aicli_config_bridge/setup/manager.py`

切り分けポイント:
- 既存のシンボリックリンクがある環境では、リンク先の実体パスとの比較結果が変わる可能性がある。
- リンク判定が想定と異なる場合は、`source`/`target` の実パスと表示パスを確認。

## 追加テスト

- `test_get_link_status_linked`: `linked` 判定のテスト
- `test_unlink_links_removes_symlink`: シンボリックリンク解除のテスト
- 該当ファイル: `tests/test_setup_manager.py`

## 作業ツリーの未追跡ファイル

- `aicli-links.json` が新規作成されており、未追跡状態。
- 必要に応じて追加・除外（`.gitignore`）を判断する。

