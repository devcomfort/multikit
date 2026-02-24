"""Multikit CLI — root application entry point."""

import cyclopts

from multikit import __version__

app = cyclopts.App(
    name="multikit",
    help="Kit manager for VS Code Copilot agents.",
    version=__version__,
)


@app.default
def default_action() -> None:
    """Show help when no command is specified."""
    app.help_print()


# Register sub-command apps
from multikit.commands.init import app as init_app  # noqa: E402
from multikit.commands.install import app as install_app  # noqa: E402
from multikit.commands.uninstall import app as uninstall_app  # noqa: E402
from multikit.commands.update import app as update_app  # noqa: E402
from multikit.commands.list_cmd import app as list_app  # noqa: E402
from multikit.commands.diff import app as diff_app  # noqa: E402

app.command(init_app)
app.command(install_app)
app.command(uninstall_app)
app.command(update_app)
app.command(list_app)
app.command(diff_app)
