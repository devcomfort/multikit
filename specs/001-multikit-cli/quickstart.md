# Quickstart: Multikit CLI

## Prerequisites

- Python ≥ 3.10
- pip (or uv/rye)

## Installation

```bash
pip install multikit
```

## Usage

### 1. Initialize a project

```bash
cd your-project
multikit init
```

This creates:

```
your-project/
├── .github/
│   ├── agents/      # VS Code Copilot agent files go here
│   └── prompts/     # VS Code Copilot prompt files go here
└── multikit.toml    # Configuration tracking installed kits
```

### 2. Install a kit

```bash
multikit install testkit
```

This downloads agent/prompt files from the remote registry and places them in `.github/`:

```
.github/
├── agents/
│   ├── testkit.testdesign.agent.md
│   └── testkit.testcoverage.agent.md
└── prompts/
    ├── testkit.testdesign.prompt.md
    └── testkit.testcoverage.prompt.md
```

### 3. List available kits

```bash
multikit list
```

Output:

```
Kit          Status        Version  Agents  Prompts
───────────  ──────────    ───────  ──────  ───────
testkit      ✅ Installed   1.0.0    2       2
gitkit       ❌ Available   1.0.0    1       1
```

### 4. Check for updates

```bash
multikit diff testkit
```

Shows file-by-file differences between your local installation and the latest remote version.

### 5. Re-install with changes

```bash
# Interactive: shows diff per file, asks before overwriting
multikit install testkit

# Force: overwrite all without asking
multikit install testkit --force
```

### 6. Uninstall a kit

```bash
multikit uninstall testkit
```

Removes all kit files from `.github/` and cleans up `multikit.toml`.

## Configuration

`multikit.toml` tracks your installed kits:

```toml
[multikit]
version = "0.1.0"
registry_url = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

[multikit.kits.testkit]
version = "1.0.0"
source = "remote"
files = [
    "agents/testkit.testdesign.agent.md",
    "agents/testkit.testcoverage.agent.md",
    "prompts/testkit.testdesign.prompt.md",
    "prompts/testkit.testcoverage.prompt.md",
]
```

## Development Setup

```bash
git clone https://github.com/devcomfort/multikit.git
cd multikit
uv sync            # or: pip install -e ".[dev]"
pytest             # run tests
```

### Key Dependencies

| Package         | Purpose                          |
| --------------- | -------------------------------- |
| cyclopts        | CLI framework (type-hint based)  |
| httpx           | HTTP client for downloading kits |
| pydantic        | Data validation for models       |
| tomli / tomli-w | TOML read/write                  |
