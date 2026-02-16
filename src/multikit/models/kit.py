"""Kit-related Pydantic models: Manifest, RegistryEntry, Registry."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator


class Manifest(BaseModel):
    """A kit's manifest.json — declares files to install."""

    name: str = Field(description="Kit name (e.g., 'testkit')")
    version: str = Field(description="Semantic version (e.g., '1.0.0')")
    description: str = Field(default="", description="Human-readable description")
    agents: list[str] = Field(
        default_factory=list,
        description="Agent filenames (e.g., ['testkit.testdesign.agent.md'])",
    )
    prompts: list[str] = Field(
        default_factory=list,
        description="Prompt filenames (e.g., ['testkit.testdesign.prompt.md'])",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v:
            raise ValueError("Kit name must not be empty")
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", v):
            raise ValueError(
                "Kit name must be lowercase alphanumeric with hyphens, "
                f"starting with a letter or digit. Got: '{v}'"
            )
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v:
            raise ValueError("Version must not be empty")
        return v

    @field_validator("agents")
    @classmethod
    def validate_agents(cls, v: list[str]) -> list[str]:
        for filename in v:
            if not filename.endswith(".agent.md"):
                raise ValueError(
                    f"Agent filename must end with '.agent.md'. Got: '{filename}'"
                )
        return v

    @field_validator("prompts")
    @classmethod
    def validate_prompts(cls, v: list[str]) -> list[str]:
        for filename in v:
            if not filename.endswith(".prompt.md"):
                raise ValueError(
                    f"Prompt filename must end with '.prompt.md'. Got: '{filename}'"
                )
        return v

    @property
    def all_files(self) -> list[tuple[str, str]]:
        """Return list of (subdir, filename) pairs for all declared files."""
        files: list[tuple[str, str]] = []
        for agent in self.agents:
            files.append(("agents", agent))
        for prompt in self.prompts:
            files.append(("prompts", prompt))
        return files


class RegistryEntry(BaseModel):
    """A single kit entry in registry.json."""

    name: str = Field(description="Kit name")
    version: str = Field(description="Latest available version")
    description: str = Field(default="", description="Short description")


class Registry(BaseModel):
    """Remote registry.json — lists all available kits."""

    kits: list[RegistryEntry] = Field(
        default_factory=list, description="Available kits"
    )

    def find_kit(self, name: str) -> RegistryEntry | None:
        """Find a kit entry by name."""
        for kit in self.kits:
            if kit.name == name:
                return kit
        return None
