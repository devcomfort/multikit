"""TOML read/write utilities for multikit.toml."""

from __future__ import annotations

import sys
from pathlib import Path

# Python 3.11+ has tomllib in stdlib
if sys.version_info >= (3, 11):  # pragma: no cover - runs only on Python 3.11+
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover - defensive: optional dependency missing
        raise ImportError(
            "Python <3.11 requires 'tomli'. Install with: pip install tomli"
        )  # pragma: no cover - same defensive path as above

import tomli_w

from multikit.models.config import DEFAULT_REGISTRY_URL, InstalledKit, MultikitConfig


def read_toml(path: Path) -> dict:
    """Read a TOML file and return as dict."""
    with open(path, "rb") as f:
        return tomllib.load(f)


def write_toml(path: Path, data: dict) -> None:
    """Write a dict to a TOML file."""
    with open(path, "wb") as f:
        tomli_w.dump(data, f)


def load_config(project_dir: Path) -> MultikitConfig:
    """Load multikit.toml from project directory.

    Returns a default config if file doesn't exist.
    """
    config_path = project_dir / "multikit.toml"
    if not config_path.exists():
        return MultikitConfig()

    data = read_toml(config_path)
    multikit_data = data.get("multikit", {})

    # Parse installed kits
    kits_data = multikit_data.get("kits", {})
    kits: dict[str, InstalledKit] = {}
    for kit_name, kit_info in kits_data.items():
        kits[kit_name] = InstalledKit(**kit_info)

    return MultikitConfig(
        version=multikit_data.get("version", "0.1.0"),
        registry_url=multikit_data.get("registry_url", DEFAULT_REGISTRY_URL),
        kits=kits,
    )


def save_config(project_dir: Path, config: MultikitConfig) -> None:
    """Write multikit.toml to project directory."""
    config_path = project_dir / "multikit.toml"

    data: dict = {
        "multikit": {
            "version": config.version,
            "registry_url": config.registry_url,
        }
    }

    if config.kits:
        data["multikit"]["kits"] = {}
        for kit_name, kit_info in config.kits.items():
            data["multikit"]["kits"][kit_name] = kit_info.model_dump()

    write_toml(config_path, data)


def create_default_config(project_dir: Path) -> None:
    """Create a default multikit.toml if it doesn't exist."""
    config_path = project_dir / "multikit.toml"
    if config_path.exists():
        return

    config = MultikitConfig()
    save_config(project_dir, config)
