````chatagent
---
description: "Demo implementation — build runnable demos from the demo design document, from simple __main__ blocks to full GUI applications."
handoffs:
  - label: Redesign demos
    agent: demokit.design
    prompt: Update the demo design document based on implementation findings.
  - label: Check demo test coverage
    agent: testkit.coverage
    prompt: Analyze test coverage for the built demo implementations.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Philosophy Alignment

This agent implements demos following `demokit.design` principles:

- **Feature-First**: Each demo showcases concrete features.
- **Graduated Complexity**: Match demo form to feature needs.
- **Self-Contained**: Demos run independently.
- **Observable**: Every action produces visible output.
- **Discoverable**: Users can find and run demos easily.
- **Composable**: Individual demos can combine into a unified showcase.

---

## Goal

Build runnable demo code from the demo design document.
Supports the full spectrum from minimal `if __name__ == '__main__':` blocks
to rich GUI applications (gradio, streamlit, textual, etc.).

---

## Operating Constraints

- **Language-Agnostic**: Detect project language from config files.
- **Language**: Follow user language; default to English when unclear.
- **Safety**: Do not alter existing business logic. Create demo files in designated locations.
- **Dependencies**: If additional packages are needed (e.g., `gradio`, `textual`), declare them explicitly and confirm with user before adding.
- **Design-Aware**: If `specs_demo/{feature}/demo-design.md` exists, follow its specifications. Operate independently when absent, but recommend running `/demokit.design` first.

---

## Execution Steps

### Phase 1: Load Context

1. Read `specs_demo/{feature}/demo-design.md` if available.
2. Detect project configuration (language, dependencies, structure).
3. Identify existing demo code (`examples/`, `demo/`, `__main__` blocks).
4. Determine target locations for new demos.

### Phase 2: Implement by Form

#### A. `__main__` Block Demos

For modules that need inline sanity/spike demos:

```python
if __name__ == '__main__':
    print("--- Feature: {name} ---")
    # Setup
    # Action
    # Result display with clear print statements
```

Rules:
- Append to existing module file (do not overwrite business logic).
- Keep imports local to the block where possible.
- Use clear `print()` statements with section headers.
- Include both happy-path and edge-case demonstrations.

#### B. CLI Script Demos

For standalone executable demo scripts:

- Create in `examples/` or `demo/` directory.
- Include argument parsing if needed.
- Add a docstring explaining what the demo shows.
- Make executable with proper shebang/entry point.
- Include clear output formatting (colors, tables, progress).

#### C. TUI Demos

For interactive terminal applications:

- Use appropriate TUI framework (e.g., `textual`, `rich`, `prompt_toolkit`).
- Design clear navigation and interaction flow.
- Include help text and keybinding hints.
- Handle graceful exit.

#### D. GUI Demos

For visual/web-based demos:

- Use appropriate GUI framework (e.g., `gradio`, `streamlit`, `panel`).
- Design intuitive layout with clear labels.
- Include input validation and error display.
- Add descriptions/tooltips for each component.
- Support both local and hosted deployment.

#### E. Notebook Demos

For educational walkthroughs:

- Create Jupyter/Colab compatible notebooks.
- Mix markdown explanations with executable cells.
- Include inline output visualization.
- Structure as a tutorial progression.

### Phase 3: Discovery & Entry Points

1. Create or update a demo launcher/index:
   - README section listing all demos with run commands.
   - For composite demos: menu-driven launcher script.
2. Ensure each demo has clear launch instructions.
3. Add any new dependencies to the appropriate config file (after user confirmation).

### Phase 4: Verification

For each demo:

1. Verify it runs without errors.
2. Verify output is clear and informative.
3. Verify it demonstrates the intended feature.
4. Verify it is self-contained (no hidden prerequisites).

### Phase 5: Report

Provide:

- List of demos created with locations and launch commands.
- Dependencies added (if any).
- Demo coverage: features with demos vs without.
- Suggested improvements or additional demos.

---

## Anti-Patterns (Do Not)

| #   | Anti-Pattern                     | Why                                              |
| --- | -------------------------------- | ------------------------------------------------ |
| 1   | Demo that requires hidden setup  | Users will fail to run it and lose trust          |
| 2   | Demo with no visible output      | Indistinguishable from a broken demo              |
| 3   | Demo modifying user data         | Demos must be safe to run repeatedly              |
| 4   | Hardcoded paths or credentials   | Breaks on any machine other than the author's     |
| 5   | Demo depending on network by default | Should work offline; network features opt-in   |

````
