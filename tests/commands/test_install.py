"""Tests for multikit install command."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from multikit.commands.install import handler as install_handler
from multikit.utils.toml_io import load_config

BASE_URL = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

SAMPLE_MANIFEST = {
    "name": "testkit",
    "version": "1.0.0",
    "description": "Test kit",
    "agents": ["testkit.testdesign.agent.md"],
    "prompts": ["testkit.testdesign.prompt.md"],
}

AGENT_CONTENT = "# Test Agent\nSample agent content.\n"
PROMPT_CONTENT = "# Test Prompt\nSample prompt content.\n"


class TestInstallCommandFresh:
    """Tests for fresh kit installation."""

    @respx.mock
    def test_install_fresh(self, initialized_project: Path, monkeypatch) -> None:
        """Install a kit on a fresh project."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        install_handler("testkit")

        # Verify files installed
        agent_file = (
            initialized_project / ".github" / "agents" / "testkit.testdesign.agent.md"
        )
        prompt_file = (
            initialized_project / ".github" / "prompts" / "testkit.testdesign.prompt.md"
        )
        assert agent_file.exists()
        assert agent_file.read_text(encoding="utf-8") == AGENT_CONTENT
        assert prompt_file.exists()

        # Verify config updated
        config = load_config(initialized_project)
        assert config.is_installed("testkit")
        kit = config.get_kit("testkit")
        assert kit is not None
        assert kit.version == "1.0.0"
        assert "agents/testkit.testdesign.agent.md" in kit.files


class TestInstallCommandErrors:
    """Tests for install error handling."""

    @respx.mock
    def test_install_kit_not_found(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install fails gracefully for unknown kit."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/nonexistent/manifest.json").mock(
            return_value=httpx.Response(404)
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler("nonexistent")
        assert exc_info.value.code == 1

    @respx.mock
    def test_install_network_error(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install fails gracefully on network error."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler("testkit")
        assert exc_info.value.code == 1

    @respx.mock
    def test_install_file_download_failure(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install rolls back atomically when a file download fails."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(404)
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler("testkit")
        assert exc_info.value.code == 1

        # Verify no files were installed (atomic rollback)
        agent_file = (
            initialized_project / ".github" / "agents" / "testkit.testdesign.agent.md"
        )
        assert not agent_file.exists()


class TestInstallCommandForce:
    """Tests for install with --force flag."""

    @respx.mock
    def test_install_force_overwrites(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install --force overwrites existing files without prompting."""
        monkeypatch.chdir(initialized_project)

        # Pre-install a file with different content
        agent_dir = initialized_project / ".github" / "agents"
        agent_dir.mkdir(parents=True, exist_ok=True)
        existing = agent_dir / "testkit.testdesign.agent.md"
        existing.write_text("old content", encoding="utf-8")

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        install_handler("testkit", force=True)

        assert existing.read_text(encoding="utf-8") == AGENT_CONTENT


class TestInstallCommandConflicts:
    """Tests for install with interactive conflict resolution."""

    @respx.mock
    def test_install_conflict_yes(self, initialized_project: Path, monkeypatch) -> None:
        """Install with conflict: user answers 'y' to overwrite."""
        monkeypatch.chdir(initialized_project)

        agents_dir = initialized_project / ".github" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            "old content\n", encoding="utf-8"
        )

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        monkeypatch.setattr("multikit.commands.install.prompt_overwrite", lambda _: "y")
        install_handler("testkit")

        assert (agents_dir / "testkit.testdesign.agent.md").read_text(
            encoding="utf-8"
        ) == AGENT_CONTENT

    @respx.mock
    def test_install_conflict_no(self, initialized_project: Path, monkeypatch) -> None:
        """Install with conflict: user answers 'n' to skip."""
        monkeypatch.chdir(initialized_project)

        agents_dir = initialized_project / ".github" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            "old content\n", encoding="utf-8"
        )

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        monkeypatch.setattr("multikit.commands.install.prompt_overwrite", lambda _: "n")
        install_handler("testkit")

        assert (agents_dir / "testkit.testdesign.agent.md").read_text(
            encoding="utf-8"
        ) == "old content\n"

    @respx.mock
    def test_install_conflict_all(self, initialized_project: Path, monkeypatch) -> None:
        """Install with conflict: user answers 'a' to overwrite all."""
        monkeypatch.chdir(initialized_project)

        agents_dir = initialized_project / ".github" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            "old content\n", encoding="utf-8"
        )

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        monkeypatch.setattr("multikit.commands.install.prompt_overwrite", lambda _: "a")
        install_handler("testkit")

        assert (agents_dir / "testkit.testdesign.agent.md").read_text(
            encoding="utf-8"
        ) == AGENT_CONTENT

    @respx.mock
    def test_install_conflict_skip_all(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install with conflict: user answers 's' to skip all."""
        monkeypatch.chdir(initialized_project)

        agents_dir = initialized_project / ".github" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            "old content\n", encoding="utf-8"
        )

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        monkeypatch.setattr("multikit.commands.install.prompt_overwrite", lambda _: "s")
        install_handler("testkit")

        assert (agents_dir / "testkit.testdesign.agent.md").read_text(
            encoding="utf-8"
        ) == "old content\n"

    @respx.mock
    def test_install_unchanged_local(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install with existing file that matches remote (no conflict)."""
        monkeypatch.chdir(initialized_project)

        agents_dir = initialized_project / ".github" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "testkit.testdesign.agent.md").write_text(
            AGENT_CONTENT, encoding="utf-8"
        )

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        install_handler("testkit")

        config = load_config(initialized_project)
        assert config.is_installed("testkit")

    @respx.mock
    def test_install_config_corrupted(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install fails on corrupted config."""
        monkeypatch.chdir(initialized_project)
        (initialized_project / "multikit.toml").write_text(
            "invalid [[[", encoding="utf-8"
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler("testkit")
        assert exc_info.value.code == 1

    @respx.mock
    def test_install_http_500(self, initialized_project: Path, monkeypatch) -> None:
        """Install handles non-404 HTTP error on manifest."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(500)
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler("testkit")
        assert exc_info.value.code == 1

    @respx.mock
    def test_install_empty_kit_warning(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Install warns about empty kit."""
        monkeypatch.chdir(initialized_project)

        empty_manifest = {
            "name": "empty-kit",
            "version": "1.0.0",
            "agents": [],
            "prompts": [],
        }
        respx.get(f"{BASE_URL}/empty-kit/manifest.json").mock(
            return_value=httpx.Response(200, json=empty_manifest)
        )

        install_handler("empty-kit")

        captured = capsys.readouterr()
        assert "declares no files" in captured.err

    @respx.mock
    def test_install_file_http_500(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install handles non-404 HTTP error on file download."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(500)
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler("testkit")
        assert exc_info.value.code == 1

    @respx.mock
    def test_install_file_network_error(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install handles network error on file download."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler("testkit")
        assert exc_info.value.code == 1

    @respx.mock
    def test_install_custom_registry(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install uses custom registry URL."""
        monkeypatch.chdir(initialized_project)
        custom_url = "https://example.com/custom/kits"

        respx.get(f"{custom_url}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{custom_url}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{custom_url}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        install_handler("testkit", registry=custom_url)

        config = load_config(initialized_project)
        assert config.is_installed("testkit")

    @respx.mock
    def test_install_handles_internal_staging_exception(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Install reports failure when staging/move phase raises unexpectedly."""
        monkeypatch.chdir(initialized_project)

        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=SAMPLE_MANIFEST)
        )
        respx.get(f"{BASE_URL}/testkit/agents/testkit.testdesign.agent.md").mock(
            return_value=httpx.Response(200, text=AGENT_CONTENT)
        )
        respx.get(f"{BASE_URL}/testkit/prompts/testkit.testdesign.prompt.md").mock(
            return_value=httpx.Response(200, text=PROMPT_CONTENT)
        )

        def _raise_runtime(*_args, **_kwargs):
            raise RuntimeError("boom")

        monkeypatch.setattr(
            "multikit.commands.install.move_staged_files", _raise_runtime
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler("testkit")
        assert exc_info.value.code == 1


class TestInstallCommandInteractive:
    """Tests for install interactive flow branches."""

    def test_install_interactive_registry_fetch_failure(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Interactive install exits when registry cannot be fetched."""
        monkeypatch.chdir(initialized_project)

        def _raise_registry(_url: str):
            raise RuntimeError("registry unavailable")

        monkeypatch.setattr("multikit.commands.install.fetch_registry", _raise_registry)

        with pytest.raises(SystemExit) as exc_info:
            install_handler()
        assert exc_info.value.code == 1

    def test_install_interactive_no_selection_exits_zero(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Interactive install exits cleanly when user selects nothing."""
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.install.fetch_registry", lambda _url: object()
        )
        monkeypatch.setattr(
            "multikit.commands.install.select_installable_kits",
            lambda _config, _registry: [],
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler()
        assert exc_info.value.code == 0

    def test_install_interactive_partial_failure_exits_one(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Interactive install exits non-zero when one of selected kits fails."""
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.install.fetch_registry", lambda _url: object()
        )
        monkeypatch.setattr(
            "multikit.commands.install.select_installable_kits",
            lambda _config, _registry: ["ok-kit", "bad-kit"],
        )

        def _fake_install(name: str, *_args, **_kwargs) -> bool:
            return name != "bad-kit"

        monkeypatch.setattr(
            "multikit.commands.install._install_single_kit", _fake_install
        )

        with pytest.raises(SystemExit) as exc_info:
            install_handler()
        assert exc_info.value.code == 1
