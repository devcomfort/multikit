"""multikit list — List available and installed kits."""

from __future__ import annotations

import sys
from pathlib import Path

from cyclopts import App

from multikit.models.kit import Registry
from multikit.registry.remote import fetch_registry
from multikit.utils.toml_io import load_config

app = App(name="list", help="List available and installed kits.")


@app.default
def handler() -> None:
    """List available and installed kits."""
    project_dir = Path(".").resolve()

    # Step 1: Load config
    try:
        config = load_config(project_dir)
    except Exception as exc:
        print(f"✗ Config corrupted: {exc}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Fetch registry (graceful on failure)
    remote_registry: Registry | None = None
    try:
        remote_registry = fetch_registry(config.registry_url)
    except Exception:
        print(
            "⚠ Could not fetch remote registry. Showing local kits only.",
            file=sys.stderr,
        )

    # Step 3: Merge remote + local
    kits_table: list[dict[str, str]] = []

    if remote_registry:
        for entry in remote_registry.kits:
            installed_kit = config.get_kit(entry.name)
            if installed_kit:
                kits_table.append(
                    {
                        "name": entry.name,
                        "status": "✅ Installed",
                        "version": installed_kit.version,
                        "agents": str(
                            len(
                                [
                                    f
                                    for f in installed_kit.files
                                    if f.startswith("agents/")
                                ]
                            )
                        ),
                        "prompts": str(
                            len(
                                [
                                    f
                                    for f in installed_kit.files
                                    if f.startswith("prompts/")
                                ]
                            )
                        ),
                    }
                )
            else:
                kits_table.append(
                    {
                        "name": entry.name,
                        "status": "❌ Available",
                        "version": entry.version,
                        "agents": "—",
                        "prompts": "—",
                    }
                )

    # Add local-only kits not in remote registry
    remote_names = {e.name for e in remote_registry.kits} if remote_registry else set()
    for kit_name, kit_info in config.kits.items():
        if kit_name not in remote_names:
            kits_table.append(
                {
                    "name": kit_name,
                    "status": "✅ Installed",
                    "version": kit_info.version,
                    "agents": str(
                        len([f for f in kit_info.files if f.startswith("agents/")])
                    ),
                    "prompts": str(
                        len([f for f in kit_info.files if f.startswith("prompts/")])
                    ),
                }
            )

    # Step 4: Print table
    if not kits_table:
        print("No kits found.")
        return

    # Calculate column widths
    headers = ["Kit", "Status", "Version", "Agents", "Prompts"]
    col_widths = [len(h) for h in headers]
    for row in kits_table:
        col_widths[0] = max(col_widths[0], len(row["name"]))
        col_widths[1] = max(col_widths[1], len(row["status"]))
        col_widths[2] = max(col_widths[2], len(row["version"]))
        col_widths[3] = max(col_widths[3], len(row["agents"]))
        col_widths[4] = max(col_widths[4], len(row["prompts"]))

    # Print header
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("  ".join("─" * w for w in col_widths))

    # Print rows
    for row in kits_table:
        values = [
            row["name"],
            row["status"],
            row["version"],
            row["agents"],
            row["prompts"],
        ]
        print("  ".join(v.ljust(w) for v, w in zip(values, col_widths)))
