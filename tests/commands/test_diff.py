"""Tests for multikit diff command."""

from __future__ import annotations

import aiohttp
from pathlib import Path
from unittest import mock

import pytest
from aioresponses import aioresponses

from multikit.commands.diff import handler as diff_handler
from multikit.models.config import InstalledKit, MultikitConfig
from multikit.utils.toml_io import save_config

BASE_URL = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

SAMPLE_MANIFEST = {
    "name": "testkit",
    "version": "1.0.0",
    "description": "Test kit",
    "agents": ["testkit.testdesign.agent.md"],
    "prompts": ["testkit.testdesign.prompt.md"],
}


class TestDiffCommand:
    """Tests for the diff command handler."""

    @pytest.mark.asyncio
    async def test_diff_has_changes(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Diff shows changes when local differs from remote."""
        monkeypatch.chdir(initialized_project)

        # Create local files with different content
        agents_dir = initialized_project / ".github" / "agents"
        prompts_dir = initialized_project / ".github" / "prompts"
        agents_dir.mkdir(parents=True, exist_ok=True)
        prompts_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            "old content\n", encoding="utf-8"
        )
        (prompts_dir / "testkit.testdesign.prompt.md").write_text(
            "same content\n", encoding="utf-8"
        )

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
                body="new content\n",
            )
            m.get(
                f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md",
                body="same content\n",
            )

            with pytest.raises(SystemExit) as exc_info:
                await diff_handler("testkit")
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "file(s) changed" in captured.out

    @pytest.mark.asyncio
    async def test_diff_no_changes(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Diff shows no changes when local matches remote."""
        monkeypatch.chdir(initialized_project)

        content = "same content\n"
        agents_dir = initialized_project / ".github" / "agents"
        prompts_dir = initialized_project / ".github" / "prompts"
        agents_dir.mkdir(parents=True, exist_ok=True)
        prompts_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            content, encoding="utf-8"
        )
        (prompts_dir / "testkit.testdesign.prompt.md").write_text(
            content, encoding="utf-8"
        )

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
                f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md", body=content
            )
            m.get(
                f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md", body=content
            )

            await diff_handler("testkit")

        captured = capsys.readouterr()
        assert "No changes detected" in captured.out

    @pytest.mark.asyncio
    async def test_diff_kit_not_installed(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Diff fails for non-installed kit."""
        monkeypatch.chdir(initialized_project)

        with pytest.raises(SystemExit) as exc_info:
            await diff_handler("nonexistent")
        assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_diff_config_corrupted(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Diff handles corrupted config gracefully."""
        monkeypatch.chdir(initialized_project)
        (initialized_project / "multikit.toml").write_text(
            "invalid [[[", encoding="utf-8"
        )

        # Should not raise, but backup and use defaults, then fail because kit not installed
        with pytest.raises(SystemExit) as exc_info:
            await diff_handler("testkit")
        assert exc_info.value.code == 1

        # Check warning message
        captured = capsys.readouterr()
        assert "Corrupted multikit.toml detected" in captured.err
        assert "is not installed" in captured.err

    @pytest.mark.asyncio
    async def test_diff_manifest_404(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Diff fails when remote manifest is 404."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={"testkit": InstalledKit(version="1.0.0", files=[])}
        )
        save_config(initialized_project, config)

        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/testkit/manifest.json", status=404)

            with pytest.raises(SystemExit) as exc_info:
                await diff_handler("testkit")
            assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_diff_manifest_http_500(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Diff fails on non-404 HTTP error."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={"testkit": InstalledKit(version="1.0.0", files=[])}
        )
        save_config(initialized_project, config)

        m = aioresponses()
        with m:
            m.get(
                f"{BASE_URL}/testkit/manifest.json",
                status=500,
                body="Internal Server Error",
            )

            with pytest.raises(SystemExit) as exc_info:
                await diff_handler("testkit")
            assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_diff_manifest_network_error(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Diff fails on network error."""
        monkeypatch.chdir(initialized_project)

        config = MultikitConfig(
            kits={"testkit": InstalledKit(version="1.0.0", files=[])}
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
                await diff_handler("testkit")
            assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_diff_missing_local_file(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Diff reports missing local files."""
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
            m.get(f"{BASE_URL}/testkit/manifest.json", payload=SAMPLE_MANIFEST)
            m.get(
                f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md",
                body="remote content\n",
            )
            m.get(
                f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md",
                body="remote content\n",
            )

            with pytest.raises(SystemExit) as exc_info:
                await diff_handler("testkit")
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Local file missing" in captured.out

    @pytest.mark.asyncio
    async def test_diff_remote_file_fetch_error(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Diff warns on individual file fetch failure."""
        monkeypatch.chdir(initialized_project)

        agents_dir = initialized_project / ".github" / "agents"
        prompts_dir = initialized_project / ".github" / "prompts"
        agents_dir.mkdir(parents=True, exist_ok=True)
        prompts_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            "content\n", encoding="utf-8"
        )
        (prompts_dir / "testkit.testdesign.prompt.md").write_text(
            "content\n", encoding="utf-8"
        )

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
            m.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md", status=404)
            m.get(
                f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md",
                body="content\n",
            )

            await diff_handler("testkit")

        captured = capsys.readouterr()
        assert "Could not fetch remote" in captured.err

    @pytest.mark.asyncio
    async def test_diff_remote_file_network_error(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Diff warns when a file fetch hits a network error."""
        monkeypatch.chdir(initialized_project)

        agents_dir = initialized_project / ".github" / "agents"
        prompts_dir = initialized_project / ".github" / "prompts"
        agents_dir.mkdir(parents=True, exist_ok=True)
        prompts_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            "content\n", encoding="utf-8"
        )
        (prompts_dir / "testkit.testdesign.prompt.md").write_text(
            "content\n", encoding="utf-8"
        )

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
                exception=aiohttp.ClientConnectorError(
                    mock.Mock(), OSError("Connection refused")
                ),
            )
            m.get(
                f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md",
                body="content\n",
            )

            await diff_handler("testkit")

        captured = capsys.readouterr()
        assert "Could not fetch remote" in captured.err


class TestDiffInteractive:
    """Tests for interactive diff flow."""

    @pytest.mark.asyncio
    async def test_diff_interactive_no_selection_exits_zero(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.diff.select_installed_kits",
            lambda _config, action="diff": [],
        )

        with pytest.raises(SystemExit) as exc_info:
            await diff_handler()
        assert exc_info.value.code == 0

    @pytest.mark.asyncio
    async def test_diff_interactive_with_changes_exits_one(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.diff.select_installed_kits",
            lambda _config, action="diff": ["testkit"],
        )

        async def fake_diff(_name, _project_dir, _github_dir):
            return False

        monkeypatch.setattr("multikit.commands.diff._diff_single_kit", fake_diff)

        with pytest.raises(SystemExit) as exc_info:
            await diff_handler()
        assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_diff_interactive_all_clean_exits_zero(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.diff.select_installed_kits",
            lambda _config, action="diff": ["testkit"],
        )

        async def fake_diff(_name, _project_dir, _github_dir):
            return True

        monkeypatch.setattr("multikit.commands.diff._diff_single_kit", fake_diff)

        await diff_handler()
