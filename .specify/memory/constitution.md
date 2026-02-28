<!--
SYNC IMPACT REPORT
==================
Version: 1.0.0 (Initial)
Changes:
- Established Core Principles:
  1. Intuitive CLI Experience
  2. Standardized Configuration
  3. Idempotent & Clean Operations
  4. Minimal & Modern Foundation
  5. Extensibility via Kits
- Defined Technology Standards (Python 3.10+, Cyclopts, Hatchling, Rye/uv)
- Set Governance (Version 1.0.0)

Templates Checked:
- .specify/templates/plan-template.md: ✅ Compatible (Placeholder refers to constitution)
- .specify/templates/spec-template.md: ✅ Compatible
- .specify/templates/tasks-template.md: ✅ Compatible

TODOs:
- None
-->

# Multikit Constitution

## Core Principles

### I. Intuitive CLI Experience

The tool must be easy to use, leveraging `cyclopts` for type-hint based command definition. Commands (`init`, `install`, `list`, `uninstall`, `diff`, `update`) must be discoverable, and behavior must be predictable and consistent with standard CLI patterns.

### II. Standardized Configuration

Strict adherence to Python ecosystem standards (TOML, `pyproject.toml` support) and VS Code Copilot agent folder structures (`.github/agents`, `.github/prompts`). Configuration must be centralized and schema-compliant.

### III. Idempotent & Clean Operations

File operations must be safe and reversible. `install` must handle existing files gracefully (e.g., prompt or skip), and `uninstall` must remove only what was installed, leaving no "zombie" files. State must be accurately tracked.

### IV. Minimal & Modern Foundation

Built on a modern Python stack (Python ≥ 3.10, `hatchling`, `rye`/`uv`) to ensure speed and maintainability. Avoid heavy dependencies; prefer lightweight, focused implementation.

### V. Extensibility via Kits

The "Kit" architecture is the single source of truth for extending functionality. Kits must be self-contained bundles of agents and prompts that can be versioned and distributed independently.

## Technology Standards

- **Language**: Python ≥ 3.10
- **CLI Framework**: Cyclopts
- **Build System**: Hatchling
- **Package Management**: Rye or uv
- **Configuration Format**: TOML

## Development Workflow

- **Spec-Driven Development**: All features must follow the Spec → Plan → Tasks workflow (Speckit).
- **Code Quality**: Type hints are mandatory (required by Cyclopts).
- **Testing**: New commands must have accompanying tests verifying file system side-effects.

## Governance

- This Constitution supersedes all other documentation or verbal agreements.
- Amendments require a Pull Request with updated versioning and rationale.
- All code reviews must verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-02-11 | **Last Amended**: 2026-02-11
