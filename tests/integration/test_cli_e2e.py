"""
End-to-end integration tests for the ``multikit`` CLI.

These tests run **inside a Docker container** where:
- ``multikit`` is installed as a real CLI tool (``pip install .``)
- A mock registry is served by nginx at ``$MOCK_REGISTRY_URL``

Every test creates a fresh temp workspace via the ``workspace`` /
``initialized_workspace`` / ``installed_demokit_workspace`` fixtures
defined in ``conftest.py``.
"""

from __future__ import annotations

from pathlib import Path

from conftest import REGISTRY_URL, run_cli, set_registry_url


# ====================================================================
# 1. multikit init
# ====================================================================


class TestInitCommand:
    """``multikit init`` — project scaffolding."""

    def test_creates_project_structure(self, workspace: Path) -> None:
        result = run_cli("init", cwd=workspace)

        assert result.returncode == 0
        assert "✓ Initialized multikit" in result.stdout
        assert (workspace / "multikit.toml").exists()
        assert (workspace / ".github" / "agents").is_dir()
        assert (workspace / ".github" / "prompts").is_dir()

    def test_idempotent(self, workspace: Path) -> None:
        run_cli("init", cwd=workspace)
        result = run_cli("init", cwd=workspace)

        assert result.returncode == 0  # second init must not fail

    def test_default_config_content(self, workspace: Path) -> None:
        run_cli("init", cwd=workspace)
        text = (workspace / "multikit.toml").read_text()

        assert "[multikit]" in text
        assert "registry_url" in text


# ====================================================================
# 2. multikit install
# ====================================================================


class TestInstallCommand:
    """``multikit install <kit>`` — download & install from registry."""

    def test_install_single_kit(self, initialized_workspace: Path) -> None:
        result = run_cli(
            "install",
            "demokit",
            "--registry",
            REGISTRY_URL,
            "--force",
            cwd=initialized_workspace,
        )

        assert result.returncode == 0
        assert "✓ Installed demokit" in result.stdout

        # Files on disk
        agents_dir = initialized_workspace / ".github" / "agents"
        prompts_dir = initialized_workspace / ".github" / "prompts"
        assert (agents_dir / "demokit.demo.agent.md").exists()
        assert (prompts_dir / "demokit.demo.prompt.md").exists()

    def test_install_updates_config(self, initialized_workspace: Path) -> None:
        run_cli(
            "install",
            "demokit",
            "--registry",
            REGISTRY_URL,
            "--force",
            cwd=initialized_workspace,
        )
        config_text = (initialized_workspace / "multikit.toml").read_text()

        assert "demokit" in config_text
        assert 'version = "1.0.0"' in config_text

    def test_install_preserves_file_content(self, initialized_workspace: Path) -> None:
        run_cli(
            "install",
            "demokit",
            "--registry",
            REGISTRY_URL,
            "--force",
            cwd=initialized_workspace,
        )
        content = (
            initialized_workspace / ".github" / "agents" / "demokit.demo.agent.md"
        ).read_text()

        assert "demokit" in content.lower()
        assert "Hello from demokit" in content

    def test_install_nonexistent_kit(self, initialized_workspace: Path) -> None:
        result = run_cli(
            "install",
            "nonexistent",
            "--registry",
            REGISTRY_URL,
            cwd=initialized_workspace,
        )

        assert result.returncode != 0

    def test_install_two_kits_sequentially(self, initialized_workspace: Path) -> None:
        ws = initialized_workspace

        r1 = run_cli(
            "install", "demokit", "--registry", REGISTRY_URL, "--force", cwd=ws
        )
        r2 = run_cli(
            "install", "alphakit", "--registry", REGISTRY_URL, "--force", cwd=ws
        )

        assert r1.returncode == 0
        assert r2.returncode == 0
        assert (ws / ".github" / "agents" / "demokit.demo.agent.md").exists()
        assert (ws / ".github" / "agents" / "alphakit.alpha.agent.md").exists()

        config_text = (ws / "multikit.toml").read_text()
        assert "demokit" in config_text
        assert "alphakit" in config_text


# ====================================================================
# 3. multikit list
# ====================================================================


class TestListCommand:
    """``multikit list`` — show available / installed kits."""

    def test_list_shows_available_kits(self, initialized_workspace: Path) -> None:
        result = run_cli("list", cwd=initialized_workspace)

        assert result.returncode == 0
        assert "demokit" in result.stdout

    def test_list_shows_installed_status(
        self, installed_demokit_workspace: Path
    ) -> None:
        result = run_cli("list", cwd=installed_demokit_workspace)

        assert result.returncode == 0
        assert "demokit" in result.stdout
        assert "Installed" in result.stdout

    def test_list_shows_multiple_kits(self, initialized_workspace: Path) -> None:
        result = run_cli("list", cwd=initialized_workspace)

        assert result.returncode == 0
        assert "demokit" in result.stdout
        assert "alphakit" in result.stdout


# ====================================================================
# 4. multikit diff
# ====================================================================


class TestDiffCommand:
    """``multikit diff <kit>`` — compare local vs. remote."""

    def test_diff_no_changes(self, installed_demokit_workspace: Path) -> None:
        result = run_cli("diff", "demokit", cwd=installed_demokit_workspace)

        assert result.returncode == 0
        assert "No changes" in result.stdout

    def test_diff_detects_modification(self, installed_demokit_workspace: Path) -> None:
        ws = installed_demokit_workspace
        agent_file = ws / ".github" / "agents" / "demokit.demo.agent.md"
        agent_file.write_text("MODIFIED CONTENT")

        result = run_cli("diff", "demokit", cwd=ws)

        # diff exits 1 when changes are detected
        assert result.returncode == 1
        assert "changed" in result.stdout.lower()

    def test_diff_not_installed(self, initialized_workspace: Path) -> None:
        result = run_cli("diff", "demokit", cwd=initialized_workspace)

        assert result.returncode != 0
        assert "not installed" in result.stderr.lower()


# ====================================================================
# 5. multikit update
# ====================================================================


class TestUpdateCommand:
    """``multikit update <kit>`` — re-install from latest remote."""

    def test_update_reinstalls_kit(self, installed_demokit_workspace: Path) -> None:
        result = run_cli(
            "update",
            "demokit",
            "--registry",
            REGISTRY_URL,
            "--force",
            cwd=installed_demokit_workspace,
        )

        assert result.returncode == 0
        assert "✓ Installed demokit" in result.stdout

    def test_update_restores_modified_file(
        self, installed_demokit_workspace: Path
    ) -> None:
        ws = installed_demokit_workspace
        agent_file = ws / ".github" / "agents" / "demokit.demo.agent.md"
        original = agent_file.read_text()

        # Corrupt the local file
        agent_file.write_text("CORRUPTED")

        # Update with --force restores original
        run_cli(
            "update",
            "demokit",
            "--registry",
            REGISTRY_URL,
            "--force",
            cwd=ws,
        )

        assert agent_file.read_text() == original

    def test_update_not_installed(self, initialized_workspace: Path) -> None:
        result = run_cli(
            "update",
            "demokit",
            "--registry",
            REGISTRY_URL,
            cwd=initialized_workspace,
        )

        assert result.returncode != 0
        assert "not installed" in result.stderr.lower()


# ====================================================================
# 6. multikit uninstall
# ====================================================================


class TestUninstallCommand:
    """``multikit uninstall <kit>`` — remove an installed kit."""

    def test_uninstall_removes_files(self, installed_demokit_workspace: Path) -> None:
        ws = installed_demokit_workspace
        result = run_cli("uninstall", "demokit", cwd=ws)

        assert result.returncode == 0
        assert "✓ Uninstalled demokit" in result.stdout
        assert not (ws / ".github" / "agents" / "demokit.demo.agent.md").exists()
        assert not (ws / ".github" / "prompts" / "demokit.demo.prompt.md").exists()

    def test_uninstall_removes_config_entry(
        self, installed_demokit_workspace: Path
    ) -> None:
        ws = installed_demokit_workspace
        run_cli("uninstall", "demokit", cwd=ws)

        config_text = (ws / "multikit.toml").read_text()
        assert "demokit" not in config_text

    def test_uninstall_not_installed(self, initialized_workspace: Path) -> None:
        result = run_cli("uninstall", "demokit", cwd=initialized_workspace)

        assert result.returncode != 0
        assert "not installed" in result.stderr.lower()


# ====================================================================
# 7. Full lifecycle (golden-path)
# ====================================================================


class TestFullWorkflow:
    """init → install → list → diff → modify → diff → update → uninstall."""

    def test_complete_lifecycle(self, workspace: Path) -> None:
        # ── 1. Init ──────────────────────────────────────────────────
        r = run_cli("init", cwd=workspace)
        assert r.returncode == 0, f"init failed: {r.stderr}"
        set_registry_url(workspace, REGISTRY_URL)

        # ── 2. Install demokit ───────────────────────────────────────
        r = run_cli(
            "install",
            "demokit",
            "--registry",
            REGISTRY_URL,
            "--force",
            cwd=workspace,
        )
        assert r.returncode == 0, f"install failed: {r.stderr}"
        agent_file = workspace / ".github" / "agents" / "demokit.demo.agent.md"
        assert agent_file.exists()
        original_content = agent_file.read_text()

        # ── 3. List (demokit = Installed) ────────────────────────────
        r = run_cli("list", cwd=workspace)
        assert r.returncode == 0, f"list failed: {r.stderr}"
        assert "demokit" in r.stdout
        assert "Installed" in r.stdout

        # ── 4. Diff (no changes) ─────────────────────────────────────
        r = run_cli("diff", "demokit", cwd=workspace)
        assert r.returncode == 0, f"diff (clean) failed: {r.stderr}"
        assert "No changes" in r.stdout

        # ── 5. Modify local file ─────────────────────────────────────
        agent_file.write_text("USER EDIT — this should show in diff")
        r = run_cli("diff", "demokit", cwd=workspace)
        assert r.returncode == 1, "diff should exit 1 when changes exist"

        # ── 6. Update restores original ──────────────────────────────
        r = run_cli(
            "update",
            "demokit",
            "--registry",
            REGISTRY_URL,
            "--force",
            cwd=workspace,
        )
        assert r.returncode == 0, f"update failed: {r.stderr}"
        assert agent_file.read_text() == original_content

        # ── 7. Uninstall ─────────────────────────────────────────────
        r = run_cli("uninstall", "demokit", cwd=workspace)
        assert r.returncode == 0, f"uninstall failed: {r.stderr}"
        assert not agent_file.exists()

        # ── 8. List again (demokit = Available, not installed) ───────
        r = run_cli("list", cwd=workspace)
        assert r.returncode == 0
        assert "demokit" in r.stdout
        # Should show as Available, not Installed
        output_lines = r.stdout.splitlines()
        demokit_lines = [line for line in output_lines if "demokit" in line]
        for line in demokit_lines:
            assert "Installed" not in line or "Available" in line
