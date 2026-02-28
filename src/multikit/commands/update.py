"""multikit update — Update installed kits to latest remote version."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from multikit.commands.install import _install_single_kit
from multikit.utils.prompt import select_installed_kits
from multikit.utils.toml_io import load_config

app = App(name="update", help="Update installed kit(s) to latest remote version.")


async def _update_single_kit(
    kit_name: str,
    project_dir: Path,
    github_dir: Path,
    registry_url: str,
    force: bool,
) -> bool:
    """Update a single installed kit. Returns True on success."""
    config = load_config(project_dir)

    if not config.is_installed(kit_name):
        print(f"✗ Kit '{kit_name}' is not installed", file=sys.stderr)
        return False

    print(f"Updating '{kit_name}'...")
    return await _install_single_kit(
        kit_name=kit_name,
        project_dir=project_dir,
        github_dir=github_dir,
        registry_url=registry_url,
        force=force,
    )


@app.default
async def handler(
    kit_name: Annotated[
        str | None,
        Parameter(help="Name of the installed kit to update (interactive if omitted)"),
    ] = None,
    *,
    force: Annotated[
        bool, Parameter(help="Overwrite all without confirmation")
    ] = False,
    registry: Annotated[
        str | None,
        Parameter(name="--registry", help="Custom registry base URL"),
    ] = None,
) -> None:
    """Update installed kit(s) by re-installing from latest remote version."""
    project_dir = Path(".").resolve()
    github_dir = project_dir / ".github"

    try:
        config = load_config(project_dir)
    except Exception as exc:
        print(f"✗ Config corrupted: {exc}", file=sys.stderr)
        sys.exit(1)

    registry_url = registry or config.registry_url

    if kit_name is None:
        kit_names = select_installed_kits(config, action="update")
        if not kit_names:
            sys.exit(0)

        failed: list[str] = []
        for name in kit_names:
            if not await _update_single_kit(
                name,
                project_dir=project_dir,
                github_dir=github_dir,
                registry_url=registry_url,
                force=force,
            ):
                failed.append(name)

        if failed:
            print(f"\n✗ Failed to update: {', '.join(failed)}", file=sys.stderr)
            sys.exit(1)
    else:
        if not await _update_single_kit(
            kit_name,
            project_dir=project_dir,
            github_dir=github_dir,
            registry_url=registry_url,
            force=force,
        ):
            sys.exit(1)


def update_handler(
    kit_name: Annotated[
        str | None,
        Parameter(help="Name of the kit to update (interactive if omitted)"),
    ] = None,
    *,
    force: Annotated[
        bool, Parameter(help="Overwrite all without confirmation")
    ] = False,
    registry: Annotated[
        str | None,
        Parameter(name="--registry", help="Custom registry base URL"),
    ] = None,
) -> None:
    """Sync wrapper for update handler."""
    import asyncio

    asyncio.run(handler(kit_name, force=force, registry=registry))
