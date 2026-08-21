"""Portable skill source-of-truth management."""

from __future__ import annotations

import filecmp
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

AGENTS = ("codex", "claude")


@dataclass(frozen=True)
class SkillStatus:
    """A managed skill and its deployment state."""

    agent: str
    name: str
    source: Path
    target: Path
    status: str


class SkillManager:
    """Manage shared and agent-specific skill sources."""

    def __init__(self, project_root: Path, homes: dict[str, Path] | None = None) -> None:
        self.project_root = project_root.resolve()
        self.source_root = self.project_root / "project-configs" / "skills"
        self.homes = homes or {
            "codex": Path.home() / ".codex" / "skills",
            "claude": Path.home() / ".claude" / "skills",
        }

    def sources_for(self, agent: str) -> dict[str, Path]:
        """Return effective sources, with agent variants overriding shared skills."""
        sources: dict[str, Path] = {}
        for scope in ("shared", agent):
            directory = self.source_root / scope
            if not directory.exists():
                continue
            for skill in sorted(directory.iterdir()):
                if skill.is_dir() and (skill / "SKILL.md").is_file():
                    sources[skill.name] = skill
        return sources

    def statuses(self) -> list[SkillStatus]:
        """Return deployment status for every effective managed skill."""
        rows: list[SkillStatus] = []
        for agent in AGENTS:
            for name, source in self.sources_for(agent).items():
                target = self.homes[agent] / name
                if target.is_symlink() and target.resolve() == source.resolve():
                    status = "linked"
                elif target.is_symlink():
                    status = "wrong_link"
                elif target.exists():
                    status = "existing"
                else:
                    status = "missing"
                rows.append(SkillStatus(agent, name, source, target, status))
        return rows

    def apply(self, conflict: str = "skip", dry_run: bool = False) -> list[SkillStatus]:
        """Link all managed skills into Codex and Claude homes."""
        if conflict not in {"skip", "backup"}:
            raise ValueError("conflict must be skip or backup")

        conflicts = [row for row in self.statuses() if row.status in {"existing", "wrong_link"}]
        if conflicts and conflict == "skip":
            names = ", ".join(f"{row.agent}:{row.name}" for row in conflicts)
            raise FileExistsError(f"conflicting skills: {names}")

        for row in self.statuses():
            if row.status == "linked":
                continue
            if dry_run:
                continue
            row.target.parent.mkdir(parents=True, exist_ok=True)
            if row.target.exists() or row.target.is_symlink():
                self._backup(row.target)
                if row.target.is_dir() and not row.target.is_symlink():
                    shutil.rmtree(row.target)
                else:
                    row.target.unlink()
            row.target.symlink_to(row.source, target_is_directory=True)
        return self.statuses()

    def import_skill(self, source: Path, dry_run: bool = False) -> Path:
        """Import one project skill into the shared source of truth."""
        source = source.resolve()
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"SKILL.md not found: {source}")
        destination = self.source_root / "shared" / source.name
        if destination.exists():
            if self._same_tree(source, destination):
                return destination
            raise FileExistsError(f"shared skill already differs: {destination}")
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination, copy_function=shutil.copy2)
        return destination

    @staticmethod
    def _same_tree(left: Path, right: Path) -> bool:
        comparison = filecmp.dircmp(left, right)
        if comparison.left_only or comparison.right_only or comparison.funny_files:
            return False
        if any(
            not filecmp.cmp(left / name, right / name, shallow=False)
            for name in comparison.common_files
        ):
            return False
        return all(
            SkillManager._same_tree(left / name, right / name) for name in comparison.common_dirs
        )

    @staticmethod
    def _backup(target: Path) -> Path:
        backup_root = target.parent / ".aicli-backup"
        backup_root.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup = backup_root / f"{target.name}.backup_{timestamp}"
        if target.is_symlink():
            backup.symlink_to(target.resolve(), target_is_directory=True)
        else:
            shutil.copytree(target, backup, copy_function=shutil.copy2)
        return backup
