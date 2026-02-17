"""Remote registry client — fetches kits from raw.githubusercontent.com."""

from __future__ import annotations


import httpx

from multikit.models.kit import Manifest, Registry

TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)
USER_AGENT = "multikit/0.1.0"


def _create_client() -> httpx.Client:
    """Create a configured httpx client."""
    return httpx.Client(
        timeout=TIMEOUT,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    )


def fetch_registry(registry_url: str) -> Registry:
    """Fetch registry.json from remote.

    Args:
        registry_url: Base URL like https://raw.githubusercontent.com/owner/repo/branch/kits

    Returns:
        Registry model with available kits

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx
        httpx.RequestError: On network errors
    """
    url = f"{registry_url}/registry.json"
    with _create_client() as client:
        response = client.get(url)
        response.raise_for_status()
        return Registry.model_validate_json(response.content)


def fetch_manifest(registry_url: str, kit_name: str) -> Manifest:
    """Fetch manifest.json for a specific kit.

    Args:
        registry_url: Base URL
        kit_name: Name of the kit

    Returns:
        Manifest model

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx (404 = kit not found)
        httpx.RequestError: On network errors
    """
    url = f"{registry_url}/{kit_name}/manifest.json"
    with _create_client() as client:
        response = client.get(url)
        response.raise_for_status()
        return Manifest.model_validate_json(response.content)


def fetch_file(registry_url: str, kit_name: str, subdir: str, filename: str) -> str:
    """Fetch a single file content from remote.

    Args:
        registry_url: Base URL
        kit_name: Name of the kit
        subdir: Subdirectory ('agents' or 'prompts')
        filename: File name

    Returns:
        File content as string

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx
        httpx.RequestError: On network errors
    """
    url = f"{registry_url}/{kit_name}/{subdir}/{filename}"
    with _create_client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
