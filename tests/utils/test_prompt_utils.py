"""Tests for interactive prompt utility helpers."""

from __future__ import annotations

from multikit.models.config import InstalledKit, MultikitConfig
from multikit.models.kit import Registry, RegistryEntry
from multikit.utils.prompt import select_installable_kits, select_installed_kits


class _FakeCheckbox:
    def __init__(self, result):
        self._result = result

    def ask(self):
        return self._result


def test_select_installable_kits_registry_unavailable(capsys) -> None:
    config = MultikitConfig()

    selected = select_installable_kits(config, None)

    captured = capsys.readouterr()
    assert selected == []
    assert "registry unavailable" in captured.err


def test_select_installable_kits_no_choices(capsys) -> None:
    config = MultikitConfig(kits={"testkit": InstalledKit(version="1.0.0", files=[])})
    registry = Registry(
        kits=[RegistryEntry(name="testkit", version="1.1.0", description="")]
    )

    selected = select_installable_kits(config, registry)

    captured = capsys.readouterr()
    assert selected == []
    assert "No kits available to install." in captured.out


def test_select_installable_kits_returns_selected(monkeypatch) -> None:
    config = MultikitConfig()
    registry = Registry(
        kits=[RegistryEntry(name="testkit", version="1.0.0", description="")]
    )
    monkeypatch.setattr(
        "multikit.utils.prompt.questionary.checkbox",
        lambda *_args, **_kwargs: _FakeCheckbox(["testkit"]),
    )

    selected = select_installable_kits(config, registry)

    assert selected == ["testkit"]


def test_select_installable_kits_cancel_returns_empty(monkeypatch) -> None:
    config = MultikitConfig()
    registry = Registry(
        kits=[RegistryEntry(name="testkit", version="1.0.0", description="")]
    )
    monkeypatch.setattr(
        "multikit.utils.prompt.questionary.checkbox",
        lambda *_args, **_kwargs: _FakeCheckbox(None),
    )

    selected = select_installable_kits(config, registry)

    assert selected == []


def test_select_installed_kits_no_kits(capsys) -> None:
    config = MultikitConfig()

    selected = select_installed_kits(config)

    captured = capsys.readouterr()
    assert selected == []
    assert "No kits installed." in captured.out


def test_select_installed_kits_selected_and_cancel(monkeypatch) -> None:
    config = MultikitConfig(kits={"gitkit": InstalledKit(version="1.0.0", files=[])})

    monkeypatch.setattr(
        "multikit.utils.prompt.questionary.checkbox",
        lambda *_args, **_kwargs: _FakeCheckbox(["gitkit"]),
    )
    assert select_installed_kits(config, action="diff") == ["gitkit"]

    monkeypatch.setattr(
        "multikit.utils.prompt.questionary.checkbox",
        lambda *_args, **_kwargs: _FakeCheckbox(None),
    )
    assert select_installed_kits(config, action="diff") == []
