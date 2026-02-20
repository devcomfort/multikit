"""Tests for README badge definitions and format."""

from __future__ import annotations

from pathlib import Path


def _readme() -> str:
    repo_root = Path(__file__).resolve().parents[1]
    return (repo_root / "README.md").read_text(encoding="utf-8")


def test_readme_has_coverage_badge() -> None:
    readme = _readme()
    assert "[![Coverage]" in readme
    assert (
        "https://codecov.io/gh/devcomfort/multikit/branch/main/graph/badge.svg"
        in readme
    )


def test_readme_has_python_support_badge() -> None:
    readme = _readme()
    assert "[![Python Support]" in readme
    assert "python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13" in readme


def test_readme_badges_are_near_top() -> None:
    readme = _readme()
    lines = readme.splitlines()
    # Keep badge visibility in the top section of the document.
    top = "\n".join(lines[:12])
    assert "[![Coverage]" in top
    assert "[![Python Support]" in top
