# Python Development Rules

## Import Organization
- 標準ライブラリ
- サードパーティ
- ローカルインポート

## Error Handling
- 具体的な例外クラスを使用
- ログを適切に出力
- ユーザーフレンドリーなエラーメッセージ

## Type Hints
- すべての関数に型ヒントを付ける
- pydanticモデルを活用
- Anyタイプは最終手段

## コーディング規約
- すべての関数に型ヒントを必須とする
- pydanticモデルを積極的に活用する
- Googleスタイルのdocstringを使用する
- pathlib.Pathを使用（os.pathは使用しない）

## CLI開発ガイドライン
- typerを使用してCLIを構築
- 設定管理にpydanticを活用
- シンボリックリンク操作は十分な検証を行う
- クロスプラットフォーム対応を考慮

## セキュリティ
- ファイルパスの検証を徹底
- 権限チェックを適切に実行
- 機密情報をログに出力しない