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


class TestListExceptionPaths:
    """Tests for specific exception paths in list command."""

    @pytest.mark.asyncio
    async def test_list_registry_http_500(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """List gracefully handles HTTP 500 errors from registry."""
        monkeypatch.chdir(initialized_project)

        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/registry.json", status=500)

            await list_handler()

        captured = capsys.readouterr()
        assert "Could not fetch remote registry" in captured.err
        assert "No kits found" in captured.out

    @pytest.mark.asyncio
    async def test_list_shows_local_only_kits_with_remote(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """List shows locally-installed kits with available remote kits."""
        monkeypatch.chdir(initialized_project)

        # Add a local kit
        config = MultikitConfig(
            kits={
                "local-kit": InstalledKit(
                    version="1.0.0",
                    files=["agents/local.agent.md"],
                )
            }
        )
        save_config(initialized_project, config)

        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/registry.json", payload=SAMPLE_REGISTRY)

            await list_handler()

        captured = capsys.readouterr()
        # Should show both remote and local kits in table
        lines = captured.out.split("\n")
        kit_names = [
            line
            for line in lines
            if "testkit" in line or "gitkit" in line or "local-kit" in line
        ]
        assert len(kit_names) > 0, "Should display kits in table"


class TestListRemoteFetchFailure:
    """Tests for remote registry fetch failure in list command."""

    @pytest.mark.asyncio
    async def test_list_remote_fetch_failure(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Test list handles remote registry fetch failure gracefully."""
        monkeypatch.chdir(initialized_project)

        # Create local kit
        agents_dir = initialized_project / ".github" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            "agent content\n", encoding="utf-8"
        )

        from multikit.models.config import InstalledKit, MultikitConfig
        from multikit.utils.toml_io import save_config

        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=["agents/testkit.testdesign.agent.md"],
                )
            }
        )
        save_config(initialized_project, config)

        # Mock fetch_registry to raise exception
        async def mock_fetch_registry(_url):
            raise Exception("Network error")

        monkeypatch.setattr(
            "multikit.commands.list_cmd.fetch_registry", mock_fetch_registry
        )

        from multikit.commands.list_cmd import handler as list_handler

        await list_handler()

        captured = capsys.readouterr()
        assert "Could not fetch remote registry" in captured.err
        assert "testkit" in captured.out
