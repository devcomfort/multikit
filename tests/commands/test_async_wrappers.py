"""Tests for sync wrapper functions when invoked from async context."""

from __future__ import annotations

import pytest

from multikit.commands.diff import diff_handler
from multikit.commands.install import install_handler
from multikit.commands.list_cmd import list_handler
from multikit.commands.uninstall import handler as uninstall_handler


class TestSyncWrappersInAsync:
    """Ensure sync wrappers raise when called from running event loop."""

    @pytest.mark.asyncio
    async def test_diff_handler_in_async(self):
        with pytest.raises(RuntimeError):
            diff_handler()

    @pytest.mark.asyncio
    async def test_install_handler_in_async(self):
        with pytest.raises(RuntimeError):
            install_handler("testkit")

    @pytest.mark.asyncio
    async def test_list_handler_in_async(self):
        with pytest.raises(RuntimeError):
            list_handler()

    @pytest.mark.asyncio
    async def test_uninstall_handler_in_async(self):
        # uninstall_handler has no async wrapper; it will execute synchronously
        # and may call sys.exit() when kit is not installed. We simply ensure
        # calling it from an async context does not raise RuntimeError but may
        # raise SystemExit which we capture.
        with pytest.raises(SystemExit) as exc_info:
            uninstall_handler("testkit")
        assert exc_info.value.code == 1
