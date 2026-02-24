"""Tests for multikit update command."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

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

    @respx.mock
    def test_update_single_installed_kit(
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

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        update_handler("testkit")

        agent_file = (
            initialized_project / ".github" / "agents" / "testkit.testdesign.agent.md"
        )
        prompt_file = (
            initialized_project / ".github" / "prompts" / "testkit.testdesign.prompt.md"
        )
        assert agent_file.exists()
        assert prompt_file.exists()
        assert agent_file.read_text(encoding="utf-8") == AGENT_CONTENT

        new_config = load_config(initialized_project)
        updated_kit = new_config.get_kit("testkit")
        assert updated_kit is not None
        assert updated_kit.version == "1.1.0"

    def test_update_not_installed_kit(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Update fails for kits that are not installed."""
        monkeypatch.chdir(initialized_project)

        with pytest.raises(SystemExit) as exc_info:
            update_handler("unknownkit")
        assert exc_info.value.code == 1

    def test_update_interactive_no_selection_exits_zero(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Interactive mode exits 0 when user selects nothing."""
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.update.select_installed_kits",
            lambda _config, action="update": [],
        )

        with pytest.raises(SystemExit) as exc_info:
            update_handler()
        assert exc_info.value.code == 0

    def test_update_interactive_partial_failure_exits_one(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Interactive mode exits 1 if any selected update fails."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={
                "ok-kit": InstalledKit(version="1.0.0", files=[]),
                "bad-kit": InstalledKit(version="1.0.0", files=[]),
            }
        )
        save_config(initialized_project, config)

        monkeypatch.setattr(
            "multikit.commands.update.select_installed_kits",
            lambda _config, action="update": ["ok-kit", "bad-kit"],
        )

        def _fake_update(name: str, *_args, **_kwargs) -> bool:
            return name != "bad-kit"

        monkeypatch.setattr("multikit.commands.update._update_single_kit", _fake_update)

        with pytest.raises(SystemExit) as exc_info:
            update_handler()
        assert exc_info.value.code == 1

    def test_update_config_corrupted(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Update fails on corrupted config."""
        monkeypatch.chdir(initialized_project)
        (initialized_project / "multikit.toml").write_text(
            "invalid [[[", encoding="utf-8"
        )

        with pytest.raises(SystemExit) as exc_info:
            update_handler("testkit")
        assert exc_info.value.code == 1
