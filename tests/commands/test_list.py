"""Tests for multikit list command."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

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

    @respx.mock
    def test_list_with_installed_kit(
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

        respx.get(f"{BASE_URL}/registry.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_REGISTRY)
        )

        list_handler()

        captured = capsys.readouterr()
        assert "testkit" in captured.out
        assert "Installed" in captured.out
        assert "gitkit" in captured.out
        assert "Available" in captured.out

    @respx.mock
    def test_list_empty(self, initialized_project: Path, monkeypatch, capsys) -> None:
        """List with no kits installed and empty registry."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/registry.json").mock(
            return_value=httpx.Response(200, json={"kits": []})
        )

        list_handler()

        captured = capsys.readouterr()
        assert "No kits found" in captured.out

    @respx.mock
    def test_list_network_error_fallback(
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

        respx.get(f"{BASE_URL}/registry.json").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        list_handler()

        captured = capsys.readouterr()
        assert "testkit" in captured.out
        assert "Installed" in captured.out
        assert "Could not fetch remote registry" in captured.err

    def test_list_config_corrupted(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """List fails on corrupted config."""
        monkeypatch.chdir(initialized_project)
        (initialized_project / "multikit.toml").write_text(
            "invalid [[[", encoding="utf-8"
        )

        with pytest.raises(SystemExit) as exc_info:
            list_handler()
        assert exc_info.value.code == 1
