"""multikit install — Install kits from a registry."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import httpx
from cyclopts import App, Parameter

from multikit.models.config import InstalledKit
from multikit.registry.remote import fetch_file, fetch_manifest
from multikit.utils.diff import prompt_overwrite, show_diff
from multikit.utils.files import atomic_staging, move_staged_files, stage_file
from multikit.utils.toml_io import load_config, save_config

app = App(name="install", help="Install a kit from the registry.")


@app.default
def handler(
    kit_name: str,
    *,
    force: Annotated[
        bool, Parameter(help="Overwrite all without confirmation")
    ] = False,
    registry: Annotated[
        str | None,
        Parameter(name="--registry", help="Custom registry base URL"),
    ] = None,
) -> None:
    """Install a kit by name.

    Parameters
    ----------
    kit_name
        Name of the kit to install.
    """
    project_dir = Path(".").resolve()
    github_dir = project_dir / ".github"

    # Step 1: Load config
    try:
        config = load_config(project_dir)
    except Exception as exc:
        print(f"✗ Config corrupted: {exc}", file=sys.stderr)
        sys.exit(1)

    registry_url = registry or config.registry_url

    # Step 2: Fetch manifest
    print(f"Fetching manifest for '{kit_name}'...")
    try:
        manifest = fetch_manifest(registry_url, kit_name)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            print(f"✗ Kit '{kit_name}' not found", file=sys.stderr)
        else:
            print(
                f"✗ HTTP error {exc.response.status_code} fetching manifest",
                file=sys.stderr,
            )
        sys.exit(1)
    except httpx.RequestError as exc:
        print(f"✗ Network error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not manifest.agents and not manifest.prompts:
        print(f"⚠ Kit '{kit_name}' declares no files to install", file=sys.stderr)

    # Step 3-4: Download all files atomically to temp dir
    print(f"Downloading {kit_name} v{manifest.version}...")
    try:
        with atomic_staging() as staging_dir:
            # Download all declared files
            for subdir, filename in manifest.all_files:
                print(f"  Downloading {subdir}/{filename}...")
                try:
                    content = fetch_file(registry_url, kit_name, subdir, filename)
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == 404:
                        print(
                            f"✗ File not found: {subdir}/{filename}",
                            file=sys.stderr,
                        )
                    else:
                        print(
                            f"✗ HTTP error {exc.response.status_code} downloading "
                            f"{subdir}/{filename}",
                            file=sys.stderr,
                        )
                    sys.exit(1)
                except httpx.RequestError as exc:
                    print(
                        f"✗ Network error downloading {subdir}/{filename}: {exc}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                stage_file(staging_dir, subdir, filename, content)

            # Step 5-6: Compare with local and resolve conflicts
            files_to_install: list[tuple[str, str]] = []
            overwrite_all = force
            skip_all = False

            for subdir, filename in manifest.all_files:
                rel_path = f"{subdir}/{filename}"
                local_file = github_dir / subdir / filename
                staged_file = staging_dir / subdir / filename

                if local_file.exists() and not overwrite_all and not skip_all:
                    local_content = local_file.read_text(encoding="utf-8")
                    remote_content = staged_file.read_text(encoding="utf-8")

                    if local_content == remote_content:
                        print(f"  ✓ {rel_path} (unchanged)")
                        files_to_install.append((subdir, filename))
                        continue

                    # Show diff and prompt
                    print(f"\n  Conflict: {rel_path}")
                    show_diff(local_content, remote_content, filename)

                    choice = prompt_overwrite(rel_path)
                    if choice == "y":
                        files_to_install.append((subdir, filename))
                    elif choice == "n":
                        print(f"  Skipped {rel_path}")
                        continue
                    elif choice == "a":
                        overwrite_all = True
                        files_to_install.append((subdir, filename))
                    elif choice == "s":
                        skip_all = True
                        print(f"  Skipped {rel_path}")
                        continue
                elif skip_all:
                    print(f"  Skipped {rel_path}")
                    continue
                else:
                    files_to_install.append((subdir, filename))

            # Step 7: Move files from staging to .github/
            if files_to_install:
                installed_paths = move_staged_files(
                    staging_dir, github_dir, files_to_install
                )
            else:
                installed_paths = []

    except SystemExit:
        raise
    except Exception as exc:
        print(f"✗ Installation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # Step 8: Update config
    config.kits[kit_name] = InstalledKit(
        version=manifest.version,
        source="remote",
        files=installed_paths,
    )
    save_config(project_dir, config)

    print(f"✓ Installed {kit_name} v{manifest.version}")
