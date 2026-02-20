"""Tests for multikit CLI entry point."""

from __future__ import annotations

from multikit.cli import app, default_action


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

    def test_default_action_prints_help(self, monkeypatch) -> None:
        called = {"help": False}

        def _fake_help_print(_self) -> None:
            called["help"] = True

        monkeypatch.setattr(type(app), "help_print", _fake_help_print)

        default_action()

        assert called["help"] is True
