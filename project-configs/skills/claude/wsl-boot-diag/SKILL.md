---
name: wsl-boot-diag
description: WSL起動直後にVS Code Remote-WSL接続が切断・killされる、またはWSLの起動が遅い/固まる問題を診断するスキル。「WSLに繋がらない」「VS Code Serverが起動直後にkillされる」「WSLの起動が遅い」と感じたときに使う。systemdサービス/タイマーが起動をブロックしているケースを特定し、恒久修正する。
---

# WSL Boot Diagnostics — WSL起動阻害要因の診断・修正スキル

WSL起動直後にVS Code Remote-WSLの接続が失敗・killされる、あるいはWSL自体の起動が遅いという症状は、多くの場合「起動時に自動実行されるsystemdサービス（特にtimer経由のもの）が、ネットワーク待ちや重い処理でハングし、WSLの起動完了判定をブロックしている」ことが原因である。

## 症状パターン
- VS Code Serverログに `NodeExecServer run: ... wsl.exe -d <distro> -e kill <PID>` が起動直後に出て接続できない
- WSLへの接続やコマンド実行が起動後しばらく遅い/固まる
- `code .` や Remote-WSL拡張が「closed unexpectedly」で失敗する

## 診断手順

1. **WSL起動時のカーネルログを確認**
   ```bash
   wsl -d <distro> -e bash -c "dmesg -T | grep -iE 'oom|kill|timeout|failed to start'"
   ```
   `WaitForBootProcess: /sbin/init failed to start within 10000ms` や `CreateLoginSession: Timed out` が出ていれば、systemdの起動完了が遅延している。

2. **systemd全体の状態を確認**
   ```bash
   wsl -d <distro> -e bash -c "systemctl is-system-running; systemctl --failed --no-pager"
   ```
   `starting` のまま長時間変化しない、または `failed` ユニットがある場合は要調査。

3. **起動をブロックしているジョブを特定（最重要）**
   ```bash
   wsl -d <distro> -e bash -c "systemctl list-jobs --no-pager"
   ```
   `start running` のまま残っているユニットが、起動をブロックしている犯人であることが多い。

4. **犯人ユニットの詳細を確認**
   ```bash
   wsl -d <distro> -e bash -c "systemctl status <unit> --no-pager -l"
   ```
   `Main PID` のプロセス内容、`Active: activating (start) since ... Xs ago` の経過時間を見る。

5. **ユニット定義とスクリプト本体を読む**
   ```bash
   wsl -d <distro> -e bash -c "cat /etc/systemd/system/<unit>.service /etc/systemd/system/<unit>.timer"
   ```
   以下の設定に特に注意する。
   - `After=network.target` のみ（実際にネットワークが使える保証がない。`network-online.target` + `Wants=` が必要）
   - `TimeoutStartSec` が未設定（無限にハングしうる）
   - timerの `Requires=<service>`（起動処理と不要に同期結合している）
   - `Persistent=true`（WSL停止中に取りこぼした分を**起動直後に即実行**してしまう）
   - スクリプト内部で外部サービス（LLM/DB/API等）への接続待ちがないか、タイムアウトが設定されているか

## 修正パターン（恒久対策）

- `After=network.target` → `After=network-online.target` + `Wants=network-online.target`
- `TimeoutStartSec=<秒数>` を追加し、ハングしても起動をブロックし続けないようにする
- timerの `Requires=<service>` は基本削除し疎結合にする
- 重い処理（モデルロード・外部API接続等）が起動直後の自動実行に含まれる場合、`Persistent=true` を見直す。または起動時のみ軽量モード（例: `--pull-only` 相当のフラグ）で実行する分岐を検討する

## 適用手順

1. 対象unitファイルをバックアップ（`.bak`）
2. `sudo tee <path> > /dev/null <<'EOF' ... EOF` で新内容を書き込む（**bashであることを確認してから実行**。Nushell等では動かないので、プロンプトが `$` で終わるbashシェルであることを事前に確認する）
3. `sudo systemctl daemon-reload`
4. 必要なら `sudo systemctl disable --now <timer>` で一旦自動起動を止める
5. `wsl --shutdown` → 再度WSLを起動し、手順1〜3で改善を確認する

## 注意点
- sudoにパスワードが必要な環境が多いため、書き込み系コマンドはユーザー自身のWSLターミナルで実行してもらう（AIはコマンド内容を提示するに留める）
- 変更前に必ずバックアップを取る
- 一度に全部直そうとせず、診断→原因特定→最小限の修正の順で進める
