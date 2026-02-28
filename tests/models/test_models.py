"""Tests for Pydantic models: Manifest, Registry, MultikitConfig."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from multikit.models.config import (
    InstalledKit,
    MultikitConfig,
    NetworkConfig,
)
from multikit.models.kit import Manifest, Registry, RegistryEntry


class TestManifest:
    """Tests for Manifest model."""

    def test_valid_manifest(self, sample_manifest: dict) -> None:
        m = Manifest(**sample_manifest)
        assert m.name == "testkit"
        assert m.version == "1.0.0"
        assert len(m.agents) == 2
        assert len(m.prompts) == 2

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Manifest(name="", version="1.0.0")

    def test_uppercase_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Manifest(name="TestKit", version="1.0.0")

    def test_name_with_spaces_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Manifest(name="test kit", version="1.0.0")

    def test_hyphenated_name_allowed(self) -> None:
        m = Manifest(name="my-kit", version="1.0.0")
        assert m.name == "my-kit"

    def test_empty_version_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Manifest(name="testkit", version="")

    def test_invalid_agent_extension(self) -> None:
        with pytest.raises(ValidationError):
            Manifest(
                name="testkit",
                version="1.0.0",
                agents=["bad-extension.md"],
            )

    def test_invalid_prompt_extension(self) -> None:
        with pytest.raises(ValidationError):
            Manifest(
                name="testkit",
                version="1.0.0",
                prompts=["bad-extension.md"],
            )

    def test_all_files_property(self, sample_manifest: dict) -> None:
        m = Manifest(**sample_manifest)
        files = m.all_files
        assert len(files) == 4
        assert ("agents", "testkit.testdesign.agent.md") in files
        assert ("prompts", "testkit.testdesign.prompt.md") in files

    def test_empty_agents_and_prompts(self) -> None:
        m = Manifest(name="empty-kit", version="1.0.0")
        assert m.agents == []
        assert m.prompts == []
        assert m.all_files == []

    def test_manifest_from_json(self) -> None:
        json_str = '{"name": "testkit", "version": "1.0.0", "agents": ["x.agent.md"]}'
        m = Manifest.model_validate_json(json_str)
        assert m.name == "testkit"
        assert m.agents == ["x.agent.md"]


class TestRegistryEntry:
    """Tests for RegistryEntry model."""

    def test_valid_entry(self) -> None:
        entry = RegistryEntry(name="testkit", version="1.0.0", description="desc")
        assert entry.name == "testkit"

    def test_optional_description(self) -> None:
        entry = RegistryEntry(name="testkit", version="1.0.0")
        assert entry.description == ""


class TestRegistry:
    """Tests for Registry model."""

    def test_valid_registry(self, sample_registry: dict) -> None:
        r = Registry(**sample_registry)
        assert len(r.kits) == 2

    def test_find_kit_existing(self, sample_registry: dict) -> None:
        r = Registry(**sample_registry)
        entry = r.find_kit("testkit")
        assert entry is not None
        assert entry.name == "testkit"

    def test_find_kit_missing(self, sample_registry: dict) -> None:
        r = Registry(**sample_registry)
        assert r.find_kit("nonexistent") is None

    def test_empty_registry(self) -> None:
        r = Registry()
        assert r.kits == []
        assert r.find_kit("anything") is None

    def test_registry_from_json(self) -> None:
        json_str = '{"kits": [{"name": "a", "version": "1.0.0"}]}'
        r = Registry.model_validate_json(json_str)
        assert len(r.kits) == 1


class TestInstalledKit:
    """Tests for InstalledKit model."""

    def test_valid_installed_kit(self) -> None:
        kit = InstalledKit(
            version="1.0.0",
            source="remote",
            files=["agents/test.agent.md"],
        )
        assert kit.version == "1.0.0"
        assert kit.source == "remote"
        assert len(kit.files) == 1

    def test_defaults(self) -> None:
        kit = InstalledKit(version="1.0.0")
        assert kit.source == "remote"
        assert kit.files == []


class TestMultikitConfig:
    """Tests for MultikitConfig model."""

    def test_default_config(self) -> None:
        config = MultikitConfig()
        assert config.version == "0.1.0"
        assert "raw.githubusercontent.com" in config.registry_url
        assert config.kits == {}

    def test_is_installed(self) -> None:
        config = MultikitConfig(kits={"testkit": InstalledKit(version="1.0.0")})
        assert config.is_installed("testkit") is True
        assert config.is_installed("other") is False

    def test_get_kit(self) -> None:
        kit = InstalledKit(version="1.0.0", files=["agents/a.agent.md"])
        config = MultikitConfig(kits={"testkit": kit})
        assert config.get_kit("testkit") is kit
        assert config.get_kit("other") is None


class TestNetworkConfig:
    """Tests for NetworkConfig model."""

    def test_default_values(self) -> None:

        config = NetworkConfig()
        assert config.max_concurrency == 8
        assert config.max_retries == 3
        assert config.retry_base_delay == 0.5
        assert config.retry_max_delay == 2.0

    def test_custom_values(self) -> None:

        config = NetworkConfig(
            max_concurrency=16,
            max_retries=5,
            retry_base_delay=1.0,
            retry_max_delay=10.0,
        )
        assert config.max_concurrency == 16
        assert config.max_retries == 5
        assert config.retry_base_delay == 1.0
        assert config.retry_max_delay == 10.0

    def test_max_concurrency_bounds(self) -> None:

        # Valid bounds
        config = NetworkConfig(max_concurrency=1)
        assert config.max_concurrency == 1
        config = NetworkConfig(max_concurrency=32)
        assert config.max_concurrency == 32

        # Out of bounds
        with pytest.raises(ValidationError):
            NetworkConfig(max_concurrency=0)
        with pytest.raises(ValidationError):
            NetworkConfig(max_concurrency=33)

    def test_max_retries_bounds(self) -> None:

        # Valid bounds
        config = NetworkConfig(max_retries=0)
        assert config.max_retries == 0
        config = NetworkConfig(max_retries=10)
        assert config.max_retries == 10

        # Out of bounds
        with pytest.raises(ValidationError):
            NetworkConfig(max_retries=-1)
        with pytest.raises(ValidationError):
            NetworkConfig(max_retries=11)

    def test_multikit_config_with_network(self) -> None:

        network = NetworkConfig(max_concurrency=16)
        config = MultikitConfig(network=network)
        assert config.network.max_concurrency == 16
        assert config.network.max_retries == 3  # default
