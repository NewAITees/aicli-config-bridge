# Codex Hook Porting Plan

## Goal

2026-11-02のClaude側hook配線作業（`sfw_pre_tool_use.py` / `hook_pre_commands.sh` / `hook_test_gate.sh`の実配線と、そこで見つかったCRLF・Windowsパス関連の不具合修正）を、Codex側（`project-configs/.codex/`）に移植する。

## Current State（移植前の現状）

- Codex側で実際に配線されているHookは`project-configs/.codex/hooks.json`経由の**RTKのみ**（`PreToolUse`、matcher `^Bash$`）
- `hook_pre_commands.sh`（危険コマンド検知=ask）、sfw（パッケージ取得ガード=deny）、`hook_test_gate.sh`（テストゲート=Stop相当）はCodex側に**一つも配線されていない**
- しかし`project-configs/.codex/AGENTS.md`（Codexの運用指示文書）の中では、第5原則やvibe-diffの説明で`hook_pre_commands.sh`の`ask`挙動が**あたかも有効であるかのように言及されている**。これはドキュメントと実装の食い違いなので、移植完了後に表現を実態に合わせて確認すること
- `rtk_pre_tool_use.py` / `rtk_pre_tool_use.mjs`（既存のCodex用RTKアダプタ）は、今回問題になったバグ（jqのCRLF出力、`/bin/bash`固定、Windowsパスのバックスラッシュ、素の`bash`がSystem32のWSLスタブへ解決される問題）を**最初から踏んでいない**。理由は両方とも`jq`やbashサブプロセスを経由せず、`shutil.which("rtk")`（Python）/ `spawnSync(rtkCommand, ...)`（Node、`rtkCommand`はPATH解決）で直接rtkバイナリを呼んでいるため。これは移植時の設計方針として参考にする

## 移植前に必ず確認すること（未確定・要検証）

- **Codexの`PreToolUse`フック契約が`permissionDecision: "ask"`を受理するか**: 確認できているのは`rtk-common-spec.md`に書かれている「`updatedInput`と同時に`permissionDecision: allow`が必須」という点のみ。「ask」や「deny」がClaude同様に効くかは一次情報（Codex本体のドキュメント、または実機での動作確認）で確認してから実装する。効かない場合、危険コマンド検知やsfwの拒否はCodexでは別の表現（たとえば`updatedInput`で安全なコマンドに書き換える、exit codeで中断するなど）を使う必要がある
- Codexに`Stop`相当のフックイベントが存在するか（`hook_test_gate.sh`の移植に必要）。`cross-agent-settings-policy.md`には「`codex`: 明示的なhook設定よりも、スキルと実行ポリシーで代替される箇所が多い」とあるため、Stop相当が無ければテストゲートはスキル側の運用でカバーする設計に切り替える

## 移植対象と方針

### 1. sfw（パッケージ取得ガード）

- `sfw-common-spec.md`に明記されている通り、現状「Codexには効かない（Codex用は別途）」という前提のまま。bashスクリプトをそのまま移植するのではなく、**Python版アダプタを新規作成**する（`rtk_pre_tool_use.py`と同じ設計: 標準ライブラリのみ、`jq`に依存しない）
  - `project-configs/.claude/hooks/sfw_pre_tool_use.py`は既にPython実装なので、ロジック自体は流用できる。Codex用に別ファイルを作るのではなく、**同じスクリプトをCodex用hooks.jsonからも呼ぶ**（出力契約の差だけアダプタで吸収する、RTKと同じパターン）のが望ましい
  - Codexが`permissionDecision: deny`を解釈できるかを先に確認する（上記「確認すること」参照）。できない場合は`updatedInput`で`exit 1`相当のコマンドに書き換える等、別の表現に落とす

### 2. hook_pre_commands.sh（危険コマンド検知）

- 現行はbashスクリプト + jqで実装されている。Codex用に移植する場合、**今回踏んだ2つの不具合を最初から回避する設計**にする
  - jqのCRLF出力問題: `jq`の代わりに標準ライブラリの`json`モジュールでルールを読み込むPython実装に書き換える（sfw同様）。bash+jqのままCodex用アダプタを作ると、Windows上のjq.exeで同じCRLFバグを再現するリスクがある
  - ルールファイル（`hook_pre_commands_rules.json`）は既存の正規表現パターンをそのまま使えるので、Python側で`re.search(pattern, command, re.IGNORECASE)`に置き換える（POSIX文字クラス`[[:alnum:]]`等はPythonの`re`では使えないため、`\w`等への書き換えが必要なことに注意）
  - Codexの`ask`対応が未確認の間は、`permissionDecision`を出力せず、まずはログ出力のみ（no-op）で動作確認してから有効化する

### 3. hook_test_gate.sh（テストゲート）

- Stop相当のイベントがCodexに無ければ、hookとしての移植は見送り、`AGENTS.md`側に「完了報告前にテストを実行する」という運用ルールとして残す（スキルベースの代替、`cross-agent-settings-policy.md`の方針に合わせる）
- Stop相当がある場合は、sfwと同じくPython実装に起こし直す（現行はbash、`jq`非依存だが`pyproject.toml`/`.venv`の存在確認ロジックはそのまま流用可能）

## 共通の落とし穴チェックリスト（今回学んだこと、`tasks/lessons.md`参照）

Codex用に新規スクリプトを書く・既存をbashのまま使う場合は、必ず以下を確認する。

- [ ] `.gitattributes`の`eol=lf`対象に新規ファイルの拡張子が含まれているか（`.py`/`.sh`は既に対象）
- [ ] bashスクリプトでjqを使うなら、`read`で読んだ値の末尾`\r`を`"${var%$'\r'}"`で剥がす処理を入れる（またはPythonに書き換えてこの問題自体を回避する）
- [ ] テストから外部コマンドを呼ぶ場合、`subprocess.run(["bash", ...])`ではなく`shutil.which("bash")`で解決したパスを使う（素の`"bash"`はWindowsでSystem32のWSL起動スタブに解決される）
- [ ] スクリプトパスをサブプロセス引数として渡す場合、`str(path)`ではなく`Path.as_posix()`を使う（MSYS2 bashがバックスラッシュをエスケープ文字として解釈し消してしまう）
- [ ] 新規hookスクリプトは、Agentのフック呼び出し契約（stdin/argv、JSON形式、必須フィールド）を一次情報で確認してから実装し、`echo '{...}' | python3 hook.py`のような形で実際に動作確認する（`lessons.md`の「hook_pre_commands.shが`$1`を読んでいたため実質無効化されていた」と同じ失敗を避ける）

## 検証手順（移植後）

```bash
# WSL/Linux側
echo '{"tool_input":{"command":"npm install left-pad"}}' | python3 ~/.codex/hooks/<新しいsfwアダプタ>.py
echo '{"tool_input":{"command":"rm -rf /tmp/x"}}' | python3 ~/.codex/hooks/<新しいpre_commandsアダプタ>.py
```

```powershell
# Windows側
Get-Content hooks.json | ConvertFrom-Json  # JSON構文確認
node --check "$env:USERPROFILE\.codex\hooks\<新しいアダプタ>.mjs"  # Node版を作る場合
```

- 新規アダプタにも、既存の`test_sfw_hook.py`/`test_pre_commands_hook.py`と同等のテスト（正常系・危険コマンド・敵対的な入力変種）を書く。単体テストだけで「検証済み」と報告しない（`code-review`/`security-review`で敵対的入力のレビューも通す）

## ロールバック

- `project-configs/.codex/hooks.json`に追加したhookエントリを削除すれば即座に無効化できる（RTKエントリには影響しない）
- Python/Nodeアダプタファイル自体は追加するだけなので、`hooks.json`から参照を外せば副作用なく元に戻せる
