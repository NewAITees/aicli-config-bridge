"""
CLI interface for aicli-config-bridge

このモジュールは aicli-config-bridge の メインCLIインターフェースを提供します。
Typerを使用してコマンドライン引数を処理し、Rich を使用して美しい出力を生成します。

主な機能：
- プロジェクトの初期化 (init)
- 設定の検出 (detect-configs)
- 設定のインポート (import-config)
- 設定のリンク (link, link-all)
- 設定のリンク解除 (unlink)
- リンク状態の確認 (status)
- 設定の検証 (validate)
- コンテキストファイル管理 (import-context, link-context, create-context)

Usage:
    $ aicli-config-bridge init my-project
    $ aicli-config-bridge detect-configs
    $ aicli-config-bridge import-config --tool claude-code
    $ aicli-config-bridge link --tool claude-code
    $ aicli-config-bridge status
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import ConfigManager, ToolType
from .linker import LinkManager
from .tools import ClaudeCodeHandler, GeminiCLIHandler, MarkdownHandler, MCPHandler

app = typer.Typer(
    name="aicli-config-bridge",
    help="A streamlined configuration management tool for AI CLI applications",
    rich_markup_mode="rich",
)

console = Console()


def get_managers() -> tuple[ConfigManager, LinkManager]:
    """設定・リンク管理マネージャーを取得."""
    config_manager = ConfigManager()
    link_manager = LinkManager(config_manager)
    return config_manager, link_manager


def get_tool_handler(tool_name: str) -> ClaudeCodeHandler | GeminiCLIHandler:
    """ツールハンドラを取得."""
    config_manager, link_manager = get_managers()

    if tool_name == "claude-code":
        return ClaudeCodeHandler(config_manager, link_manager)
    elif tool_name == "gemini-cli":
        return GeminiCLIHandler(config_manager, link_manager)
    else:
        raise ValueError(f"サポートされていないツール: {tool_name}")


def version_callback(value: bool) -> None:
    """バージョン情報を表示する."""
    if value:
        console.print(f"aicli-config-bridge version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, help="Show version and exit"),
    ] = None,
) -> None:
    """AI CLI Configuration Bridge - 設定管理ツール."""
    pass


@app.command()
def init(
    project_name: Annotated[Optional[str], typer.Argument(help="プロジェクト名")] = None,
) -> None:
    """新しい設定プロジェクトを初期化する."""
    if project_name is None:
        project_name = typer.prompt("プロジェクト名を入力してください")

    console.print(f"[green]✅ プロジェクト '{project_name}' を初期化しています...[/green]")

    # プロジェクトディレクトリを作成
    project_dir = Path(project_name)
    project_dir.mkdir(exist_ok=True)

    # 設定管理マネージャーを初期化
    config_manager = ConfigManager(project_dir)
    project_config = config_manager.project_config
    project_config.name = project_name
    config_manager.save_project_config(project_config)

    # 基本ディレクトリ構造を作成
    (project_dir / "configs").mkdir(exist_ok=True)
    (project_dir / "backups").mkdir(exist_ok=True)

    console.print(f"[green]✅ プロジェクト '{project_name}' の初期化が完了しました[/green]")


@app.command()
def detect_configs() -> None:
    """既存の設定を検出する."""
    console.print("[blue]🔍 既存の AI CLI 設定を検出しています...[/blue]")

    config_manager, _ = get_managers()
    detected = config_manager.detect_tool_configs()

    table = Table(title="検出された設定")
    table.add_column("ツール")
    table.add_column("設定ファイル")
    table.add_column("状態")

    for tool_type, path in detected.items():
        if path:
            table.add_row(tool_type.value, str(path), "[green]✅ 検出[/green]")
        else:
            table.add_row(tool_type.value, "なし", "[red]❌ 未検出[/red]")

    console.print(table)
    console.print("[green]✅ 設定の検出が完了しました[/green]")


@app.command()
def import_config(
    tool: Annotated[
        Optional[str], typer.Option("--tool", "-t", help="インポートするツール名")
    ] = None,
) -> None:
    """システムから設定をインポートする."""
    if tool is None:
        # 利用可能なツールを表示
        table = Table(title="利用可能なツール")
        table.add_column("ツール名")
        table.add_column("説明")
        table.add_row("claude-code", "Claude Code 設定")
        table.add_row("gemini-cli", "Gemini CLI 設定")
        console.print(table)

        tool = typer.prompt("インポートするツール名を選択してください")

    console.print(f"[blue]📥 {tool} の設定をインポートしています...[/blue]")

    try:
        handler = get_tool_handler(tool)
        config = handler.import_config()
        console.print(f"[green]✅ {tool} の設定インポートが完了しました[/green]")
        console.print(f"インポート先: {config.project_config_path}")
    except FileNotFoundError as e:
        console.print(f"[red]❌ エラー: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ 予期せぬエラー: {e}[/red]")


@app.command()
def link(
    tool: Annotated[Optional[str], typer.Option("--tool", "-t", help="リンクするツール名")] = None,
) -> None:
    """設定をシステムの場所にリンクする."""
    if tool is None:
        tool = typer.prompt("リンクするツール名を入力してください")

    console.print(f"[blue]🔗 {tool} の設定をリンクしています...[/blue]")

    try:
        handler = get_tool_handler(tool)
        success = handler.create_link()
        if success:
            console.print(f"[green]✅ {tool} の設定リンクが完了しました[/green]")
        else:
            console.print(f"[red]❌ {tool} の設定リンクに失敗しました[/red]")
    except Exception as e:
        console.print(f"[red]❌ エラー: {e}[/red]")


@app.command()
def link_all() -> None:
    """すべての設定をリンクする."""
    console.print("[blue]🔗 すべての設定をリンクしています...[/blue]")

    config_manager, _ = get_managers()
    detected = config_manager.detect_tool_configs()

    success_count = 0
    error_count = 0

    for tool_type, path in detected.items():
        if not path:
            console.print(f"[yellow]⚠️ {tool_type.value} の設定が見つかりませんでした[/yellow]")
            continue

        try:
            handler = get_tool_handler(tool_type.value)
            if handler.create_link():
                console.print(f"[green]✅ {tool_type.value} の設定リンクが完了しました[/green]")
                success_count += 1
            else:
                console.print(f"[red]❌ {tool_type.value} の設定リンクに失敗しました[/red]")
                error_count += 1
        except Exception as e:
            console.print(f"[red]❌ {tool_type.value} でエラー: {e}[/red]")
            error_count += 1

    console.print(f"[green]✅ リンク処理完了: 成功 {success_count}件, エラー {error_count}件[/green]")


@app.command()
def unlink(
    tool: Annotated[
        Optional[str], typer.Option("--tool", "-t", help="リンク解除するツール名")
    ] = None,
) -> None:
    """設定のリンクを解除する."""
    if tool is None:
        tool = typer.prompt("リンク解除するツール名を入力してください")

    console.print(f"[yellow]🔓 {tool} の設定リンクを解除しています...[/yellow]")

    try:
        _, link_manager = get_managers()

        # 対象ツールのリンク情報を取得
        links = link_manager.get_all_links()

        if tool not in links:
            console.print(f"[red]❌ {tool} のリンク情報が見つかりません[/red]")
            return

        link_info = links[tool]

        # リンクを削除
        if link_manager.remove_link(link_info.target_path, restore_backup=True):
            console.print(f"[green]✅ {tool} の設定リンク解除が完了しました[/green]")
            console.print(f"バックアップから復元: {link_info.target_path}")
        else:
            console.print(f"[red]❌ {tool} の設定リンク解除に失敗しました[/red]")

    except Exception as e:
        console.print(f"[red]❌ エラー: {e}[/red]")


@app.command()
def status() -> None:
    """リンク状態を確認する."""
    console.print("[blue]📊 設定のリンク状態を確認しています...[/blue]")

    _, link_manager = get_managers()
    links = link_manager.get_all_links()

    table = Table(title="設定リンク状態")
    table.add_column("ツール")
    table.add_column("ステータス")
    table.add_column("設定ファイル")

    for tool_name, link_info in links.items():
        if link_info.status.value == "linked":
            status_text = "[green]✅ リンク済み[/green]"
        elif link_info.status.value == "broken":
            status_text = "[yellow]⚠️ 壊れたリンク[/yellow]"
        else:
            status_text = "[red]❌ 未リンク[/red]"

        table.add_row(tool_name, status_text, str(link_info.target_path))

    console.print(table)


@app.command()
def validate() -> None:
    """設定の整合性を検証する."""
    console.print("[blue]🔍 設定の整合性を検証しています...[/blue]")

    _, link_manager = get_managers()

    # リンクの整合性を検証
    validation_results = link_manager.validate_links()

    table = Table(title="設定の整合性検証結果")
    table.add_column("ツール")
    table.add_column("結果")
    table.add_column("詳細")

    all_valid = True
    for tool_name, is_valid in validation_results.items():
        if is_valid:
            table.add_row(tool_name, "[green]✅ 正常[/green]", "リンクが正常に機能しています")
        else:
            table.add_row(tool_name, "[red]❌ 異常[/red]", "リンクが壊れているか、ファイルが存在しません")
            all_valid = False

    console.print(table)

    if all_valid:
        console.print("[green]✅ すべての設定の検証が完了しました[/green]")
    else:
        console.print("[red]⚠️ 一部の設定に問題があります。修復が必要です[/red]")


@app.command("import-context")
def import_context_command(
    tool: Annotated[
        Optional[str], typer.Option("--tool", "-t", help="インポートするツール名")
    ] = None,
) -> None:
    """コンテキストファイル（CLAUDE.md、GEMINI.md）をインポートする."""
    if tool is None:
        table = Table(title="利用可能なツール")
        table.add_column("ツール名")
        table.add_column("コンテキストファイル")
        table.add_row("claude-code", "CLAUDE.md")
        table.add_row("gemini-cli", "GEMINI.md")
        console.print(table)

        tool = typer.prompt("インポートするツール名を選択してください")

    console.print(f"[blue]📄 {tool} のコンテキストファイルをインポートしています...[/blue]")

    try:
        handler = get_tool_handler(tool)
        if hasattr(handler, "import_context"):
            context_path = handler.import_context()
            console.print(
                f"[green]✅ {tool} のコンテキストファイルインポートが完了しました[/green]"
            )
            console.print(f"インポート先: {context_path}")
        else:
            console.print(f"[red]❌ {tool} はコンテキストファイル管理に対応していません[/red]")
    except FileNotFoundError as e:
        console.print(f"[red]❌ エラー: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ 予期せぬエラー: {e}[/red]")


@app.command("link-context")
def link_context_command(
    tool: Annotated[Optional[str], typer.Option("--tool", "-t", help="リンクするツール名")] = None,
) -> None:
    """コンテキストファイルをシステムの場所にリンクする."""
    if tool is None:
        tool = typer.prompt("リンクするツール名を入力してください")

    console.print(f"[blue]🔗 {tool} のコンテキストファイルをリンクしています...[/blue]")

    try:
        handler = get_tool_handler(tool)
        if hasattr(handler, "create_context_link"):
            success = handler.create_context_link()
            if success:
                console.print(
                    f"[green]✅ {tool} のコンテキストファイルリンクが完了しました[/green]"
                )
            else:
                console.print(f"[red]❌ {tool} のコンテキストファイルリンクに失敗しました[/red]")
        else:
            console.print(f"[red]❌ {tool} はコンテキストファイル管理に対応していません[/red]")
    except Exception as e:
        console.print(f"[red]❌ エラー: {e}[/red]")


@app.command("create-context")
def create_context_command(
    tool: Annotated[Optional[str], typer.Option("--tool", "-t", help="作成するツール名")] = None,
) -> None:
    """デフォルトのコンテキストファイルを作成する."""
    if tool is None:
        tool = typer.prompt("作成するツール名を入力してください")

    console.print(f"[blue]📄 {tool} のデフォルトコンテキストファイルを作成しています...[/blue]")

    try:
        handler = get_tool_handler(tool)
        if hasattr(handler, "create_default_context"):
            context_path = handler.create_default_context()
            console.print(f"[green]✅ {tool} のコンテキストファイル作成が完了しました[/green]")
            console.print(f"作成場所: {context_path}")
        else:
            console.print(f"[red]❌ {tool} はコンテキストファイル管理に対応していません[/red]")
    except Exception as e:
        console.print(f"[red]❌ エラー: {e}[/red]")


if __name__ == "__main__":
    app()
