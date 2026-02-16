"""Tests for multikit CLI entry point."""

from __future__ import annotations

from multikit.cli import app


class TestCLIApp:
    """Tests for the root CLI app."""

    def test_app_exists(self) -> None:
        assert app is not None

    def test_app_name(self) -> None:
        assert app.name == ("multikit",)

    def test_app_has_commands(self) -> None:
        # Get registered command names (cyclopts uses tuples for names)
        command_names = [cmd.name for cmd in app._commands.values()]
        assert ("init",) in command_names
        assert ("install",) in command_names
        assert ("uninstall",) in command_names
        assert ("list",) in command_names
        assert ("diff",) in command_names
