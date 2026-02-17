"""Interactive kit selection prompts using questionary."""

from __future__ import annotations

import sys

import questionary

from multikit.models.config import MultikitConfig
from multikit.models.kit import Registry


def select_installable_kits(
    config: MultikitConfig,
    remote_registry: Registry | None,
) -> list[str]:
    """Prompt the user to select kits to install (multi-select).

    Shows only kits that are available but not yet installed.

    Returns:
        List of selected kit names (empty if cancelled or none available).
    """
    if remote_registry is None:
        print("✗ Cannot show kit list: registry unavailable.", file=sys.stderr)
        return []

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
        return []

    result = questionary.checkbox(
        "Select kits to install (space to toggle, enter to confirm):",
        choices=choices,
    ).ask()

    return result if result else []


def select_installed_kits(
    config: MultikitConfig,
    action: str = "uninstall",
) -> list[str]:
    """Prompt the user to select installed kits (multi-select).

    Args:
        config: Current multikit config.
        action: Action verb for the prompt (e.g. "uninstall", "diff").

    Returns:
        List of selected kit names (empty if cancelled or none installed).
    """
    if not config.kits:
        print("No kits installed.")
        return []

    choices: list[questionary.Choice] = []
    for kit_name, kit_info in config.kits.items():
        choices.append(
            questionary.Choice(
                title=f"{kit_name} (v{kit_info.version})",
                value=kit_name,
            )
        )

    result = questionary.checkbox(
        f"Select kits to {action} (space to toggle, enter to confirm):",
        choices=choices,
    ).ask()

    return result if result else []
