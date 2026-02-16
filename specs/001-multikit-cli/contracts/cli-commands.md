# CLI Command Contracts: Multikit CLI (MVP)

**Feature**: 001-multikit-cli
**Date**: 2026-02-12
**Framework**: cyclopts

## Entry Point

```toml
# pyproject.toml
[project.scripts]
multikit = "multikit.cli:app"
```

```python
# src/multikit/cli.py
import cyclopts
from multikit import __version__

app = cyclopts.App(
    name="multikit",
    help="Kit manager for VS Code Copilot agents.",
    version=__version__,
)

# Sub-command apps are registered via app.command()
from multikit.commands.init import app as init_app
from multikit.commands.install import app as install_app
from multikit.commands.uninstall import app as uninstall_app
from multikit.commands.list_cmd import app as list_app
from multikit.commands.diff import app as diff_app

app.command(init_app)
app.command(install_app)
app.command(uninstall_app)
app.command(list_app)
app.command(diff_app)
```

---

## Command: `multikit init`

**Module**: `src/multikit/commands/init.py`

### Signature

```python
# src/multikit/commands/init.py
from cyclopts import App

app = App(name="init", help="Initialize a new multikit project.")

@app.default
def handler(
    path: Annotated[str, Parameter(help="Target project directory")] = ".",
) -> None:
```

### Behavior

| Step | Action                    | Detail                                                         |
| ---- | ------------------------- | -------------------------------------------------------------- |
| 1    | Resolve path              | `Path(path).resolve()`                                         |
| 2    | Create `.github/agents/`  | `mkdir(parents=True, exist_ok=True)`                           |
| 3    | Create `.github/prompts/` | `mkdir(parents=True, exist_ok=True)`                           |
| 4    | Create `multikit.toml`    | Only if not exists. Default template with `[multikit]` section |

### Input/Output

| Type            | Format                                 |
| --------------- | -------------------------------------- |
| Input           | `path` (string, default ".")           |
| Output (stdout) | `✓ Initialized multikit in {abs_path}` |
| Output (stderr) | Error messages                         |
| Exit code       | 0 (success), 1 (error)                 |

### Idempotency

- All `mkdir` calls use `exist_ok=True`
- `multikit.toml` is only written if it doesn't already exist
- Existing files in `.github/` are never modified

---

## Command: `multikit install <kit_name>`

**Module**: `src/multikit/commands/install.py`

### Signature

```python
# src/multikit/commands/install.py
from cyclopts import App

app = App(name="install", help="Install a kit from the remote registry.")

@app.default
def handler(
    kit_name: Annotated[str, Parameter(help="Name of the kit to install")],
    *,
    force: Annotated[bool, Parameter(help="Overwrite all without confirmation")] = False,
    registry_url: Annotated[str | None, Parameter(name="--registry", help="Custom registry base URL")] = None,
) -> None:
```

### Behavior

| Step | Action            | Detail                                                                    |
| ---- | ----------------- | ------------------------------------------------------------------------- |
| 1    | Load config       | Read `multikit.toml`, extract `registry_url`                              |
| 2    | Fetch manifest    | GET `{registry_url}/{kit_name}/manifest.json`                             |
| 3    | Create temp dir   | `tempfile.TemporaryDirectory(prefix="multikit-")`                         |
| 4    | Download files    | GET each file listed in manifest → write to temp dir                      |
| 5    | Compare local     | If files exist in `.github/`, compare with downloaded                     |
| 6    | Resolve conflicts | `--force`: overwrite all. Otherwise: interactive y/n/a/s per file         |
| 7    | Move files        | `shutil.move()` from temp dir to `.github/agents/` and `.github/prompts/` |
| 8    | Update config     | Add `[multikit.kits.<kit_name>]` to `multikit.toml`                       |

### Input/Output

| Type            | Format                                                                                         |
| --------------- | ---------------------------------------------------------------------------------------------- |
| Input           | `kit_name` (string), `--force` (flag), `--registry` (optional URL)                             |
| Output (stdout) | Progress: `Fetching manifest...`, `Downloading {file}...`, `✓ Installed {kit_name} v{version}` |
| Output (stdout) | Diff output when conflicts detected                                                            |
| Output (stdin)  | Interactive prompt `[y/n/a/s]` when conflicts and no `--force`                                 |
| Output (stderr) | Error: `✗ Kit '{kit_name}' not found`, `✗ Network error: {detail}`                             |
| Exit code       | 0 (success, including partial skip), 1 (error)                                                 |

### Error Cases

| Error                   | Exit Code | Behavior                                                 |
| ----------------------- | --------- | -------------------------------------------------------- |
| Network error (connect) | 1         | Cleanup temp, print error                                |
| 404 on manifest         | 1         | Print "Kit not found"                                    |
| 404 on individual file  | 1         | Cleanup ALL temp files (atomic), print which file failed |
| TOML parse error        | 1         | Print "Config corrupted" + path                          |
| Permission denied       | 1         | Print "Cannot write to .github/"                         |

---

## Command: `multikit uninstall <kit_name>`

**Module**: `src/multikit/commands/uninstall.py`

### Signature

```python
# src/multikit/commands/uninstall.py
from cyclopts import App

app = App(name="uninstall", help="Uninstall a kit.")

@app.default
def handler(
    kit_name: Annotated[str, Parameter(help="Name of the kit to uninstall")],
) -> None:
```

### Behavior

| Step | Action          | Detail                                                               |
| ---- | --------------- | -------------------------------------------------------------------- |
| 1    | Load config     | Read `multikit.toml`                                                 |
| 2    | Check installed | Verify `kit_name` exists in `config.kits`                            |
| 3    | Delete files    | Remove files listed in `config.kits[kit_name].files` from `.github/` |
| 4    | Update config   | Remove `[multikit.kits.<kit_name>]` section                          |
| 5    | Report          | Print removed files count                                            |

### Input/Output

| Type            | Format                                         |
| --------------- | ---------------------------------------------- |
| Input           | `kit_name` (string)                            |
| Output (stdout) | `✓ Uninstalled {kit_name} ({n} files removed)` |
| Output (stderr) | `✗ Kit '{kit_name}' is not installed`          |
| Exit code       | 0 (success), 1 (not installed)                 |

---

## Command: `multikit list`

**Module**: `src/multikit/commands/list_cmd.py`

### Signature

```python
# src/multikit/commands/list_cmd.py
from cyclopts import App

app = App(name="list", help="List available and installed kits.")

@app.default
def handler() -> None:
```

### Behavior

| Step | Action         | Detail                                                   |
| ---- | -------------- | -------------------------------------------------------- |
| 1    | Load config    | Read `multikit.toml`                                     |
| 2    | Fetch registry | GET `{registry_url}/registry.json` (graceful on failure) |
| 3    | Merge          | Combine remote available kits + local installed status   |
| 4    | Print table    | Formatted table output                                   |

### Output Format

```
Kit          Status       Version  Agents  Prompts
───────────  ──────────   ───────  ──────  ───────
testkit      ✅ Installed  1.0.0    2       2
gitkit       ❌ Available  1.0.0    —       —
speckit      ❌ Available  2.0.0    —       —
```

On network error:

```
⚠ Could not fetch remote registry. Showing local kits only.

Kit          Status       Version  Agents  Prompts
───────────  ──────────   ───────  ──────  ───────
testkit      ✅ Installed  1.0.0    2       2
```

### Input/Output

| Type            | Format                            |
| --------------- | --------------------------------- |
| Input           | None                              |
| Output (stdout) | Table as shown above              |
| Output (stderr) | Warning on network failure        |
| Exit code       | 0 (always, even on network error) |

---

## Command: `multikit diff <kit_name>`

**Module**: `src/multikit/commands/diff.py`

### Signature

```python
# src/multikit/commands/diff.py
from cyclopts import App

app = App(name="diff", help="Show diff between local and remote kit files.")

@app.default
def handler(
    kit_name: Annotated[str, Parameter(help="Name of the kit to diff")],
) -> None:
```

### Behavior

| Step | Action             | Detail                                                |
| ---- | ------------------ | ----------------------------------------------------- |
| 1    | Load config        | Read `multikit.toml`, verify kit is installed         |
| 2    | Fetch remote files | GET manifest + all files from remote                  |
| 3    | Read local files   | Read corresponding files from `.github/`              |
| 4    | Compare            | `difflib.unified_diff()` per file                     |
| 5    | Output             | Print colored diff per file, or "No changes detected" |

### Output Format

```
Comparing testkit (local v1.0.0 ↔ remote v1.1.0)

--- local/testkit.testdesign.agent.md
+++ remote/testkit.testdesign.agent.md
@@ -10,3 +10,5 @@
 existing line
-removed line
+added line
+another new line

✓ 1 file(s) changed, 0 unchanged
```

Or:

```
✓ No changes detected for testkit
```

### Input/Output

| Type            | Format                                       |
| --------------- | -------------------------------------------- |
| Input           | `kit_name` (string)                          |
| Output (stdout) | Colored unified diff or "No changes" message |
| Output (stderr) | `✗ Kit '{kit_name}' is not installed`        |
| Exit code       | 0 (no changes), 1 (has changes or error)     |

---

## Shared Patterns

### Config I/O

```python
# Used by all commands
def load_config(project_dir: Path) -> MultikitConfig:
    """Load multikit.toml from project directory."""

def save_config(project_dir: Path, config: MultikitConfig) -> None:
    """Write multikit.toml to project directory."""
```

### Registry Client

```python
# Used by install, list, diff
def fetch_registry(registry_url: str) -> Registry:
    """Fetch registry.json from remote."""

def fetch_manifest(registry_url: str, kit_name: str) -> Manifest:
    """Fetch manifest.json for a specific kit."""

def fetch_file(registry_url: str, kit_name: str, subdir: str, filename: str) -> str:
    """Fetch a single file content from remote."""
```
