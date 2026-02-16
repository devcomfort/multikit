"""multikit uninstall — Remove an installed kit."""

from __future__ import annotations

import sys
from pathlib import Path

from cyclopts import App

from multikit.utils.files import delete_kit_files
from multikit.utils.toml_io import load_config, save_config

app = App(name="uninstall", help="Uninstall a kit.")


@app.default
def handler(kit_name: str) -> None:
    """Uninstall a kit by name.

    Parameters
    ----------
    kit_name
        Name of the kit to uninstall.
    """
    project_dir = Path(".").resolve()
    github_dir = project_dir / ".github"

    # Step 1: Load config
    try:
        config = load_config(project_dir)
    except Exception as exc:
        print(f"✗ Config corrupted: {exc}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Check if installed
    if not config.is_installed(kit_name):
        print(f"✗ Kit '{kit_name}' is not installed", file=sys.stderr)
        sys.exit(1)

    kit_info = config.get_kit(kit_name)
    assert kit_info is not None

    # Step 3: Delete tracked files
    deleted = delete_kit_files(github_dir, kit_info.files)

    # Step 4: Remove from config
    del config.kits[kit_name]
    save_config(project_dir, config)

    # Step 5: Report
    print(f"✓ Uninstalled {kit_name} ({deleted} files removed)")
