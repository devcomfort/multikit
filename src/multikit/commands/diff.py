"""multikit diff — Show differences between local and remote kit files."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx
from cyclopts import App

from multikit.registry.remote import fetch_file, fetch_manifest
from multikit.utils.diff import generate_diff, print_colored_diff
from multikit.utils.toml_io import load_config

app = App(name="diff", help="Show diff between local and remote kit files.")


@app.default
def handler(kit_name: str) -> None:
    """Show differences for an installed kit.

    Parameters
    ----------
    kit_name
        Name of the kit to diff.
    """
    project_dir = Path(".").resolve()
    github_dir = project_dir / ".github"

    # Step 1: Load config and verify kit is installed
    try:
        config = load_config(project_dir)
    except Exception as exc:
        print(f"✗ Config corrupted: {exc}", file=sys.stderr)
        sys.exit(1)

    if not config.is_installed(kit_name):
        print(f"✗ Kit '{kit_name}' is not installed", file=sys.stderr)
        sys.exit(1)

    installed_kit = config.get_kit(kit_name)
    assert installed_kit is not None

    # Step 2: Fetch remote manifest
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
        sys.exit(1)
    except httpx.RequestError as exc:
        print(f"✗ Network error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Comparing {kit_name} "
        f"(local v{installed_kit.version} ↔ remote v{manifest.version})"
    )
    print()

    # Step 3-4: Compare each file
    changed = 0
    unchanged = 0

    for subdir, filename in manifest.all_files:
        local_path = github_dir / subdir / filename

        # Fetch remote file
        try:
            remote_content = fetch_file(config.registry_url, kit_name, subdir, filename)
        except httpx.HTTPStatusError:
            print(f"  ⚠ Could not fetch remote {subdir}/{filename}", file=sys.stderr)
            continue
        except httpx.RequestError:
            print(f"  ⚠ Network error fetching {subdir}/{filename}", file=sys.stderr)
            continue

        # Read local file
        if not local_path.exists():
            print(f"  ✗ Local file missing: {subdir}/{filename}")
            changed += 1
            continue

        local_content = local_path.read_text(encoding="utf-8")

        # Compare
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

    # Step 5: Summary
    print()
    if changed == 0:
        print(f"✓ No changes detected for {kit_name}")
    else:
        print(f"✓ {changed} file(s) changed, {unchanged} unchanged")
        sys.exit(1)
