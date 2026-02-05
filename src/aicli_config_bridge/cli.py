"""CLI for aicli-config-bridge."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

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
