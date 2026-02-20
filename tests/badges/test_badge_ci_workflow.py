"""Contract tests for badge-related CI workflow coupling."""

from __future__ import annotations

from pathlib import Path


def _ci_workflow() -> str:
    repo_root = Path(__file__).resolve().parents[2]
    return (repo_root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")


def test_ci_has_tox_test_step() -> None:
    ci = _ci_workflow()
    assert "name: Run tests with tox" in ci
    assert "run: tox" in ci


def test_ci_has_coverage_step_coupled_to_test_job() -> None:
    ci = _ci_workflow()
    assert "name: Run coverage and generate report" in ci
    assert "run: tox -e coverage" in ci
    assert "if: matrix.python-version == '3.13'" in ci


def test_ci_has_codecov_upload_step() -> None:
    ci = _ci_workflow()
    assert "name: Upload coverage to Codecov" in ci
    assert "uses: codecov/codecov-action@v4" in ci
    assert "files: ./coverage.xml" in ci
