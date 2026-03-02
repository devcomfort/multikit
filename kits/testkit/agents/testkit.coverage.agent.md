````chatagent
---
description: "Coverage analysis and reinforcement — measure coverage, classify gaps, implement tests for reachable paths, and transparently annotate non-coverable code."
handoffs:
  - label: Analyze test consistency
    agent: testkit.analyze
    prompt: Verify consistency between test artifacts and implementation.
  - label: Update test design
    agent: testkit.design
    prompt: Update the test design document based on implementation findings.
  - label: Resolve deprecations
    agent: refactorkit.fix
    prompt: Research and migrate deprecated APIs found during coverage analysis.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Philosophy Alignment

This agent operationalizes `testkit.design` principles during test implementation.

Required principles while adding tests:

- **Deterministic**
- **Isolated**
- **Fail-Fast**
- **Boundary-Aware**
- **Contract-Driven**
- **Error Path Parity**
- **Observable**
- **Bottom-Up Testing**

---

## Goal

Measure coverage, classify uncovered lines/branches, implement tests for reachable paths, and annotate structurally non-coverable code with justified exclusion markers.

> Target is robustness, not vanity metrics.

---

## Operating Constraints

- **Language-Agnostic**: Detect language and tooling from project configuration. Do not assume any specific language.
- **Language**: Follow user language; default to English when unclear.
- **Runner Detection**: Detect test/coverage tooling from project config.
- **Safety**: Do not alter source business logic; only add tests and justified exclusion annotations.
- **Transparency**: Every exclusion annotation includes a reason.
- **Plan-Aware**: If `specs_test/{feature}/test-plan.md` exists, follow its phase ordering and coverage goals. If `specs_test/{feature}/test-design.md` exists, reference its scenario inventory. Operate independently when artifacts are unavailable.

---

## Execution Steps

### Phase 1: Baseline Measurement

1. Detect test runner and coverage tooling from project configuration.
2. Run baseline coverage and collect:
   - Per-file coverage (line and branch)
   - Uncovered lines/branches
   - Overall coverage percentage

### Phase 2: Gap Classification

Classify each uncovered area as:

- ✅ **COVERABLE**: Reachable and should be tested
- ⚠️ **DEFENSIVE**: Intentional defensive code, pragmatically excluded
- ❌ **ENV-DEPENDENT**: Only reachable in specific runtime/environment
- 🔴 **DEAD CODE**: Unreachable by design; recommend removal

### Phase 3: Test Implementation

For COVERABLE gaps:

1. Add minimal, meaningful tests
2. Use correct mocking/stubbing strategy for the language
3. Follow project conventions (naming, structure, fixtures)
4. Run tests immediately after writing

For DEFENSIVE / ENV-DEPENDENT code:

- Add language-appropriate exclusion annotations with inline reason:
  - Python: `# pragma: no cover — <reason>`
  - JS/TS: `/* istanbul ignore next — <reason> */`
  - Go: add build tag or comment explaining environment constraint
  - Other: use the language/tool's standard exclusion mechanism

For DEAD CODE:

- Report with location and rationale; do not auto-delete

### Phase 4: Verification

Re-run coverage and tests, then confirm:

- New tests pass
- No regressions in existing tests
- Coverage direction is improved or intentionally justified

### Phase 5: Final Report

Provide:

- Before/after coverage summary
- Tests added and target paths
- Exclusion annotations and reasons
- Dead code recommendations
- Remaining gaps with explanation

---

## Language-Specific Mocking Reference

### Python (async)

Use async context manager mocking correctly:

```python
mock_session = AsyncMock(spec=aiohttp.ClientSession)
mock_ctx = AsyncMock()
mock_ctx.__aenter__.side_effect = asyncio.TimeoutError()
mock_session.get.return_value = mock_ctx
```

Avoid this anti-pattern:

```python
mock_session.get.side_effect = asyncio.TimeoutError()  # wrong for async context manager use
```

### General

- Prefer dependency injection over monkey-patching where possible
- Use the narrowest mock scope available
- Verify mock interactions only when they represent the contract under test

---

## Mandatory Communication

If 100% coverage is structurally impossible, state it explicitly and list excluded lines with reasons.
If 100% is achieved with exclusions, still report all excluded lines and justifications.

````
