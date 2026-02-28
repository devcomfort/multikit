"""Concurrency tests for install/update/uninstall operations."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from multikit.models.config import InstalledKit, MultikitConfig
from multikit.utils.toml_io import load_config, save_config
from multikit.commands.install import install_handler, handler as install_async_handler


class TestConcurrentInstalls:
    """Ensure concurrent installs do not corrupt config."""

    @pytest.mark.asyncio
    async def test_two_installs_race(self, initialized_project: Path, monkeypatch):
        monkeypatch.chdir(initialized_project)

        # start with empty config
        save_config(initialized_project, MultikitConfig())

        # create fake install that sleeps before writing
        async def fake_install(kit_name, project_dir, github_dir, registry_url, force):
            # simulate some work
            await asyncio.sleep(0.01)
            config = load_config(project_dir)
            config.kits[kit_name] = InstalledKit(
                version="1.0.0",
                source="remote",
                files=[],
            )
            save_config(project_dir, config)
            return True

        monkeypatch.setattr(
            "multikit.commands.install._install_single_kit", fake_install
        )

        # run two installs concurrently by invoking the async handler directly
        await asyncio.gather(
            install_async_handler("kit1", force=True),
            install_async_handler("kit2", force=True),
        )

        config = load_config(initialized_project)
        # both kits should be present without config corruption
        assert config.is_installed("kit1")
        assert config.is_installed("kit2")
