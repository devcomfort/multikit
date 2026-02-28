"""Tests for multikit update command."""

from __future__ import annotations

import aiohttp
from pathlib import Path
from unittest import mock

import pytest
from aioresponses import aioresponses

from multikit.commands.update import handler as update_handler
from multikit.models.config import InstalledKit, MultikitConfig
from multikit.utils.toml_io import load_config, save_config

BASE_URL = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

SAMPLE_MANIFEST = {
    "name": "testkit",
    "version": "1.1.0",
    "description": "Test kit",
    "agents": ["testkit.testdesign.agent.md"],
    "prompts": ["testkit.testdesign.prompt.md"],
}

AGENT_CONTENT = "# Updated Agent\nNew agent content.\n"
PROMPT_CONTENT = "# Updated Prompt\nNew prompt content.\n"


class TestUpdateCommand:
    """Tests for update command behavior."""

    @pytest.mark.asyncio
    async def test_update_single_installed_kit(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Update refreshes an installed kit to latest remote version."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=[
                        "agents/testkit.testdesign.agent.md",
                        "prompts/testkit.testdesign.prompt.md",
                    ],
                )
            }
        )
        save_config(initialized_project, config)

        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/testkit/manifest.json", payload=SAMPLE_MANIFEST)
            m.get(
                f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md",
                body=AGENT_CONTENT,
            )
            m.get(
                f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md",
                body=PROMPT_CONTENT,
            )

            await update_handler("testkit", force=True)

        # Verify version updated
        config = load_config(initialized_project)
        kit = config.get_kit("testkit")
        assert kit is not None
        assert kit.version == "1.1.0"

    @pytest.mark.asyncio
    async def test_update_non_installed_kit(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Update fails for non-installed kit."""
        monkeypatch.chdir(initialized_project)

        with pytest.raises(SystemExit) as exc_info:
            await update_handler("nonexistent")
        assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_update_config_corrupted(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Update handles corrupted config gracefully."""
        monkeypatch.chdir(initialized_project)
        (initialized_project / "multikit.toml").write_text(
            "invalid [[[", encoding="utf-8"
        )

        # Should not raise, but backup and use defaults, then fail because kit not installed
        with pytest.raises(SystemExit) as exc_info:
            await update_handler("testkit")
        assert exc_info.value.code == 1

        # Check warning message
        captured = capsys.readouterr()
        assert "Corrupted multikit.toml detected" in captured.err
        assert "is not installed" in captured.err

    @pytest.mark.asyncio
    async def test_update_manifest_404(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Update fails when remote manifest is 404."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=["agents/testkit.testdesign.agent.md"],
                )
            }
        )
        save_config(initialized_project, config)

        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/testkit/manifest.json", status=404)

            with pytest.raises(SystemExit) as exc_info:
                await update_handler("testkit")
            assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_update_network_error(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Update fails on network error."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=["agents/testkit.testdesign.agent.md"],
                )
            }
        )
        save_config(initialized_project, config)

        m = aioresponses()
        with m:
            m.get(
                f"{BASE_URL}/testkit/manifest.json",
                exception=aiohttp.ClientConnectorError(
                    mock.Mock(), OSError("Connection refused")
                ),
            )

            with pytest.raises(SystemExit) as exc_info:
                await update_handler("testkit")
            assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_update_custom_registry(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Update uses custom registry URL."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=[
                        "agents/testkit.testdesign.agent.md",
                        "prompts/testkit.testdesign.prompt.md",
                    ],
                )
            }
        )
        save_config(initialized_project, config)

        custom_url = "https://example.com/custom/kits"
        m = aioresponses()
        with m:
            m.get(f"{custom_url}/testkit/manifest.json", payload=SAMPLE_MANIFEST)
            m.get(
                f"{custom_url}/testkit/agents/testkit.testdesign.agent.md",
                body=AGENT_CONTENT,
            )
            m.get(
                f"{custom_url}/testkit/prompts/testkit.testdesign.prompt.md",
                body=PROMPT_CONTENT,
            )

            await update_handler("testkit", force=True, registry=custom_url)

        # Verify version updated
        config = load_config(initialized_project)
        kit = config.get_kit("testkit")
        assert kit is not None
        assert kit.version == "1.1.0"


class TestUpdateInteractive:
    """Tests for interactive update flow."""

    @pytest.mark.asyncio
    async def test_update_interactive_no_selection_exits_zero(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Interactive update exits cleanly when user selects nothing."""
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.update.select_installed_kits",
            lambda _config, action="update": [],
        )

        with pytest.raises(SystemExit) as exc_info:
            await update_handler()
        assert exc_info.value.code == 0

    @pytest.mark.asyncio
    async def test_update_interactive_partial_failure_exits_one(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Interactive update exits non-zero when one of selected kits fails."""
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.update.select_installed_kits",
            lambda _config, action="update": ["ok-kit", "bad-kit"],
        )

        async def fake_update(name: str, *_args, **_kwargs) -> bool:
            return name != "bad-kit"

        monkeypatch.setattr("multikit.commands.update._update_single_kit", fake_update)

        with pytest.raises(SystemExit) as exc_info:
            await update_handler()
        assert exc_info.value.code == 1


class TestUpdateWrapperFunction:
    """Tests for the sync wrapper function update_handler."""

    def test_update_handler_wrapper_no_args(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Test the sync wrapper with no kit name (interactive)."""
        from multikit.commands.update import update_handler

        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.update.select_installed_kits",
            lambda _config, action="update": [],
        )

        with pytest.raises(SystemExit) as exc_info:
            update_handler()
        assert exc_info.value.code == 0

    def test_update_handler_wrapper_with_kit_name(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Test the sync wrapper with explicit kit name."""
        from multikit.commands.update import update_handler

        monkeypatch.chdir(initialized_project)

        # Setup installed kit
        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=[
                        "agents/testkit.testdesign.agent.md",
                        "prompts/testkit.testdesign.prompt.md",
                    ],
                )
            }
        )
        save_config(initialized_project, config)

        async def mock_update(*args, **kwargs):
            return True

        monkeypatch.setattr("multikit.commands.update._update_single_kit", mock_update)

        update_handler("testkit", force=False)

    def test_update_handler_wrapper_with_force_flag(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Test the sync wrapper passes force flag correctly."""
        from multikit.commands.update import update_handler

        monkeypatch.chdir(initialized_project)

        # Setup installed kit
        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=["agents/test.agent.md"],
                )
            }
        )
        save_config(initialized_project, config)

        call_args = {}

        async def mock_update(kit_name, project_dir, github_dir, registry_url, force):
            call_args["force"] = force
            return True

        monkeypatch.setattr("multikit.commands.update._update_single_kit", mock_update)

        update_handler("testkit", force=True)
        assert call_args.get("force") is True


class TestUpdateConfigCorruption:
    """Tests for config corruption handling in update command."""

    @pytest.mark.asyncio
    async def test_update_corrupted_config_exits_one(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        """Test update handles corrupted config."""
        monkeypatch.chdir(tmp_path)

        # Create corrupted config
        config_path = tmp_path / "multikit.toml"
        config_path.write_text(
            "[multikit\n"  # Invalid TOML
            'version = "0.1.0"\n',
            encoding="utf-8",
        )

        with pytest.raises(SystemExit) as exc_info:
            from multikit.commands.update import handler as update_handler

            await update_handler("testkit")
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Corrupted multikit.toml" in captured.err
