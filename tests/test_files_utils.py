"""Tests for file utility functions."""

from __future__ import annotations

from pathlib import Path

from multikit.utils.files import (
    atomic_staging,
    delete_kit_files,
    move_staged_files,
    stage_file,
)


class TestAtomicStaging:
    """Tests for atomic_staging context manager."""

    def test_staging_dir_created(self) -> None:
        with atomic_staging() as staging_dir:
            assert staging_dir.is_dir()
            assert "multikit-" in staging_dir.name

    def test_staging_dir_cleaned_on_exit(self) -> None:
        with atomic_staging() as staging_dir:
            path = staging_dir
        assert not path.exists()

    def test_staging_dir_cleaned_on_error(self) -> None:
        path = None
        try:
            with atomic_staging() as staging_dir:
                path = staging_dir
                raise RuntimeError("test error")
        except RuntimeError:
            pass
        assert path is not None
        assert not path.exists()


class TestStageFile:
    """Tests for stage_file."""

    def test_stage_file(self) -> None:
        with atomic_staging() as staging_dir:
            path = stage_file(staging_dir, "agents", "test.agent.md", "content")
            assert path.exists()
            assert path.read_text(encoding="utf-8") == "content"

    def test_stage_creates_subdirs(self) -> None:
        with atomic_staging() as staging_dir:
            path = stage_file(staging_dir, "deep/nested", "file.md", "data")
            assert path.exists()


class TestMoveStaged:
    """Tests for move_staged_files."""

    def test_move_files(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()

        with atomic_staging() as staging_dir:
            stage_file(staging_dir, "agents", "a.agent.md", "agent content")
            stage_file(staging_dir, "prompts", "p.prompt.md", "prompt content")

            installed = move_staged_files(
                staging_dir,
                target,
                [("agents", "a.agent.md"), ("prompts", "p.prompt.md")],
            )

        assert len(installed) == 2
        assert (target / "agents" / "a.agent.md").read_text(
            encoding="utf-8"
        ) == "agent content"

    def test_move_skips_missing(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()

        with atomic_staging() as staging_dir:
            installed = move_staged_files(
                staging_dir,
                target,
                [("agents", "nonexistent.agent.md")],
            )

        assert installed == []


class TestDeleteKitFiles:
    """Tests for delete_kit_files."""

    def test_delete_existing_files(self, tmp_path: Path) -> None:
        github_dir = tmp_path / ".github"
        (github_dir / "agents").mkdir(parents=True)
        (github_dir / "agents" / "a.agent.md").write_text("content")

        deleted = delete_kit_files(github_dir, ["agents/a.agent.md"])
        assert deleted == 1
        assert not (github_dir / "agents" / "a.agent.md").exists()

    def test_delete_missing_files(self, tmp_path: Path) -> None:
        github_dir = tmp_path / ".github"
        github_dir.mkdir()

        deleted = delete_kit_files(github_dir, ["agents/missing.agent.md"])
        assert deleted == 0
