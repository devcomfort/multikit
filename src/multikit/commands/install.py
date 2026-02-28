"""multikit install — Install kits from a registry."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import aiohttp
from cyclopts import App, Parameter

from multikit.models.config import InstalledKit
from multikit.registry.remote import (
    RemoteFetchError,
    fetch_file,
    fetch_manifest,
    fetch_registry,
)
from multikit.utils.diff import prompt_overwrite, show_diff
from multikit.utils.files import atomic_staging, move_staged_files, stage_file
from multikit.utils.prompt import select_installable_kits
from multikit.utils.toml_io import load_config, save_config

app = App(name="install", help="Install a kit from the registry.")


async def _install_single_kit(
    kit_name: str,
    project_dir: Path,
    github_dir: Path,
    registry_url: str,
    force: bool,
) -> bool:
    """Install a single kit. Returns True on success, False on failure."""
    config = load_config(project_dir)

    # Fetch manifest
    print(f"Fetching manifest for '{kit_name}'...")
    try:
        manifest = await fetch_manifest(registry_url, kit_name)
    except RemoteFetchError as exc:
        print(
            f"✗ Failed to fetch manifest after {exc.attempts} attempts: {exc}",
            file=sys.stderr,
        )
        return False
    except aiohttp.ClientResponseError as exc:
        if exc.status == 404:
            print(f"✗ Kit '{kit_name}' not found", file=sys.stderr)
        else:
            print(
                f"✗ HTTP error {exc.status} fetching manifest",
                file=sys.stderr,
            )
        return False
    except aiohttp.ClientError as exc:
        print(f"✗ Network error: {exc}", file=sys.stderr)
        return False

    if not manifest.agents and not manifest.prompts:
        print(f"⚠ Kit '{kit_name}' declares no files to install", file=sys.stderr)

    # Download all files atomically to temp dir
    print(f"Downloading {kit_name} v{manifest.version}...")
    try:
        with atomic_staging() as staging_dir:
            for subdir, filename in manifest.all_files:
                print(f"  Downloading {subdir}/{filename}...")
                try:
                    content = await fetch_file(registry_url, kit_name, subdir, filename)
                except RemoteFetchError as exc:
                    print(
                        f"✗ Failed to download {subdir}/{filename} after {exc.attempts} attempts: {exc}",
                        file=sys.stderr,
                    )
                    return False
                except aiohttp.ClientResponseError as exc:
                    if exc.status == 404:
                        print(
                            f"✗ File not found: {subdir}/{filename}",
                            file=sys.stderr,
                        )
                    else:
                        print(
                            f"✗ HTTP error {exc.status} downloading "
                            f"{subdir}/{filename}",
                            file=sys.stderr,
                        )
                    return False
                except aiohttp.ClientError as exc:
                    print(
                        f"✗ Network error downloading {subdir}/{filename}: {exc}",
                        file=sys.stderr,
                    )
                    return False

                stage_file(staging_dir, subdir, filename, content)

            # Compare with local and resolve conflicts
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

            # Move files from staging to .github/
            if files_to_install:
                installed_paths = move_staged_files(
                    staging_dir, github_dir, files_to_install
                )
            else:
                installed_paths = []

    except Exception as exc:
        print(f"✗ Installation failed: {exc}", file=sys.stderr)
        return False

    # Update config
    config.kits[kit_name] = InstalledKit(
        version=manifest.version,
        source="remote",
        files=installed_paths,
    )
    save_config(project_dir, config)

    print(f"✓ Installed {kit_name} v{manifest.version}")
    return True


@app.default
async def handler(
    kit_name: Annotated[
        str | None,
        Parameter(help="Name of the kit to install (interactive if omitted)"),
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
    """Async install handler.

    Parameters
    ----------
    kit_name
        Name of the kit to install. If omitted, shows an interactive selection.
    """
    project_dir = Path(".").resolve()
    github_dir = project_dir / ".github"

    # Load config
    try:
        config = load_config(project_dir)
    except Exception as exc:
        print(f"✗ Config corrupted: {exc}", file=sys.stderr)
        sys.exit(1)

    registry_url = registry or config.registry_url

    # Interactive multi-select when kit_name is not provided
    if kit_name is None:
        try:
            remote_registry = await fetch_registry(registry_url)
        except Exception:
            print("✗ Cannot fetch registry for interactive selection.", file=sys.stderr)
            sys.exit(1)
        kit_names = select_installable_kits(config, remote_registry)
        if not kit_names:
            sys.exit(0)
        failed = []
        for name in kit_names:
            if not await _install_single_kit(
                name, project_dir, github_dir, registry_url, force
            ):
                failed.append(name)
        if failed:
            print(f"\n✗ Failed to install: {', '.join(failed)}", file=sys.stderr)
            sys.exit(1)
    else:
        if not await _install_single_kit(
            kit_name, project_dir, github_dir, registry_url, force
        ):
            sys.exit(1)


def install_handler(
    kit_name: Annotated[str | None, Parameter(help="Kit name to install")] = None,
    *,
    force: Annotated[
        bool, Parameter(help="Overwrite existing files without prompting")
    ] = False,
    registry: Annotated[str | None, Parameter(help="Custom registry URL")] = None,
) -> None:
    """Install handler wrapper for cyclopts."""
    import asyncio

    asyncio.run(handler(kit_name, force=force, registry=registry))
