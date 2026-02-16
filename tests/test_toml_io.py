"""Tests for TOML I/O utilities."""

from __future__ import annotations

from pathlib import Path

from multikit.models.config import InstalledKit, MultikitConfig
from multikit.utils.toml_io import (
    create_default_config,
    load_config,
    read_toml,
    save_config,
    write_toml,
)


class TestReadWriteToml:
    """Tests for low-level TOML read/write."""

    def test_write_and_read(self, tmp_path: Path) -> None:
        path = tmp_path / "test.toml"
        data = {"key": "value", "nested": {"inner": 42}}
        write_toml(path, data)
        result = read_toml(path)
        assert result == data

    def test_read_toml_with_sections(self, tmp_path: Path) -> None:
        path = tmp_path / "test.toml"
        path.write_text(
            '[multikit]\nversion = "0.1.0"\n\n'
            '[multikit.kits.testkit]\nversion = "1.0.0"\n',
            encoding="utf-8",
        )
        data = read_toml(path)
        assert data["multikit"]["version"] == "0.1.0"
        assert data["multikit"]["kits"]["testkit"]["version"] == "1.0.0"


class TestLoadConfig:
    """Tests for load_config."""

    def test_load_missing_config_returns_default(self, tmp_path: Path) -> None:
        config = load_config(tmp_path)
        assert config.version == "0.1.0"
        assert config.kits == {}

    def test_load_existing_config(self, tmp_path: Path) -> None:
        config_path = tmp_path / "multikit.toml"
        config_path.write_text(
            "[multikit]\n"
            'version = "0.1.0"\n'
            'registry_url = "https://example.com/kits"\n'
            "\n"
            "[multikit.kits.testkit]\n"
            'version = "1.0.0"\n'
            'source = "remote"\n'
            'files = ["agents/test.agent.md"]\n',
            encoding="utf-8",
        )
        config = load_config(tmp_path)
        assert config.registry_url == "https://example.com/kits"
        assert config.is_installed("testkit")
        kit = config.get_kit("testkit")
        assert kit is not None
        assert kit.version == "1.0.0"
        assert kit.files == ["agents/test.agent.md"]

    def test_load_empty_multikit_section(self, tmp_path: Path) -> None:
        config_path = tmp_path / "multikit.toml"
        config_path.write_text("[multikit]\n", encoding="utf-8")
        config = load_config(tmp_path)
        assert config.kits == {}


class TestSaveConfig:
    """Tests for save_config."""

    def test_save_default_config(self, tmp_path: Path) -> None:
        config = MultikitConfig()
        save_config(tmp_path, config)
        loaded = load_config(tmp_path)
        assert loaded.version == config.version
        assert loaded.registry_url == config.registry_url

    def test_save_config_with_kits(self, tmp_path: Path) -> None:
        config = MultikitConfig(
            kits={
                "testkit": InstalledKit(
                    version="1.0.0",
                    source="remote",
                    files=["agents/test.agent.md", "prompts/test.prompt.md"],
                )
            }
        )
        save_config(tmp_path, config)
        loaded = load_config(tmp_path)
        assert loaded.is_installed("testkit")
        kit = loaded.get_kit("testkit")
        assert kit is not None
        assert kit.files == ["agents/test.agent.md", "prompts/test.prompt.md"]

    def test_save_roundtrip(self, tmp_path: Path) -> None:
        """Verify write → read → write → read is consistent."""
        config = MultikitConfig(
            kits={
                "a": InstalledKit(version="1.0.0", files=["agents/a.agent.md"]),
                "b": InstalledKit(version="2.0.0", files=["prompts/b.prompt.md"]),
            }
        )
        save_config(tmp_path, config)
        loaded = load_config(tmp_path)
        save_config(tmp_path, loaded)
        loaded2 = load_config(tmp_path)
        assert loaded2.kits.keys() == config.kits.keys()


class TestCreateDefaultConfig:
    """Tests for create_default_config."""

    def test_creates_file_if_missing(self, tmp_path: Path) -> None:
        create_default_config(tmp_path)
        assert (tmp_path / "multikit.toml").exists()
        config = load_config(tmp_path)
        assert config.version == "0.1.0"

    def test_does_not_overwrite_existing(self, tmp_path: Path) -> None:
        config_path = tmp_path / "multikit.toml"
        config_path.write_text('[multikit]\nversion = "9.9.9"\n', encoding="utf-8")
        create_default_config(tmp_path)
        config = load_config(tmp_path)
        assert config.version == "9.9.9"
