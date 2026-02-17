"""Shared pytest fixtures for multikit tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory for testing."""
    return tmp_path / "project"


@pytest.fixture
def initialized_project(project_dir: Path) -> Path:
    """Create an initialized multikit project (with dirs and config)."""
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / ".github" / "agents").mkdir(parents=True, exist_ok=True)
    (project_dir / ".github" / "prompts").mkdir(parents=True, exist_ok=True)

    config_content = (
        "[multikit]\n"
        'version = "0.1.0"\n'
        'registry_url = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"\n'
        "\n"
    )
    (project_dir / "multikit.toml").write_text(config_content, encoding="utf-8")
    return project_dir


@pytest.fixture
def sample_manifest() -> dict:
    """Return a sample kit manifest dict."""
    return {
        "name": "testkit",
        "version": "1.0.0",
        "description": "Test design and coverage agents",
        "agents": [
            "testkit.testdesign.agent.md",
            "testkit.testcoverage.agent.md",
        ],
        "prompts": [
            "testkit.testdesign.prompt.md",
            "testkit.testcoverage.prompt.md",
        ],
    }


@pytest.fixture
def sample_registry() -> dict:
    """Return a sample registry dict."""
    return {
        "kits": [
            {
                "name": "testkit",
                "version": "1.0.0",
                "description": "Test design and coverage agents",
            },
            {
                "name": "gitkit",
                "version": "1.0.0",
                "description": "Git commit agents",
            },
        ]
    }


SAMPLE_AGENT_CONTENT = "# Test Agent\n\nThis is a sample agent file.\n"
SAMPLE_PROMPT_CONTENT = "# Test Prompt\n\nThis is a sample prompt file.\n"
