# sfw Hook 共通仕様 / sfw Hook Common Specification

## 目的 / Purpose

sfw（Socket Firewall）は、パッケージマネージャーの通信を監視するサプライチェーン対策ツール。
エージェントが毎回 `sfw` を思い出す運用ではなく、`PreToolUse` Hookで `sfw` なしのパッケージ取得を機械的に拒否する。

## 管理構造 / Managed Structure

```text
aicli-config-bridge
├─ project-configs/.claude/hooks/sfw_pre_tool_use.py
│  └─ Claude PreToolUse Hook本体（標準ライブラリのみ）
├─ aicli-links.json
│  └─ id: claude-hook-sfw-pre-tool-use で ~/.claude/hooks/ へ配置
└─ tests/test_sfw_hook.py

ユーザー環境
└─ ~/.claude/settings.json
   └─ hooks.PreToolUse (matcher: Bash) に python3 ~/.claude/hooks/sfw_pre_tool_use.py を登録
```

## 動作 / Behavior

- Bashコマンドを `&&` `||` `;` `|` で分割し、各セグメントの先頭コマンドを検査する。
- `sfw` で始まらないパッケージ取得系サブコマンドは `permissionDecision: deny` で拒否し、`sfw <コマンド>` での再実行を促す。
- 拒否後は `sfw` を付けて再実行すれば通る。コマンドの自動書き換えはしない（RTKとの適用順に依存させない）。
- `sudo` `env` `time` などのラッパー、`VAR=1` 形式の環境変数、`bash -c '...'` 内のコマンド、`python -m pip` も検査する。
- 入力JSONの不正、クォートの不整合など解析できない場合は何も出力せず通す（RTKアダプターと同じ失敗時の方針）。

## 対象 / Guarded Commands

| コマンド | 拒否するサブコマンド |
|---|---|
| npm | install, i, add, ci, update, up |
| pnpm | install, i, add, update, up |
| yarn | install, add, up, upgrade |
| pip / python -m pip | install |
| uv | add, sync, lock, pip install/sync/compile, tool install |
| cargo | add, install |
| go | get, install |
| gem / bundle | install |

## 既知の制約と残余リスク / Limitations

- **poetry は対象外。** `sfw` のTLS仲介のため `sfw poetry lock` が `pypi.org` に接続できない。poetry の取得は `sfw` なしで実行されるため、Hookでは守れない。
- `npx` `uvx` `pnpm dlx` `bunx`、`uv run --with`、`brew` は対象外（ad hocなパッケージ取得として残る）。
- Claude Code経由のBashにのみ効く。手動で打つコマンドやCodexには効かない（Codex用は別途）。
- `sfw` は実行のたびに最新のsfwバイナリをダウンロードする。守る側のツールが版固定されていない更新を取り込む点は、このHookでは解決しない。
- バージョンのexact固定（`==` `@x.y.z`）はHookでは検査せず、メッセージで促すのみ。

## 確認 / Verification

```bash
uv run pytest tests/test_sfw_hook.py
```

```bash
echo '{"tool_input":{"command":"npm install pkg@1.0.0"}}' | python3 ~/.claude/hooks/sfw_pre_tool_use.py
```

出力が `permissionDecision: deny` を含めば有効。`sfw npm install pkg@1.0.0` を渡した場合は出力なし。
