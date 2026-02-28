"""Tests for TOML I/O utilities."""

from __future__ import annotations

from pathlib import Path

from multikit.models.config import InstalledKit, MultikitConfig, NetworkConfig
from multikit.utils.toml_io import (
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


class TestNetworkConfigSerialization:
    """Tests for network config TOML serialization (T005)."""

    def test_save_load_network_config(self, tmp_path: Path) -> None:

        network = NetworkConfig(
            max_concurrency=16,
            max_retries=5,
            retry_base_delay=1.0,
            retry_max_delay=10.0,
        )
        config = MultikitConfig(network=network)
        save_config(tmp_path, config)
        loaded = load_config(tmp_path)

        assert loaded.network.max_concurrency == 16
        assert loaded.network.max_retries == 5
        assert loaded.network.retry_base_delay == 1.0
        assert loaded.network.retry_max_delay == 10.0

    def test_load_config_without_network_section(self, tmp_path: Path) -> None:
        """Old config files without network section should get defaults."""
        config_path = tmp_path / "multikit.toml"
        config_path.write_text(
            "[multikit]\n"
            'version = "0.1.0"\n'
            'registry_url = "https://example.com/kits"\n',
            encoding="utf-8",
        )
        config = load_config(tmp_path)
        # Should use default NetworkConfig
        assert config.network.max_concurrency == 8
        assert config.network.max_retries == 3

    def test_save_config_preserves_network_defaults(self, tmp_path: Path) -> None:
        """Default network config should be saved."""
        config = MultikitConfig()
        save_config(tmp_path, config)

        # Read raw TOML to verify network section exists
        toml_content = (tmp_path / "multikit.toml").read_text()
        assert "network" in toml_content
        assert "max_concurrency" in toml_content


class TestTomlCorruptionRecovery:
    """Tests for TOML corruption recovery (T048)."""

    def test_load_corrupted_toml_returns_default(self, tmp_path: Path) -> None:
        """Corrupted TOML should return default config."""
        config_path = tmp_path / "multikit.toml"
        config_path.write_text(
            "[multikit\n"  # Invalid TOML - missing closing bracket
            'version = "0.1.0"\n',
            encoding="utf-8",
        )
        config = load_config(tmp_path)
        # Should return default config
        assert config.version == "0.1.0"
        assert config.kits == {}

    def test_load_corrupted_toml_backups_file(self, tmp_path: Path) -> None:
        """Corrupted TOML should be backed up with timestamp."""
        config_path = tmp_path / "multikit.toml"
        config_path.write_text(
            "[multikit\n"  # Invalid TOML
            'version = "0.1.0"\n',
            encoding="utf-8",
        )
        load_config(tmp_path)

        # Check for backup file
        backup_files = list(tmp_path.glob("multikit.toml.corrupted.*"))
        assert len(backup_files) == 1

        # Verify backup contains original corrupted content
        backup_content = backup_files[0].read_text()
        assert "[multikit\n" in backup_content

    def test_load_corrupted_toml_prints_warning(self, tmp_path: Path, capsys) -> None:
        """Corrupted TOML should print warning message."""
        config_path = tmp_path / "multikit.toml"
        config_path.write_text(
            "[multikit\n"  # Invalid TOML
            'version = "0.1.0"\n',
            encoding="utf-8",
        )
        load_config(tmp_path)

        # Check warning message in stderr
        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "Corrupted multikit.toml" in captured.err
        assert "backed up" in captured.err

    def test_load_valid_toml_no_backup(self, tmp_path: Path) -> None:
        """Valid TOML should not create backup file."""
        config_path = tmp_path / "multikit.toml"
        config_path.write_text(
            '[multikit]\nversion = "0.1.0"\n',
            encoding="utf-8",
        )
        load_config(tmp_path)

        # Check no backup file created
        backup_files = list(tmp_path.glob("multikit.toml.corrupted.*"))
        assert len(backup_files) == 0
