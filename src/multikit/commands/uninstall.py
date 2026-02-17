"""multikit uninstall — Remove an installed kit."""

from __future__ import annotations

import sys
from pathlib import Path

from cyclopts import App

from multikit.utils.files import delete_kit_files
from multikit.utils.prompt import select_installed_kits
from multikit.utils.toml_io import load_config, save_config

app = App(name="uninstall", help="Uninstall a kit.")


def _uninstall_single_kit(
    kit_name: str,
    project_dir: Path,
    github_dir: Path,
) -> bool:
    """Uninstall a single kit. Returns True on success."""
    config = load_config(project_dir)

    if not config.is_installed(kit_name):
        print(f"✗ Kit '{kit_name}' is not installed", file=sys.stderr)
        return False

    kit_info = config.get_kit(kit_name)
    assert kit_info is not None

    deleted = delete_kit_files(github_dir, kit_info.files)
    del config.kits[kit_name]
    save_config(project_dir, config)

    print(f"✓ Uninstalled {kit_name} ({deleted} files removed)")
    return True


@app.default
def handler(kit_name: str | None = None) -> None:
    """Uninstall a kit by name.

    Parameters
    ----------
    kit_name
        Name of the kit to uninstall. If omitted, shows an interactive selection.
    """
    project_dir = Path(".").resolve()
    github_dir = project_dir / ".github"

    # Load config
    try:
        config = load_config(project_dir)
    except Exception as exc:
        print(f"✗ Config corrupted: {exc}", file=sys.stderr)
        sys.exit(1)

    # Interactive multi-select when kit_name is not provided
    if kit_name is None:
        kit_names = select_installed_kits(config, action="uninstall")
        if not kit_names:
            sys.exit(0)
        failed = []
        for name in kit_names:
            if not _uninstall_single_kit(name, project_dir, github_dir):
                failed.append(name)
        if failed:
            print(f"\n✗ Failed to uninstall: {', '.join(failed)}", file=sys.stderr)
            sys.exit(1)
    else:
        if not _uninstall_single_kit(kit_name, project_dir, github_dir):
            sys.exit(1)
