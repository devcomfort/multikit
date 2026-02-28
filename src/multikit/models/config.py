"""Configuration Pydantic models: InstalledKit, MultikitConfig."""

from __future__ import annotations

from pydantic import BaseModel, Field


DEFAULT_REGISTRY_URL = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"


class InstalledKit(BaseModel):
    """Tracks an installed kit in multikit.toml."""

    version: str = Field(description="Installed version")
    source: str = Field(default="remote", description="Installation source")
    files: list[str] = Field(
        default_factory=list,
        description="List of installed file paths relative to .github/",
    )


class NetworkConfig(BaseModel):
    """Network configuration for remote operations."""

    max_concurrency: int = Field(
        default=8,
        ge=1,
        le=32,
        description="Maximum concurrent HTTP requests",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for failed requests",
    )
    retry_base_delay: float = Field(
        default=0.5,
        ge=0.1,
        le=5.0,
        description="Base delay (seconds) for exponential backoff",
    )
    retry_max_delay: float = Field(
        default=2.0,
        ge=0.5,
        le=30.0,
        description="Maximum delay (seconds) between retries",
    )


class MultikitConfig(BaseModel):
    """Root config model for multikit.toml."""

    version: str = Field(default="0.1.0", description="Multikit config version")
    registry_url: str = Field(
        default=DEFAULT_REGISTRY_URL,
        description="Base URL for the remote kit registry",
    )
    network: NetworkConfig = Field(
        default_factory=NetworkConfig, description="Network configuration"
    )
    kits: dict[str, InstalledKit] = Field(
        default_factory=dict, description="Installed kits"
    )

    def is_installed(self, kit_name: str) -> bool:
        """Check if a kit is installed."""
        return kit_name in self.kits

    def get_kit(self, kit_name: str) -> InstalledKit | None:
        """Get installed kit info, or None."""
        return self.kits.get(kit_name)
