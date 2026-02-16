"""Interactive kit selection prompts using questionary."""

from __future__ import annotations

import sys

import questionary

from multikit.models.config import MultikitConfig
from multikit.models.kit import Registry


def select_installable_kit(
    config: MultikitConfig,
    remote_registry: Registry | None,
) -> str | None:
    """Prompt the user to select a kit to install.

    Shows only kits that are available but not yet installed.

    Returns:
        Selected kit name, or None if cancelled.
    """
    if remote_registry is None:
        print("✗ Cannot show kit list: registry unavailable.", file=sys.stderr)
        return None

    choices: list[questionary.Choice] = []
    for entry in remote_registry.kits:
        if not config.is_installed(entry.name):
            choices.append(
                questionary.Choice(
                    title=f"{entry.name} (v{entry.version})",
                    value=entry.name,
                )
            )

    if not choices:
        print("No kits available to install.")
        return None

    return questionary.select(
        "Select a kit to install:",
        choices=choices,
    ).ask()


def select_installed_kit(
    config: MultikitConfig,
    action: str = "uninstall",
) -> str | None:
    """Prompt the user to select an installed kit.

    Args:
        config: Current multikit config.
        action: Action verb for the prompt (e.g. "uninstall", "diff").

    Returns:
        Selected kit name, or None if cancelled.
    """
    if not config.kits:
        print("No kits installed.")
        return None

    choices: list[questionary.Choice] = []
    for kit_name, kit_info in config.kits.items():
        choices.append(
            questionary.Choice(
                title=f"{kit_name} (v{kit_info.version})",
                value=kit_name,
            )
        )

    return questionary.select(
        f"Select a kit to {action}:",
        choices=choices,
    ).ask()
