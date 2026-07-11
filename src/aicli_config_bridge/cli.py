"""CLI for aicli-config-bridge."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from .setup.manager import LinkSetup

app = typer.Typer(
    name="aicli-config-bridge",
    help="Interactive setup tool for AI CLI configuration links",
    rich_markup_mode="rich",
)

console = Console()


@app.command()
def setup(
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        "-p",
        help="プロジェクトルートディレクトリ",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="変更は行わず、実行内容のみ表示",
    ),
    skip_all: bool = typer.Option(
        False,
        "--skip-all",
        help="すべてスキップ(テスト用)",
    ),
) -> None:
    """リンク設計図に基づいて対話的にセットアップを実行."""
    try:
        setup_manager = LinkSetup(project_root)
        setup_manager.setup_interactive(skip_all=skip_all, dry_run=dry_run)
    except FileNotFoundError as exc:
        console.print(f"[red]❌ {exc}[/red]")
        raise typer.Exit(1) from exc
    except Exception as exc:  # pragma: no cover - safety net
        console.print(f"[red]❌ エラーが発生しました: {exc}[/red]")
        raise typer.Exit(1) from exc


@app.command()
def apply(
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        "-p",
        help="プロジェクトルートディレクトリ",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="変更は行わず、実行内容のみ表示",
    ),
    on_conflict: str = typer.Option(
        "backup",
        "--on-conflict",
        help="競合時の処理: backup / overwrite / skip",
    ),
    ids: Optional[list[str]] = typer.Option(
        None,
        "--id",
        help="適用するリンクID(複数指定可、省略時は全件)",
    ),
) -> None:
    """設計図通りにリンクを非対話で適用（AI向け）."""
    if on_conflict not in {"backup", "overwrite", "skip"}:
        raise typer.BadParameter(
            "backup / overwrite / skip のいずれかを指定してください",
            param_hint="--on-conflict",
        )

    try:
        setup_manager = LinkSetup(project_root)
        results = setup_manager.apply_links(ids=ids, conflict_strategy=on_conflict, dry_run=dry_run)
        if results["errors"]:
            raise typer.Exit(1)
    except FileNotFoundError as exc:
        console.print(f"[red]❌ {exc}[/red]")
        raise typer.Exit(1) from exc
    except Exception as exc:  # pragma: no cover - safety net
        console.print(f"[red]❌ エラーが発生しました: {exc}[/red]")
        raise typer.Exit(1) from exc


@app.command()
def status(
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        "-p",
        help="プロジェクトルートディレクトリ",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="JSON形式で出力(AI向け)",
    ),
) -> None:
    """リンク状態を表示."""
    try:
        setup_manager = LinkSetup(project_root)
        if json_output:
            results = [setup_manager.get_link_status(link) for link in setup_manager.list_links()]
            console.print_json(json.dumps(results, ensure_ascii=False))
        else:
            setup_manager.show_status_table()
    except FileNotFoundError as exc:
        console.print(f"[red]❌ {exc}[/red]")
        raise typer.Exit(1) from exc
    except Exception as exc:  # pragma: no cover - safety net
        console.print(f"[red]❌ エラーが発生しました: {exc}[/red]")
        raise typer.Exit(1) from exc


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        "-p",
        help="プロジェクトルートディレクトリ",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="変更は行わず、実行内容のみ表示",
    ),
) -> None:
    """引数なしで起動した場合は対話メニューを表示."""
    if ctx.invoked_subcommand is not None:
        return

    menu = Prompt.ask(
        "何をしますか?",
        choices=["setup", "status", "unlink", "exit"],
        default="setup",
    )

    setup_manager = LinkSetup(project_root)

    if menu == "setup":
        setup_manager.setup_interactive(dry_run=dry_run)
    elif menu == "status":
        results = setup_manager.show_status_table()
        has_issues = any(row["status"] != "linked" for row in results)
        if has_issues and Confirm.ask("問題が見つかりました。修復しますか?", default=False):
            setup_manager.repair_links(dry_run=dry_run)
    elif menu == "unlink":
        link_ids = [row["id"] for row in setup_manager.show_status_table()]
        if not link_ids:
            console.print("[yellow]解除対象がありません[/yellow]")
            return
        selection = Prompt.ask(
            "解除するリンクID(カンマ区切り) または all",
            default="all",
        )
        if selection.strip().lower() == "all":
            targets = link_ids
        else:
            targets = [item.strip() for item in selection.split(",") if item.strip()]
        if not targets:
            console.print("[yellow]解除対象がありません[/yellow]")
            return
        if Confirm.ask(f"{len(targets)}件のリンクを解除しますか?", default=False):
            setup_manager.unlink_links(targets, dry_run=dry_run)
    else:
        return


@app.command()
def init(
    name: str = typer.Argument(..., help="プロジェクト名"),
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        "-p",
        help="プロジェクトルートディレクトリ",
    ),
) -> None:
    """新規プロジェクトを初期化し、リンク設計図を作成."""
    project_root.mkdir(parents=True, exist_ok=True)

    links_config = {
        "version": "0.2.0",
        "description": f"{name} のリンク設定",
        "links": [
            {
                "id": "claude-md",
                "name": "Claude プロジェクトコンテキスト",
                "type": "file",
                "source": "project-configs/CLAUDE.md",
                "target": "~/CLAUDE.md",
                "create_if_missing": True,
                "default_content": "# CLAUDE.md\n\n## プロジェクト概要\n\n",
            },
            {
                "id": "gemini-md",
                "name": "Gemini プロジェクトコンテキスト",
                "type": "file",
                "source": "project-configs/GEMINI.md",
                "target": "~/GEMINI.md",
                "create_if_missing": True,
                "default_content": "# GEMINI.md\n\n## プロジェクト概要\n\n",
            },
        ],
    }

    links_file = project_root / "aicli-links.json"
    links_file.write_text(json.dumps(links_config, indent=2, ensure_ascii=False), encoding="utf-8")

    console.print(f"[green]✅ {links_file} を作成しました[/green]")


if __name__ == "__main__":
    app()
