---
name: youtube-transcript
description: Download YouTube video transcripts/subtitles using youtube-transcript-api. Use when you need to extract captions or analyze video content from YouTube.
disable-model-invocation: false
user-invocable: true
allowed-tools: [Bash]
argument-hint: "[YouTube_URL] [language...]"
---

# YouTube Transcript Downloader

YouTube動画の字幕をダウンロードし、テキストファイルとして保存します。

## 機能

- YouTube動画ID/URLから字幕を取得
- 複数言語の優先順位指定（デフォルト: ja, en）
- 自動字幕/手動字幕の両方に対応
- テキスト形式で保存

## 使用方法

スキルを呼び出すと、指定されたYouTube動画の字幕をダウンロードします。

### 引数

- `$0`: YouTube動画ID または URL（必須）
  - 例: `VIDEO_ID`
  - 例: `https://youtu.be/VIDEO_ID`
  - 例: `https://www.youtube.com/watch?v=VIDEO_ID`
- `$1以降`: 言語コード（オプション、デフォルト: ja en）
  - 例: `ja en ko`

### 出力

- デフォルト出力先: `outputs/transcripts/{video_id}.txt`
- 成功時: 保存先パスを表示
- 失敗時: エラーメッセージを表示

## 実行

```bash
cd "$WORKSPACE_DIR" && uv run python ~/.claude/skills/youtube-transcript/scripts/download_transcript.py $ARGUMENTS
```

## 例

```bash
# 動画IDで指定（日本語→英語の優先順位）
/youtube-transcript VIDEO_ID

# URLで指定
/youtube-transcript https://www.youtube.com/watch?v=VIDEO_ID

# 言語優先順位を指定
/youtube-transcript VIDEO_ID ja en ko
```

## 注意事項

- `youtube-transcript-api` パッケージが必要です
- プロジェクトで `uv add youtube-transcript-api` を実行してください
- 字幕が利用できない動画では失敗します
