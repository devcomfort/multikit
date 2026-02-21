"""Tests for python -m multikit entry path."""

from __future__ import annotations

import runpy


def test_main_module_invokes_cli_app(monkeypatch) -> None:
    called: dict[str, bool] = {"ok": False}

    def _fake_app() -> None:
        called["ok"] = True

    monkeypatch.setattr("multikit.cli.app", _fake_app)

    runpy.run_module("multikit.__main__", run_name="__main__")

    assert called["ok"] is True
