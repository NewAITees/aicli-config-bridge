"""Interactive link setup manager."""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .models import LinkItem, LinkItemType, LinksConfig, LinkStatus


def _detect_platform() -> str:
    """実行プラットフォームを検出する。

    Returns:
        str: "windows" / "wsl" / "darwin" / "linux"
    """
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "darwin"
    try:
        proc_version = Path("/proc/version").read_text(encoding="utf-8").lower()
        if "microsoft" in proc_version:
            return "wsl"
    except OSError:
        pass
    return "linux"


class LinkSetup:
    """リンク設計図からリンクを構築."""

    def __init__(self, project_root: Path) -> None:
        """初期化.

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root.resolve()
        self.config_file = self.project_root / "aicli-links.json"
        self.console = Console()

    def load_config(self) -> LinksConfig:
        """リンク設計図を読み込み.

        Returns:
            LinksConfig: リンク設定

        Raises:
            FileNotFoundError: 設計図ファイルが存在しない
        """
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"リンク設計図が見つかりません: {self.config_file}\n"
                "まず `aicli-config-bridge init` を実行してください。"
            )

        with self.config_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return LinksConfig(**data)

    def setup_interactive(self, skip_all: bool = False, dry_run: bool = False) -> None:
        """対話的セットアップを実行.

        Args:
            skip_all: すべてスキップするか（テスト用）
            dry_run: 変更は行わず、実行内容のみ表示
        """
        config = self.load_config()

        self.console.print(
            Panel.fit(
                f"[bold cyan]リンク設定を読み込みました[/bold cyan]\n対象: {len(config.links)} 件",
                title="セットアップ開始",
            )
        )

        if dry_run:
            self.console.print("[yellow]🧪 dry-run: 変更は行いません[/yellow]")

        results: dict[str, list[Any]] = {
            "created": [],
            "linked": [],
            "skipped": [],
            "errors": [],
        }

        for i, link in enumerate(config.links, 1):
            self.console.print(f"\n{'=' * 60}")
            self.console.print(f"[bold][{i}/{len(config.links)}] {link.name}[/bold]")
            self.console.print(f"{'=' * 60}")

            if skip_all:
                self.console.print("[yellow]⏭️ スキップ[/yellow]")
                results["skipped"].append(link.id)
                continue

            try:
                action = self._process_link(link, dry_run=dry_run)
                results[action].append(link.id)
            except Exception as exc:
                self.console.print(f"[red]❌ エラー: {exc}[/red]")
                results["errors"].append((link.id, str(exc)))

        self._show_summary(results)

    def apply_links(
        self,
        ids: list[str] | None = None,
        conflict_strategy: str = "backup",
        dry_run: bool = False,
    ) -> dict[str, list[Any]]:
        """非対話でリンクを適用（AI向け）.

        Args:
            ids: 適用するリンクID一覧。Noneの場合は全件
            conflict_strategy: 競合時の処理（backup/overwrite/skip）
            dry_run: 変更は行わず、実行内容のみ表示
        """
        if conflict_strategy not in {"backup", "overwrite", "skip"}:
            raise ValueError("競合戦略は backup / overwrite / skip のいずれかです")

        config = self.load_config()
        links = config.links

        if ids is not None:
            link_map = {link.id: link for link in links}
            unknown = [id_ for id_ in ids if id_ not in link_map]
            if unknown:
                self.console.print(f"[yellow]⚠️ 不明なID: {', '.join(unknown)}[/yellow]")
            links = [link_map[id_] for id_ in ids if id_ in link_map]

        if dry_run:
            self.console.print("[yellow]🧪 dry-run: 変更は行いません[/yellow]")

        results: dict[str, list[Any]] = {"created": [], "linked": [], "skipped": [], "errors": []}

        for link in links:
            try:
                action = self._process_link_non_interactive(
                    link, conflict_strategy=conflict_strategy, dry_run=dry_run
                )
                results[action].append(link.id)
            except Exception as exc:
                self.console.print(f"[red]❌ {link.id}: {exc}[/red]")
                results["errors"].append((link.id, str(exc)))

        self._show_summary(results)
        return results

    def list_links(self) -> list[LinkItem]:
        """リンク一覧を取得."""
        return self.load_config().links

    def get_link_map(self) -> dict[str, LinkItem]:
        """リンクIDとリンク情報のマップを取得."""
        return {link.id: link for link in self.list_links()}

    def get_link_status(self, link: LinkItem) -> dict[str, str]:
        """リンク状態を取得."""
        source = self._resolve_path(link.source)
        target = self._resolve_path(self._get_target_str(link))

        if not source.exists():
            status = LinkStatus.MISSING_SOURCE
        elif target.is_symlink():
            link_target = target.resolve()
            if link_target == source and link_target.exists():
                status = LinkStatus.LINKED
            elif not link_target.exists():
                status = LinkStatus.BROKEN_LINK
            else:
                status = LinkStatus.WRONG_LINK
        elif target.exists():
            status = LinkStatus.EXISTING_FILE
        else:
            status = LinkStatus.MISSING_TARGET

        return {
            "id": link.id,
            "name": link.name,
            "source": str(source),
            "target": str(target),
            "status": status.value,
        }

    def show_status_table(self) -> list[dict[str, str]]:
        """リンク状態を表形式で表示."""
        rows = [self.get_link_status(link) for link in self.list_links()]

        table = Table(title="リンク状態")
        table.add_column("ID")
        table.add_column("名前")
        table.add_column("状態")
        table.add_column("ターゲット")

        for row in rows:
            table.add_row(row["id"], row["name"], row["status"], row["target"])

        self.console.print(table)
        return rows

    def repair_links(self, dry_run: bool = False) -> None:
        """壊れたリンクの修復を試行."""
        for link in self.list_links():
            status = self.get_link_status(link)["status"]
            if status in {LinkStatus.LINKED.value}:
                continue

            source = self._resolve_path(link.source)
            target = self._resolve_path(self._get_target_str(link))

            if not source.exists():
                continue

            if target.exists() or target.is_symlink():
                action = self._handle_existing_target(target, source, dry_run=dry_run)
                if action == "skip":
                    continue

            if dry_run:
                self.console.print(f"[yellow]🧪 修復リンク作成予定: {target} → {source}[/yellow]")
            else:
                self._create_link(source, target)
                self.console.print(f"[green]✅ 修復リンク作成: {target} → {source}[/green]")

    def unlink_links(self, link_ids: list[str], dry_run: bool = False) -> dict[str, list[str]]:
        """指定リンクを解除."""
        results: dict[str, list[str]] = {"removed": [], "skipped": [], "errors": []}
        link_map = self.get_link_map()

        for link_id in link_ids:
            link = link_map.get(link_id)
            if link is None:
                results["errors"].append(link_id)
                continue

            target = self._resolve_path(self._get_target_str(link))
            if not target.exists() and not target.is_symlink():
                results["skipped"].append(link_id)
                continue

            if target.is_symlink():
                source = self._resolve_path(link.source)
                if target.resolve() != source.resolve():
                    self.console.print(
                        f"[yellow]⏭️ 管理対象外のリンクのため解除をスキップ: {target}[/yellow]"
                    )
                    results["skipped"].append(link_id)
                    continue
                if dry_run:
                    self.console.print(f"[yellow]🧪 解除予定: {target}[/yellow]")
                else:
                    target.unlink()
                results["removed"].append(link_id)
                continue

            if not Confirm.ask(f"通常ファイルです。削除しますか? ({target})", default=False):
                results["skipped"].append(link_id)
                continue

            if dry_run:
                self.console.print(f"[yellow]🧪 削除予定: {target}[/yellow]")
            else:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            results["removed"].append(link_id)

        return results

    def _process_link(self, link: LinkItem, dry_run: bool = False) -> str:
        """個別リンクを処理.

        Args:
            link: リンクアイテム

        Returns:
            str: 実行したアクション（created, linked, skipped）
        """
        source = self._resolve_path(link.source)
        target = self._resolve_path(self._get_target_str(link))

        self._show_link_status(link, source, target)

        if not source.exists():
            if link.create_if_missing:
                if not Confirm.ask(
                    f"ソースファイルを作成しますか? ({source})",
                    default=True,
                ):
                    return "skipped"

                if dry_run:
                    self.console.print(f"[yellow]🧪 作成予定: {source}[/yellow]")
                else:
                    self._create_default_file(source, link)
                    self.console.print(f"[green]📝 作成: {source}[/green]")
            else:
                self.console.print(f"[yellow]⚠️ ソースファイルが存在しません: {source}[/yellow]")
                return "skipped"

        if target.exists() or target.is_symlink():
            action = self._handle_existing_target(target, source, dry_run=dry_run)
            if action == "skip":
                return "skipped"

        if dry_run:
            self.console.print(f"[yellow]🧪 リンク作成予定: {target} → {source}[/yellow]")
        else:
            self._create_link(source, target)
            self.console.print(f"[green]✅ リンク作成: {target} → {source}[/green]")

        return "linked"

    def _process_link_non_interactive(
        self,
        link: LinkItem,
        conflict_strategy: str = "backup",
        dry_run: bool = False,
    ) -> str:
        """個別リンクを非対話で処理.

        Args:
            link: リンクアイテム
            conflict_strategy: 競合時の処理（backup/overwrite/skip）
            dry_run: 変更は行わず、実行内容のみ表示

        Returns:
            str: 実行したアクション（created, linked, skipped）
        """
        source = self._resolve_path(link.source)
        target = self._resolve_path(self._get_target_str(link))

        if not source.exists():
            if link.create_if_missing:
                if dry_run:
                    self.console.print(f"[yellow]🧪 作成予定: {source}[/yellow]")
                else:
                    self._create_default_file(source, link)
                    self.console.print(f"[green]📝 作成: {source}[/green]")
            else:
                self.console.print(f"[yellow]⚠️ ソースが存在しません: {source}[/yellow]")
                return "skipped"

        if target.exists() or target.is_symlink():
            if target.is_symlink() and target.resolve() == source.resolve():
                self.console.print(f"[green]✅ 既にリンク済み: {target}[/green]")
                return "skipped"

            if conflict_strategy == "skip":
                self.console.print(f"[yellow]⏭️ スキップ(競合): {target}[/yellow]")
                return "skipped"

            if conflict_strategy == "backup" and not dry_run:
                self._backup_existing(target)

            if dry_run:
                prefix = "バックアップ後に" if conflict_strategy == "backup" else ""
                self.console.print(f"[yellow]🧪 {prefix}削除予定: {target}[/yellow]")
            else:
                if target.is_dir() and not target.is_symlink():
                    shutil.rmtree(target)
                else:
                    target.unlink()

        if dry_run:
            self.console.print(f"[yellow]🧪 リンク作成予定: {target} → {source}[/yellow]")
        else:
            self._create_link(source, target)
            self.console.print(f"[green]✅ リンク作成: {target} → {source}[/green]")

        return "linked"

    def _show_link_status(self, link: LinkItem, source: Path, target: Path) -> None:
        """リンクの現状を表示."""
        table = Table(show_header=False, box=None)
        table.add_column("項目", style="cyan")
        table.add_column("値")

        table.add_row("ID", link.id)
        table.add_row("種類", str(link.type))
        table.add_row("ソース", str(source))
        table.add_row("ターゲット", str(target))

        source_status = "✅ 存在" if source.exists() else "❌ 存在しない"
        target_status = "✅ 存在" if target.exists() else "❌ 存在しない"

        if target.is_symlink():
            link_target = target.resolve()
            if link_target == source:
                target_status = "✅ 正しくリンク済み"
            else:
                target_status = f"⚠️ 別のファイルにリンク: {link_target}"

        table.add_row("ソース状態", source_status)
        table.add_row("ターゲット状態", target_status)

        self.console.print(table)

    def _handle_existing_target(self, target: Path, source: Path, dry_run: bool = False) -> str:
        """既存のターゲットファイルを処理.

        Args:
            target: ターゲットパス
            source: ソースパス

        Returns:
            str: "continue" or "skip"
        """
        if target.is_symlink() and target.resolve() == source:
            self.console.print("[green]✅ 既に正しくリンクされています[/green]")
            return "skip"

        if target.is_symlink():
            link_target = target.resolve()
            self.console.print(
                f"[yellow]⚠️ 既に別のファイルにリンクされています: {link_target}[/yellow]"
            )
        else:
            self.console.print("[yellow]⚠️ ターゲットファイルが既に存在します[/yellow]")

        choice = Prompt.ask(
            "どうしますか?",
            choices=["backup", "overwrite", "skip"],
            default="backup",
        )

        if choice == "skip":
            return "skip"
        if choice == "backup":
            if dry_run:
                self.console.print(f"[yellow]🧪 バックアップ予定: {target}[/yellow]")
            else:
                self._backup_existing(target)

        if dry_run:
            self.console.print(f"[yellow]🧪 既存ターゲット削除予定: {target}[/yellow]")
        else:
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()

        return "continue"

    def _create_link(self, source: Path, target: Path) -> None:
        """シンボリックリンクを作成."""
        target.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(source, target)

    def _create_default_file(self, path: Path, link: LinkItem) -> None:
        """デフォルトファイルを作成."""
        path.parent.mkdir(parents=True, exist_ok=True)

        if link.type == LinkItemType.FILE:
            content = link.default_content or ""
            path.write_text(content, encoding="utf-8")
        else:
            path.mkdir(parents=True, exist_ok=True)

    def _backup_existing(self, path: Path) -> None:
        """既存ファイルをバックアップ."""
        backup_dir = path.parent / ".aicli-backup"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{path.name}.backup_{timestamp}"

        if path.is_dir() and not path.is_symlink():
            shutil.copytree(path, backup_path)
        else:
            shutil.copy2(path, backup_path)

        self.console.print(f"[blue]💾 バックアップ: {backup_path}[/blue]")

    def _get_target_str(self, link: "LinkItem") -> str:  # type: ignore[name-defined]
        """プラットフォームに応じたターゲットパス文字列を返す."""
        current_platform = _detect_platform()
        if current_platform == "windows" and link.target_windows:
            return link.target_windows
        return link.target

    def _resolve_path(self, path_str: str) -> Path:
        """パス文字列を解決（~および%USERPROFILE%を展開）."""
        if path_str.startswith("~"):
            expanded = Path(str(Path.home()) + path_str[1:])
        elif "%USERPROFILE%" in path_str:
            userprofile = os.environ.get("USERPROFILE", str(Path.home()))
            expanded = Path(path_str.replace("%USERPROFILE%", userprofile))
        else:
            expanded = Path(path_str)
        if expanded.is_absolute():
            return expanded.absolute()
        return (self.project_root / expanded).absolute()

    def _show_summary(self, results: dict[str, list[Any]]) -> None:
        """セットアップ結果のサマリーを表示."""
        self.console.print(f"\n{'=' * 60}")
        self.console.print("[bold cyan]セットアップ完了[/bold cyan]")
        self.console.print(f"{'=' * 60}\n")

        table = Table(show_header=False)
        table.add_column("項目", style="cyan")
        table.add_column("件数")

        table.add_row("📝 作成", str(len(results["created"])))
        table.add_row("✅ リンク", str(len(results["linked"])))
        table.add_row("⏭️ スキップ", str(len(results["skipped"])))
        table.add_row("❌ エラー", str(len(results["errors"])))

        self.console.print(table)

        if results["errors"]:
            self.console.print("\n[bold red]エラー詳細:[/bold red]")
            for item_id, error in results["errors"]:
                self.console.print(f"  - {item_id}: {error}")
