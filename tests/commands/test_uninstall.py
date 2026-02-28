"""Tests for multikit uninstall command."""

from __future__ import annotations

from pathlib import Path

import pytest

from multikit.commands.uninstall import handler as uninstall_handler
from multikit.models.config import InstalledKit, MultikitConfig
from multikit.utils.toml_io import load_config, save_config


class TestUninstallCommand:
    """Tests for the uninstall command handler."""

    def test_uninstall_installed_kit(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Uninstall removes files and config entry."""
        monkeypatch.chdir(initialized_project)

        # Create installed files
        agents_dir = initialized_project / ".github" / "agents"
        prompts_dir = initialized_project / ".github" / "prompts"
        agent_file = agents_dir / "testkit.testdesign.agent.md"
        prompt_file = prompts_dir / "testkit.testdesign.prompt.md"
        agent_file.write_text("agent content", encoding="utf-8")
        prompt_file.write_text("prompt content", encoding="utf-8")

        # Save config with kit
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

        uninstall_handler("testkit")

        # Verify files deleted
        assert not agent_file.exists()
        assert not prompt_file.exists()

        # Verify config updated
        config = load_config(initialized_project)
        assert not config.is_installed("testkit")

        captured = capsys.readouterr()
        assert "Uninstalled testkit" in captured.out
        assert "2 files removed" in captured.out

    def test_uninstall_not_installed(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Uninstall fails for non-installed kit."""
        monkeypatch.chdir(initialized_project)

        with pytest.raises(SystemExit) as exc_info:
            uninstall_handler("nonexistent")
        assert exc_info.value.code == 1

    def test_uninstall_file_already_deleted(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Uninstall handles already-deleted files gracefully."""
        monkeypatch.chdir(initialized_project)

        # Save config with kit but don't create the actual files
        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=["agents/testkit.testdesign.agent.md"],
                )
            }
        )
        save_config(initialized_project, config)

        uninstall_handler("testkit")

        captured = capsys.readouterr()
        assert "Uninstalled testkit" in captured.out
        assert "0 files removed" in captured.out

        config = load_config(initialized_project)
        assert not config.is_installed("testkit")

    def test_uninstall_config_corrupted(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Uninstall fails on corrupted config."""
        monkeypatch.chdir(initialized_project)
        (initialized_project / "multikit.toml").write_text(
            "invalid [[[", encoding="utf-8"
        )

        with pytest.raises(SystemExit) as exc_info:
            uninstall_handler("testkit")
        assert exc_info.value.code == 1


class TestUninstallInteractive:
    """Tests for interactive uninstall flow."""

    def test_uninstall_interactive_no_selection_exits_zero(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.uninstall.select_installed_kits",
            lambda _config, action="uninstall": [],
        )

        with pytest.raises(SystemExit) as exc_info:
            uninstall_handler()
        assert exc_info.value.code == 0

    def test_uninstall_interactive_partial_failure_exits_one(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.uninstall.select_installed_kits",
            lambda _config, action="uninstall": ["ok-kit", "bad-kit"],
        )

        def _fake_uninstall(name: str, *_args, **_kwargs) -> bool:
            return name != "bad-kit"

        monkeypatch.setattr(
            "multikit.commands.uninstall._uninstall_single_kit", _fake_uninstall
        )

        with pytest.raises(SystemExit) as exc_info:
            uninstall_handler()
        assert exc_info.value.code == 1


class TestUninstallWrapperFunction:
    """Tests for the sync wrapper function uninstall_handler."""

    def test_uninstall_handler_wrapper_no_args(
        self, initialized_project: Path, monkeypatch
    ) -> None:
        """Test the sync wrapper with no kit name (interactive)."""
        monkeypatch.chdir(initialized_project)
        monkeypatch.setattr(
            "multikit.commands.uninstall.select_installed_kits",
            lambda _config, action="uninstall": [],
        )

        with pytest.raises(SystemExit) as exc_info:
            uninstall_handler()
        assert exc_info.value.code == 0

    def test_uninstall_handler_wrapper_with_kit_name(
        self, initialized_project: Path, monkeypatch, capsys
    ) -> None:
        """Test the sync wrapper with explicit kit name."""
        monkeypatch.chdir(initialized_project)

        # Create installed files and config
        agents_dir = initialized_project / ".github" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        agent_file = agents_dir / "testkit.testdesign.agent.md"
        agent_file.write_text("agent content", encoding="utf-8")

        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    files=["agents/testkit.testdesign.agent.md"],
                )
            }
        )
        save_config(initialized_project, config)

        uninstall_handler("testkit")

        captured = capsys.readouterr()
        assert "Uninstalled testkit" in captured.out
        assert not agent_file.exists()


class TestUninstallConfigCorruption:
    """Tests for config corruption handling in uninstall command."""

    def test_uninstall_corrupted_config_exits_one(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        """Test uninstall handles corrupted config."""
        monkeypatch.chdir(tmp_path)

        # Create corrupted config
        config_path = tmp_path / "multikit.toml"
        config_path.write_text(
            "[multikit\n"  # Invalid TOML
            'version = "0.1.0"\n',
            encoding="utf-8",
        )

        with pytest.raises(SystemExit) as exc_info:
            from multikit.commands.uninstall import handler as uninstall_handler

            uninstall_handler("testkit")
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Corrupted multikit.toml" in captured.err
