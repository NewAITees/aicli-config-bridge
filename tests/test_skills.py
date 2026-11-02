"""Tests for portable skill management."""

from pathlib import Path

import pytest

from aicli_config_bridge.skills import SkillManager


def write_skill(path: Path, body: str = "body") -> Path:
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text(f"---\nname: {path.name}\ndescription: test\n---\n{body}\n")
    return path


@pytest.fixture
def manager(tmp_path: Path) -> SkillManager:
    homes = {agent: tmp_path / agent for agent in ("codex", "claude", "opencode")}
    return SkillManager(tmp_path, homes=homes)


def test_shared_skill_is_linked_to_both_agents(manager: SkillManager) -> None:
    source = write_skill(manager.source_root / "shared" / "sample")

    rows = manager.apply()

    assert all(row.status == "linked" for row in rows)
    assert (manager.homes["codex"] / "sample").resolve() == source.resolve()
    assert (manager.homes["claude"] / "sample").resolve() == source.resolve()
    assert (manager.homes["opencode"] / "sample").resolve() == source.resolve()


def test_opencode_variant_isolated_from_other_agents(manager: SkillManager) -> None:
    shared = write_skill(manager.source_root / "shared" / "sample")
    variant = write_skill(manager.source_root / "opencode" / "sample", "opencode")

    manager.apply()

    assert (manager.homes["opencode"] / "sample").resolve() == variant.resolve()
    assert (manager.homes["codex"] / "sample").resolve() == shared.resolve()
    assert (manager.homes["claude"] / "sample").resolve() == shared.resolve()


def test_opencode_conflict_stops_all_changes(manager: SkillManager) -> None:
    write_skill(manager.source_root / "shared" / "sample")
    write_skill(manager.homes["opencode"] / "sample", "local")

    with pytest.raises(FileExistsError, match="opencode:sample"):
        manager.apply()

    assert not (manager.homes["codex"] / "sample").exists()


def test_default_opencode_home_uses_config_directory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    manager = SkillManager(tmp_path)

    assert manager.homes["opencode"] == tmp_path / ".config" / "opencode" / "skills"


def test_agent_variant_overrides_shared(manager: SkillManager) -> None:
    write_skill(manager.source_root / "shared" / "sample", "shared")
    variant = write_skill(manager.source_root / "codex" / "sample", "codex")

    manager.apply()

    assert (manager.homes["codex"] / "sample").resolve() == variant.resolve()
    assert (manager.homes["claude"] / "sample").resolve().parent.name == "shared"


def test_apply_stops_on_existing_conflict(manager: SkillManager) -> None:
    write_skill(manager.source_root / "shared" / "sample")
    write_skill(manager.homes["codex"] / "sample", "local")

    with pytest.raises(FileExistsError, match="codex:sample"):
        manager.apply()


def test_import_adds_new_shared_skill(manager: SkillManager, tmp_path: Path) -> None:
    source = write_skill(tmp_path / "project-skill")

    destination = manager.import_skill(source)

    assert (destination / "SKILL.md").read_text() == (source / "SKILL.md").read_text()


def test_import_rejects_different_existing_skill(manager: SkillManager, tmp_path: Path) -> None:
    source = write_skill(tmp_path / "sample", "new")
    write_skill(manager.source_root / "shared" / "sample", "old")

    with pytest.raises(FileExistsError, match="already differs"):
        manager.import_skill(source)


def test_unreadable_windows_link_is_reported_and_never_overwritten(manager, monkeypatch):
    write_skill(manager.source_root / "shared" / "sample")
    target = manager.homes["codex"] / "sample"
    original_exists = Path.exists

    def exists(path):
        if path == target:
            raise OSError(1920, "unreadable reparse point")
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", exists)
    rows = manager.statuses()
    assert next(row for row in rows if row.agent == "codex").status == "inaccessible"
    with pytest.raises(FileExistsError, match=r"inaccessible.*codex:sample"):
        manager.apply(conflict="backup")
    assert not (manager.homes["opencode"] / "sample").exists()
