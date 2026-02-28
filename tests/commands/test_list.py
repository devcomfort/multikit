"""Tests for multikit list command."""

from __future__ import annotations

import aiohttp
from pathlib import Path
from unittest import mock

import pytest
from aioresponses import aioresponses

from multikit.commands.list_cmd import handler as list_handler
from multikit.models.config import InstalledKit, MultikitConfig
from multikit.utils.toml_io import save_config

BASE_URL = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

SAMPLE_REGISTRY = {
    "kits": [
        {"name": "testkit", "version": "1.0.0", "description": "Test kit"},
        {"name": "gitkit", "version": "1.0.0", "description": "Git kit"},
    ]
}


class TestListCommand:
    """Tests for the list command handler."""

    @pytest.mark.asyncio
    async def test_list_with_installed_kit(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """List shows installed kit status."""
        monkeypatch.chdir(initialized_project)

        # Add a kit to config
        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=["agents/test.agent.md", "prompts/test.prompt.md"],
                )
            }
        )
        save_config(initialized_project, config)

        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/registry.json", payload=SAMPLE_REGISTRY)

            await list_handler()

        captured = capsys.readouterr()
        assert "testkit" in captured.out
        assert "Installed" in captured.out
        assert "gitkit" in captured.out
        assert "Available" in captured.out

    @pytest.mark.asyncio
    async def test_list_empty(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """List with no kits installed and empty registry."""
        monkeypatch.chdir(initialized_project)

        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/registry.json", payload={"kits": []})

            await list_handler()

        captured = capsys.readouterr()
        assert "No kits found" in captured.out

    @pytest.mark.asyncio
    async def test_list_network_error_fallback(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """List gracefully degrades on network error."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=["agents/test.agent.md"],
                )
            }
        )
        save_config(initialized_project, config)

        m = aioresponses()
        with m:
            m.get(
                f"{BASE_URL}/registry.json",
                exception=aiohttp.ClientConnectorError(
                    mock.Mock(), OSError("Connection refused")
                ),
            )

            await list_handler()

        captured = capsys.readouterr()
        assert "testkit" in captured.out
        assert "Installed" in captured.out
        assert "Could not fetch remote registry" in captured.err

    @pytest.mark.asyncio
    async def test_list_config_corrupted(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """List handles corrupted config gracefully by backing up and using defaults."""
        monkeypatch.chdir(initialized_project)
        (initialized_project / "multikit.toml").write_text(
            "invalid [[[", encoding="utf-8"
        )

        # Should not raise, but backup and use defaults
        await list_handler()

        # Check backup was created
        backup_file = initialized_project / "multikit.toml.corrupted.*"
        import glob

        backups = glob.glob(str(backup_file))
        assert len(backups) > 0, "Corrupted config should be backed up"

        # Check warning message
        captured = capsys.readouterr()
        assert "Corrupted multikit.toml detected" in captured.err
        assert "backed up" in captured.err
