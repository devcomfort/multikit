"""multikit diff — Show differences between local and remote kit files."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx
from cyclopts import App

from multikit.registry.remote import fetch_file, fetch_manifest
from multikit.utils.diff import generate_diff, print_colored_diff
from multikit.utils.prompt import select_installed_kits
from multikit.utils.toml_io import load_config

app = App(name="diff", help="Show diff between local and remote kit files.")


def _diff_single_kit(
    kit_name: str,
    project_dir: Path,
    github_dir: Path,
) -> bool:
    """Diff a single kit. Returns True if no changes, False if changes found."""
    config = load_config(project_dir)

    if not config.is_installed(kit_name):
        print(f"✗ Kit '{kit_name}' is not installed", file=sys.stderr)
        return False

    installed_kit = config.get_kit(kit_name)
    assert installed_kit is not None

    try:
        manifest = fetch_manifest(config.registry_url, kit_name)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            print(f"✗ Kit '{kit_name}' not found in remote registry", file=sys.stderr)
        else:
            print(
                f"✗ HTTP error {exc.response.status_code} fetching manifest",
                file=sys.stderr,
            )
        return False
    except httpx.RequestError as exc:
        print(f"✗ Network error: {exc}", file=sys.stderr)
        return False

    print(
        f"Comparing {kit_name} "
        f"(local v{installed_kit.version} ↔ remote v{manifest.version})"
    )
    print()

    changed = 0
    unchanged = 0

    for subdir, filename in manifest.all_files:
        local_path = github_dir / subdir / filename

        try:
            remote_content = fetch_file(config.registry_url, kit_name, subdir, filename)
        except httpx.HTTPStatusError:
            print(f"  ⚠ Could not fetch remote {subdir}/{filename}", file=sys.stderr)
            continue
        except httpx.RequestError:
            print(f"  ⚠ Network error fetching {subdir}/{filename}", file=sys.stderr)
            continue

        if not local_path.exists():
            print(f"  ✗ Local file missing: {subdir}/{filename}")
            changed += 1
            continue

        local_content = local_path.read_text(encoding="utf-8")

        diff_lines = generate_diff(
            local_content,
            remote_content,
            old_label=f"local/{filename}",
            new_label=f"remote/{filename}",
        )

        if diff_lines:
            print_colored_diff(diff_lines)
            changed += 1
        else:
            unchanged += 1

    print()
    if changed == 0:
        print(f"✓ No changes detected for {kit_name}")
        return True
    else:
        print(f"✓ {changed} file(s) changed, {unchanged} unchanged")
        return False


@app.default
def handler(kit_name: str | None = None) -> None:
    """Show differences for an installed kit.

    Parameters
    ----------
    kit_name
        Name of the kit to diff. If omitted, shows an interactive selection.
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
        kit_names = select_installed_kits(config, action="diff")
        if not kit_names:
            sys.exit(0)
        has_changes = False
        for name in kit_names:
            if not _diff_single_kit(name, project_dir, github_dir):
                has_changes = True
        if has_changes:
            sys.exit(1)
    else:
        if not _diff_single_kit(kit_name, project_dir, github_dir):
            sys.exit(1)
