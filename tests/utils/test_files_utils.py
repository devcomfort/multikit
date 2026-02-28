"""Tests for file utility functions."""

from __future__ import annotations

import pytest
from pathlib import Path

from multikit.utils.files import (
    atomic_staging,
    async_delete_file,
    async_move_file,
    async_read_file,
    async_write_file,
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

    def test_move_partial_failure(self, tmp_path: Path, monkeypatch) -> None:
        """If shutil.move fails for one file, others still move and exception propagates."""
        target = tmp_path / "target"
        target.mkdir()

        # create two staged files
        with atomic_staging() as staging_dir:
            stage_file(staging_dir, "agents", "a.agent.md", "a")
            stage_file(staging_dir, "agents", "b.agent.md", "b")
            # monkeypatch shutil.move to raise on second file
            import shutil

            orig_move = shutil.move

            def fake_move(src, dst):
                if src.endswith("b.agent.md"):
                    raise PermissionError("deny")
                return orig_move(src, dst)

            monkeypatch.setattr(shutil, "move", fake_move)

            with pytest.raises(PermissionError):
                move_staged_files(
                    staging_dir,
                    target,
                    [("agents", "a.agent.md"), ("agents", "b.agent.md")],
                )

            # first file should have moved before the error
            assert (target / "agents" / "a.agent.md").exists()
            # second file should remain in staging dir
            assert (staging_dir / "agents" / "b.agent.md").exists()

    def test_move_cross_device(self, tmp_path: Path, monkeypatch) -> None:
        """Simulate cross-device link error and ensure subsequent files are untouched."""
        target = tmp_path / "target"
        target.mkdir()

        with atomic_staging() as staging_dir:
            stage_file(staging_dir, "agents", "a.agent.md", "a")
            stage_file(staging_dir, "agents", "b.agent.md", "b")

            import shutil

            orig_move = shutil.move

            def fake_move(src, dst):
                if src.endswith("a.agent.md"):
                    # simulate cross-device link error
                    raise OSError(18, "Cross-device link")
                return orig_move(src, dst)

            monkeypatch.setattr(shutil, "move", fake_move)

            with pytest.raises(OSError):
                move_staged_files(
                    staging_dir,
                    target,
                    [("agents", "a.agent.md"), ("agents", "b.agent.md")],
                )

            # first file should still exist in staging (move never succeeded)
            assert (staging_dir / "agents" / "a.agent.md").exists()
            # second file should likewise remain untouched in staging
            assert (staging_dir / "agents" / "b.agent.md").exists()
            # target directory may contain empty directories (created before move)
            # but no actual file should have been copied
            assert not any(f.is_file() for f in target.rglob("*"))


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


class TestAsyncFileOperations:
    """Tests for async file I/O functions."""

    @pytest.mark.asyncio
    async def test_async_write_file(self, tmp_path: Path) -> None:
        """Test async_write_file creates and writes content."""
        file_path = tmp_path / "test.txt"
        await async_write_file(file_path, "test content")

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == "test content"

    @pytest.mark.asyncio
    async def test_async_write_file_creates_subdirs(self, tmp_path: Path) -> None:
        """Test async_write_file creates parent directories."""
        file_path = tmp_path / "deep" / "nested" / "dir" / "test.txt"
        await async_write_file(file_path, "nested content")

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == "nested content"

    @pytest.mark.asyncio
    async def test_async_read_file(self, tmp_path: Path) -> None:
        """Test async_read_file reads content correctly."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("read test", encoding="utf-8")

        content = await async_read_file(file_path)
        assert content == "read test"

    @pytest.mark.asyncio
    async def test_async_move_file(self, tmp_path: Path) -> None:
        """Test async_move_file moves file to destination."""
        src = tmp_path / "source.txt"
        src.write_text("move content", encoding="utf-8")

        dst = tmp_path / "subdir" / "destination.txt"
        await async_move_file(src, dst)

        assert not src.exists()
        assert dst.exists()
        assert dst.read_text(encoding="utf-8") == "move content"

    @pytest.mark.asyncio
    async def test_async_move_file_creates_target_dir(self, tmp_path: Path) -> None:
        """Test async_move_file creates target directories."""
        src = tmp_path / "source.txt"
        src.write_text("nested move", encoding="utf-8")

        dst = tmp_path / "deep" / "nested" / "destination.txt"
        await async_move_file(src, dst)

        assert not src.exists()
        assert dst.exists()
        assert dst.read_text(encoding="utf-8") == "nested move"

    @pytest.mark.asyncio
    async def test_async_delete_file_existing(self, tmp_path: Path) -> None:
        """Test async_delete_file removes existing file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("delete me", encoding="utf-8")

        result = await async_delete_file(file_path)

        assert result is True
        assert not file_path.exists()

    @pytest.mark.asyncio
    async def test_async_delete_file_missing(self, tmp_path: Path) -> None:
        """Test async_delete_file returns False for non-existent file."""
        file_path = tmp_path / "nonexistent.txt"

        result = await async_delete_file(file_path)

        assert result is False
