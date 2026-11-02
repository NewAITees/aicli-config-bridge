# グローバル settings.json 整理メモ

## 背景

`C:\Users\perso\.claude\settings.json`（ライブの個人設定）には、他プロジェクト（aituber_test / DataDigger / yadorigi / ollama-swapper / AIBackgroundWorker）作業中に蓄積された `permissions.allow` エントリと、`autoMode.environment` のプロジェクト固有記述が混在していた。

これらはグローバル管理対象（`project-configs/.claude/settings.json`、本リポジトリ正本）には**含めなかった**。理由は、グローバルファイルは全プロジェクトで共有されるため、一つのプロジェクトの事情（パス・ポート・ファイル名）をそこに残すと、無関係なプロジェクトでも誤って有効な許可として適用されてしまうため。

このファイルは、各プロジェクト側の `.claude/settings.local.json`（または該当プロジェクトの `.claude/settings.json`）に移すべき内容の記録。移行作業は、各プロジェクトにアクセスできるセッションで行う必要がある（このリポジトリの作業範囲外のため、ここでは実施していない）。

## プロジェクト別の移行対象

### aituber_test (`C:\analysis2\aituber_test`)
```
Bash(Get-ChildItem -Path "c:\analysis2\aituber_test" -Recurse -Include "*.py", "*.toml")
Bash(Find "c:\analysis2\aituber_test\src" -type f -name "*.py")
Read(//c/analysis2/aituber_test/ukagaka/**)
Bash(node src/scenes/pachinko-draw/debug-early.mjs)
Bash(node src/scenes/pachinko-draw/debug-jam.mjs)
```
`autoMode.environment` の "User-specific" セクション全体（Trusted repo: github.com/NewAITees/aituber_test、ポート50032/11434/31555 等のローカルサービス情報、COEIROINK/Unity関連の信頼範囲）も aituber_test 側に移す。

### DataDigger (`C:\analysis2\DataDigger`)
```
Bash(Get-ChildItem -Path "c:\analysis2\DataDigger" -Force)
Bash(find /c/analysis2/DataDigger/app/backend/src -type f | sort)
Read(//c/analysis2/DataDigger/app/backend/src/**)
Bash(find /c/analysis2/DataDigger/app/frontend/src -type f | sort)
Read(//c/analysis2/DataDigger/app/frontend/src/**)
Bash(find /c/analysis2/DataDigger/cases -type d | sort)
Read(//c/analysis2/DataDigger/cases/**)
Bash(find /c/analysis2/DataDigger/cases/s-01 -type f | sort)
Read(//c/analysis2/DataDigger/cases/s-01/**)
Bash(find /c/analysis2/DataDigger/docs -type f | sort)
Read(//c/analysis2/DataDigger/docs/**)
Bash(find /c/analysis2/DataDigger/cases/case001 -type f | sort)
Read(//c/analysis2/DataDigger/cases/case001/**)
Bash(find /c/analysis2/DataDigger -name "*.json" -type f | grep -E "\(vite|webpack|tsconfig|electron\)" | sort)
Read(//c/analysis2/DataDigger/**)
```

### yadorigi (`C:\analysis2\yadorigi`)
```
Bash(find /c/analysis2/yadorigi -name "*.py" -not -path "*/.venv/*" | sort)
Read(//c/analysis2/yadorigi/**)
Bash(OLLAMA_HOST=http://localhost:11436 nohup uv run python -m inference.server)
Bash(OLLAMA_HOST=http://127.0.0.1:11436 nohup uv run python -m inference.server)
Bash(curl -s -m 90 -X POST http://localhost:54217/ingest -F "file=@/tmp/note1.md")
Bash(time curl -s -m 60 -w '\nHTTP_STATUS:%{http_code}\n' -X POST http://localhost:54217/metabolize -H 'Content-Type: application/json' --data-binary @/tmp/search_req.json)
Bash(curl -s -m 60 -w '\nHTTP_STATUS:%{http_code}\n' -X POST http://localhost:54217/metabolize -H 'Content-Type: application/json' --data-binary @/tmp/verify_m1.json -o C:/Users/perso/AppData/Local/Temp/verify_m1_out.json)
Bash(curl -s http://localhost:6333/collections/nodes)
Bash(curl -s -m 3 http://127.0.0.1:54217/health)
Bash(curl -s -m 30 -X POST http://127.0.0.1:54217/ingest -F kind= -F scope= -F source_type= -F file=@/tmp/memo.md -v)
Bash(curl -s -m 5 -o /dev/null -w "health: %{http_code}\n" http://127.0.0.1:54217/health)
Bash(rtk read /c/analysis2/yadorigi/.env 2>/dev/null | grep -i ollama *)
Read(//c/analysis2/yadorigi/inference/**)
Bash(find /c/analysis2/yadorigi/test_data -maxdepth 1 -iname "*.md" | head -5 > /tmp/first5.txt *)
Read(//c/analysis2/yadorigi/test_data/**)
Bash(find /c/analysis2/yadorigi/tests -name "*.py" | sort)
Read(//c/analysis2/yadorigi/tests/**)
Bash(timeout 5 docker inspect yadorigi-qdrant-1 --format '{{.State.Status}} {{.State.Error}}')
Bash(timeout 15 docker start yadorigi-qdrant-1)
PowerShell(Get-Content -Path "$env:TEMP\yadorigi_server7.log" -Encoding UTF8 -Tail 30)
PowerShell(Get-Content -Path "$env:TEMP\yadorigi_hook_start.log" -Encoding UTF8 -Tail 80)
```

### ollama-swapper (`C:\analysis2\ollama-swapper`)
```
Bash(cd /c/analysis2/ollama-swapper *)
Read(//c/analysis2/ollama-swapper/**)
```

### AIBackgroundWorker (`C:\analysis2\AIBackgroundWorker`)
```
Read(//c/analysis2/AIBackgroundWorker/apps/**)
Read(//c/analysis2/AIBackgroundWorker/apps/web/**)
```

## グローバルから完全に削除した項目（どこにも移行しない）

これらは特定の一回限りの操作を文字通り固定しただけで、どのプロジェクトでも再利用価値がなく、むしろ誤って再発火すると意味不明な動作になるため削除した。

```
Bash(node "C:/Users/perso/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs" task "y — proceed with the implementation. The user has confirmed. Execute all three phases now." --write --resume-last)
```
→ 過去のワンオフなプロンプト文字列そのものが許可ルールとして固定されてしまっていた。

```
Bash(powershell -Command "Stop-Process -Id 20096 -Force")
```
→ 特定PID（20096）をハードコードしており、二度と一致しない。

```
Bash(python exp.py:*)
Bash(xargs grep -liE "outline")
```
→ 出自不明の一回限りのスクラッチコマンドと判断し、再利用価値なしとして削除（該当プロジェクトが判明した場合はそちらへの移行を検討）。

## autoMode.environment

現状の内容は全てaituber_test固有（trusted repo、ローカルサービスのポート等）だったため、グローバル管理版の `settings.json` には含めていない。aituber_test側で `/auto-mode-setup` を再実行し、そのプロジェクトの `~/.claude/settings.json` ではなくプロジェクト側の設定として持たせることを推奨する。

## 反映時の注意

この移行はまだ**どのプロジェクトのファイルにも書き込んでいない**（このリポジトリの作業範囲外のため）。実際にライブの `~/.claude/settings.json` を本リポジトリ管理版へ切り替える前に、上記の移行対象を該当プロジェクト側へ先に退避すること。
