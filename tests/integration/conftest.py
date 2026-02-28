"""Shared fixtures for Docker-based integration tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REGISTRY_URL: str = os.environ.get("MOCK_REGISTRY_URL", "http://mock-registry")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run ``multikit <args>`` as a subprocess and return the result."""
    result = subprocess.run(
        ["multikit", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )
    return result


def set_registry_url(workspace: Path, url: str) -> None:
    """Patch *registry_url* in an existing ``multikit.toml``."""
    config_path = workspace / "multikit.toml"
    text = config_path.read_text()
    # Replace the default GitHub URL with the mock registry URL
    import re

    text = re.sub(
        r'registry_url\s*=\s*"[^"]*"',
        f'registry_url = "{url}"',
        text,
    )
    config_path.write_text(text)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    """Return a fresh temporary directory to act as the project root."""
    return tmp_path


@pytest.fixture()
def initialized_workspace(workspace: Path) -> Path:
    """Run ``multikit init`` and point registry_url at the mock server."""
    result = run_cli("init", cwd=workspace)
    assert result.returncode == 0, f"init failed: {result.stderr}"
    set_registry_url(workspace, REGISTRY_URL)
    return workspace


@pytest.fixture()
def installed_demokit_workspace(initialized_workspace: Path) -> Path:
    """``multikit init`` + ``multikit install demokit``."""
    result = run_cli(
        "install",
        "demokit",
        "--registry",
        REGISTRY_URL,
        "--force",
        cwd=initialized_workspace,
    )
    assert result.returncode == 0, f"install failed: {result.stderr}"
    return initialized_workspace
