"""multikit init — Initialize a new multikit project."""

from __future__ import annotations

import sys
from pathlib import Path

from cyclopts import App

from multikit.utils.toml_io import create_default_config

app = App(name="init", help="Initialize a new multikit project.")


@app.default
def handler(path: str = ".") -> None:
    """Initialize multikit in the given directory.

    Parameters
    ----------
    path
        Target project directory.
    """
    project_dir = Path(path).resolve()

    try:
        # Create .github/agents/ and .github/prompts/
        github_dir = project_dir / ".github"
        (github_dir / "agents").mkdir(parents=True, exist_ok=True)
        (github_dir / "prompts").mkdir(parents=True, exist_ok=True)

        # Create default multikit.toml (only if not exists)
        create_default_config(project_dir)

        print(f"✓ Initialized multikit in {project_dir}")

    except PermissionError:
        print(f"✗ Permission denied: cannot write to {project_dir}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"✗ Error initializing project: {exc}", file=sys.stderr)
        sys.exit(1)
