"""Tests for multikit init command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from multikit.commands.init import handler as init_handler
from multikit.utils.toml_io import load_config


class TestInitCommand:
    """Tests for the init command handler."""

    def test_init_empty_directory(self, project_dir: Path) -> None:
        """Init creates all required dirs and config in an empty directory."""
        project_dir.mkdir(parents=True, exist_ok=True)
        init_handler(str(project_dir))

        assert (project_dir / ".github" / "agents").is_dir()
        assert (project_dir / ".github" / "prompts").is_dir()
        assert (project_dir / "multikit.toml").is_file()

    def test_init_creates_default_config(self, project_dir: Path) -> None:
        """Init creates a valid default config."""
        project_dir.mkdir(parents=True, exist_ok=True)
        init_handler(str(project_dir))

        config = load_config(project_dir)
        assert config.version == "0.1.0"
        assert "raw.githubusercontent.com" in config.registry_url
        assert config.kits == {}

    def test_init_idempotent(self, project_dir: Path) -> None:
        """Running init twice does not break anything."""
        project_dir.mkdir(parents=True, exist_ok=True)
        init_handler(str(project_dir))

        # Write something to agents dir to verify it's preserved
        test_file = project_dir / ".github" / "agents" / "existing.agent.md"
        test_file.write_text("existing content", encoding="utf-8")

        # Run init again
        init_handler(str(project_dir))

        # Existing file should be preserved
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == "existing content"

    def test_init_preserves_existing_config(self, project_dir: Path) -> None:
        """Init does not overwrite an existing multikit.toml."""
        project_dir.mkdir(parents=True, exist_ok=True)
        config_path = project_dir / "multikit.toml"
        config_path.write_text('[multikit]\nversion = "9.9.9"\n', encoding="utf-8")

        init_handler(str(project_dir))

        config = load_config(project_dir)
        assert config.version == "9.9.9"

    def test_init_existing_github_dir(self, project_dir: Path) -> None:
        """Init adds missing subdirs even if .github/ exists."""
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / ".github").mkdir()

        init_handler(str(project_dir))

        assert (project_dir / ".github" / "agents").is_dir()
        assert (project_dir / ".github" / "prompts").is_dir()

    def test_init_default_path(self, tmp_path: Path, monkeypatch) -> None:
        """Init defaults to current working directory."""
        monkeypatch.chdir(tmp_path)
        init_handler()

        assert (tmp_path / ".github" / "agents").is_dir()
        assert (tmp_path / ".github" / "prompts").is_dir()
        assert (tmp_path / "multikit.toml").is_file()

    def test_init_permission_error(self, tmp_path: Path) -> None:
        """Init reports permission error gracefully."""
        with patch(
            "multikit.commands.init.Path.mkdir",
            side_effect=PermissionError("denied"),
        ):
            with pytest.raises(SystemExit) as exc_info:
                init_handler(str(tmp_path))
            assert exc_info.value.code == 1

    def test_init_os_error(self, tmp_path: Path) -> None:
        """Init reports OS error gracefully."""
        with patch(
            "multikit.commands.init.Path.mkdir",
            side_effect=OSError("disk full"),
        ):
            with pytest.raises(SystemExit) as exc_info:
                init_handler(str(tmp_path))
            assert exc_info.value.code == 1
