"""Tests for the remote registry client."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from multikit.models.kit import Manifest, Registry
from multikit.registry.remote import fetch_file, fetch_manifest, fetch_registry

BASE_URL = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"


class TestFetchRegistry:
    """Tests for fetch_registry."""

    @respx.mock
    def test_fetch_registry_success(self, sample_registry: dict) -> None:
        respx.get(f"{BASE_URL}/registry.json").mock(
            return_value=httpx.Response(200, json=sample_registry)
        )
        registry = fetch_registry(BASE_URL)
        assert isinstance(registry, Registry)
        assert len(registry.kits) == 2
        assert registry.kits[0].name == "testkit"

    @respx.mock
    def test_fetch_registry_404(self) -> None:
        respx.get(f"{BASE_URL}/registry.json").mock(return_value=httpx.Response(404))
        with pytest.raises(httpx.HTTPStatusError):
            fetch_registry(BASE_URL)

    @respx.mock
    def test_fetch_registry_network_error(self) -> None:
        respx.get(f"{BASE_URL}/registry.json").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        with pytest.raises(httpx.ConnectError):
            fetch_registry(BASE_URL)


class TestFetchManifest:
    """Tests for fetch_manifest."""

    @respx.mock
    def test_fetch_manifest_success(self, sample_manifest: dict) -> None:
        respx.get(f"{BASE_URL}/testkit/manifest.json").mock(
            return_value=httpx.Response(200, json=sample_manifest)
        )
        manifest = fetch_manifest(BASE_URL, "testkit")
        assert isinstance(manifest, Manifest)
        assert manifest.name == "testkit"
        assert len(manifest.agents) == 2

    @respx.mock
    def test_fetch_manifest_404(self) -> None:
        respx.get(f"{BASE_URL}/nonexistent/manifest.json").mock(
            return_value=httpx.Response(404)
        )
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            fetch_manifest(BASE_URL, "nonexistent")
        assert exc_info.value.response.status_code == 404


class TestFetchFile:
    """Tests for fetch_file."""

    @respx.mock
    def test_fetch_file_success(self) -> None:
        content = "# Agent content"
        respx.get(f"{BASE_URL}/testkit/agents/test.agent.md").mock(
            return_value=httpx.Response(200, text=content)
        )
        result = fetch_file(BASE_URL, "testkit", "agents", "test.agent.md")
        assert result == content

    @respx.mock
    def test_fetch_file_404(self) -> None:
        respx.get(f"{BASE_URL}/testkit/agents/missing.agent.md").mock(
            return_value=httpx.Response(404)
        )
        with pytest.raises(httpx.HTTPStatusError):
            fetch_file(BASE_URL, "testkit", "agents", "missing.agent.md")
