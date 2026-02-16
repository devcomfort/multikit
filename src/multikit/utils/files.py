"""File utilities: atomic install, file delete, file move."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Generator
from contextlib import contextmanager


@contextmanager
def atomic_staging(prefix: str = "multikit-") -> Generator[Path, None, None]:
    """Context manager providing a temporary directory for atomic file staging.

    Files are written to the temp dir first, then moved to final location.
    On any error, the temp dir is automatically cleaned up.
    """
    with tempfile.TemporaryDirectory(prefix=prefix) as tmp_str:
        yield Path(tmp_str)


def stage_file(staging_dir: Path, subdir: str, filename: str, content: str) -> Path:
    """Write a file to the staging directory.

    Returns the path to the staged file.
    """
    dest = staging_dir / subdir / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return dest


def move_staged_files(
    staging_dir: Path,
    target_dir: Path,
    files: list[tuple[str, str]],
) -> list[str]:
    """Move staged files from staging dir to target .github/ directory.

    Args:
        staging_dir: Temporary directory with downloaded files
        target_dir: Project .github/ directory
        files: List of (subdir, filename) pairs

    Returns:
        List of relative file paths that were installed (relative to .github/)
    """
    installed: list[str] = []
    for subdir, filename in files:
        src = staging_dir / subdir / filename
        if not src.exists():
            continue
        dst = target_dir / subdir / filename
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        installed.append(f"{subdir}/{filename}")
    return installed


def delete_kit_files(github_dir: Path, file_paths: list[str]) -> int:
    """Delete kit files from .github/ directory.

    Args:
        github_dir: The .github/ directory
        file_paths: List of paths relative to .github/ (e.g., "agents/foo.agent.md")

    Returns:
        Number of files actually deleted
    """
    deleted = 0
    for rel_path in file_paths:
        target = github_dir / rel_path
        if target.exists():
            target.unlink()
            deleted += 1
    return deleted
