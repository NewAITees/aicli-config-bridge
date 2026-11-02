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

- Bashコマンドを `&&` `||` `;` `|` `(` `)` `<` `>` で分割し、各セグメントの先頭コマンドを検査する。
- `sfw` で始まらないパッケージ取得系サブコマンドは `permissionDecision: deny` で拒否し、`sfw <コマンド>` での再実行を促す。コマンドの自動書き換えはしない（RTKとの適用順に依存させない）。
- `sfw` として認めるのは、素の `sfw` と `/opt/homebrew/bin/sfw` `/usr/local/bin/sfw` のみ。`./sfw` など他のパスの `sfw` は、`sfw` が無いものとして中身を検査する。
- 先頭の `sudo` `env` `time` `nohup` `command` `exec` `nice` `timeout` `xargs` と、そのオプション（`sudo -u USER`、`env -u NAME`、`xargs -n 1` など）、`VAR=1` 形式の環境変数は読み飛ばして検査する。
- シェルの `-c` を含むフラグ束（`bash -c` `sh -lc` `zsh -ec` など）、`eval`、`$(...)`、バッククォートの中身も検査する。
- `pip` `pip3` `pip3.12` と、`python3.x -m pip` を同じものとして扱う。
- オプション以外の語のどれかが対象サブコマンドなら拒否する（ツールごとのオプションの引数の数を持たず、`npm --prefix test install` のようにオプションの値を挟んだ書き方も拾うため）。そのため `npm run add` のようにスクリプト名が一致した場合も拒否される。`sfw` を前に付ければ通る。
- `env -S 'cmd ...'` の中身は分割して再検査する。シェルのコメントは行頭の語でのみ始まるものとして扱い、`echo a#b; npm ...` のように `#` 以降を無視して取りこぼさない。
- 素の `yarn`（引数なし）はインストールなので拒否する。
- 解析できないコマンド（クォートの不整合など）は、パッケージ取得に見える語の並びを含み、そのセグメントの先頭（環境変数と `sudo` を除く）が信頼する `sfw` でなければ**拒否**する。それ以外は通す。入力JSONそのものが不正な場合は、何も出力せず通す。

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
- `npx` `uvx` `pnpm dlx` `bunx` `pipx`、`uv run --with`、`brew` は対象外（ローカルのバイナリ実行と区別できず誤検出が増えるため、ad hocなパッケージ取得として残る）。
- コマンド文字列の解析による防御であり、悪意をもって隠された呼び出し（変数展開、別スクリプト経由など）は防げない。確実に強制するにはネットワークやプロキシ側で止める必要がある。
- ヒアドキュメントなどで解析不能になり、本文にパッケージ取得に見える語の並びがある場合は、誤って拒否される。`sfw` を前に付けるか、本文を引用符で整える。
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
