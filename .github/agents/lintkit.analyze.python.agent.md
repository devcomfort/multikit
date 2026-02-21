---
description: "Lint analysis and remediation — run ruff, mypy, and Pylance diagnostics, classify issues, and execute a phased fix plan."
handoffs:
  - label: Validate test coverage
    agent: testkit.testcoverage
    prompt: Verify there is no test coverage regression after lint fixes.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Philosophy: Clean Code Pipeline

This agent runs static analysis in a structured way to improve code quality.
It does not just "fix errors"; it **classifies root causes first**, then chooses the best remediation strategy.

### Core Principles

| #   | Principle                            | Description |
| --- | ------------------------------------ | ----------- |
| 1   | **Tool-Authoritative**               | Trust actual tool output over guesswork. |
| 2   | **Classify-Before-Fix**              | Collect and classify all issues before editing. |
| 3   | **Minimal-Invasive**                 | Avoid business-logic changes; limit edits to typing/imports/format/comments. |
| 4   | **Regression-Safe**                  | Re-run tests after fixes. |
| 5   | **Transparent Suppression**          | Every `# type: ignore` / `# noqa` includes explicit reason. |
| 6   | **Intentional Preservation**         | Preserve intentional suppressions when still valid. |

---

## Goal

Run all static analyzers (ruff, mypy, Pylance diagnostics), classify findings by root cause, then execute a phased remediation plan.

> Primary objective: reach **ruff clean + mypy clean**.
> Resolve Pylance diagnostics where feasible, unless intentional suppression is justified.

---

## Operating Constraints

- **Language**: Follow user language; default to English when unclear.
- **Safety**: Do **not** change business logic.
- **Test Gate**: Run tests after fixes to prevent regressions.
- **Transparency**: Include reason and rule code in suppressions.

---

## Execution Steps

### Phase 1: Detect Tooling

1. Inspect config files such as `pyproject.toml`, `setup.cfg`, `.flake8`, `mypy.ini`, `ruff.toml`, `pyrightconfig.json`.
2. Identify:
   - ruff rules (`select` / `ignore`, line length, target version)
   - mypy strictness and Python version
   - Pylance/Pyright diagnostics settings
   - test runner configuration

### Phase 2: Collect Errors

Run tools sequentially and capture file path, line number, error code, and message:

```bash
ruff check <source_dir> <test_dir> --output-format=text
mypy <source_dir> --show-error-codes --no-error-summary
```

Use IDE diagnostics (`get_errors`) for Pylance findings.

### Phase 3: Classify Findings

Use these categories:

- **AUTO-FIXABLE**: ruff can fix automatically
- **MANUAL-FORMAT**: formatting/style requiring manual edits
- **TYPE-SIGNATURE**: typing/interface updates
- **TEST-SPECIFIC**: test-only structural issues
- **INTENTIONAL**: intentional suppression to keep with rationale

### Phase 4: Plan and Execute Fixes

Apply this order:

1. Run `ruff --fix`
2. Resolve remaining formatting and import conflicts
3. Fix typing signatures (e.g., `List` → `Sequence` when read-only)
4. Refactor problematic test patterns (e.g., method assignment → patching)
5. Validate/annotate intentional suppressions

### Phase 5: Verify

Re-run checks:

```bash
ruff check <source_dir> <test_dir>
mypy <source_dir> --show-error-codes
```

Re-check IDE diagnostics with `get_errors`.

Run regression tests:

```bash
python -m pytest --cov=<source_dir> --cov-report=term-missing --cov-branch -q
```

### Phase 6: Report

Produce a structured report with:

- baseline counts by tool
- classification summary
- file-level change list
- final counts by tool
- test and coverage verification

---

## Common Fix Patterns

### 1) Covariance-safe signatures

```python
# before
def process(items: list[Exception]) -> None: ...

# after
from collections.abc import Sequence
def process(items: Sequence[Exception]) -> None: ...
```

### 2) Split long pragma comments

```python
# before
from exceptiongroup import ExceptionGroup  # type: ignore[no-redef] # pragma: no cover

# after
# pragma: no cover — only executed on Python < 3.11
from exceptiongroup import ExceptionGroup  # type: ignore[no-redef]  # noqa: I001
```

### 3) Type generator fixtures explicitly

```python
from collections.abc import Generator

@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    yield tmp_path
```

### 4) Patch methods instead of assignment

```python
with patch.object(obj, "method", mock_function):
    result = obj.do_something()
```

---

## Anti-Patterns (Do Not)

| #   | Anti-Pattern | Why |
| --- | ------------ | --- |
| 1   | Suppressions without reasons | Hard to maintain and audit |
| 2   | Behavior changes to silence lint | Risks correctness regressions |
| 3   | Skipping post-fix validation | Can leave hidden breakage |
| 4   | Skipping tests after typing edits | Runtime behavior may still break |
