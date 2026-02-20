"""Tests for local badge preview command and coverage artifact settings."""

from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib


def _pyproject() -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    return tomllib.loads(content)


def test_badge_preview_script_exists() -> None:
    pyproject = _pyproject()
    scripts = pyproject["tool"]["rye"]["scripts"]
    assert "badge:preview" in scripts


def test_badge_preview_script_emits_coverage_xml() -> None:
    pyproject = _pyproject()
    preview = pyproject["tool"]["rye"]["scripts"]["badge:preview"]
    assert "--cov-report=xml:coverage.xml" in preview


def test_test_cov_script_emits_coverage_xml() -> None:
    pyproject = _pyproject()
    test_cov = pyproject["tool"]["rye"]["scripts"]["test:cov"]
    assert "--cov-report=xml:coverage.xml" in test_cov
