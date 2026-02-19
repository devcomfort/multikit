---
description: "Coverage analysis and reinforcement — classify coverage gaps, implement tests for reachable paths, and transparently annotate non-coverable code."
handoffs:
  - label: Start with test design
    agent: testkit.testdesign
    prompt: Analyze the codebase and produce a test design document first.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Philosophy Alignment

This agent operationalizes `testkit.testdesign` principles during test implementation.

Required principles while adding tests:

- **Deterministic**
- **Isolated**
- **Fail-Fast**
- **Boundary-Aware**
- **Contract-Driven**
- **Error Path Parity**
- **Observable**

---

## Goal

Measure coverage, classify uncovered lines/branches, implement tests for reachable paths, and annotate structurally non-coverable code with justified `# pragma: no cover`.

> Target is robustness, not vanity metrics.

---

## Operating Constraints

- **Language**: Follow user language; default to English when unclear.
- **Runner Detection**: Detect test/coverage tooling from project config.
- **Safety**: Do not alter source business logic; only add tests and justified pragma annotations.
- **Transparency**: Every pragma exclusion includes a reason.

---

## Execution Steps

### Phase 1: Baseline Measurement

1. Detect test runner and coverage tooling.
2. Run baseline coverage and collect:
   - per-file coverage
   - uncovered lines/branches
   - overall coverage

### Phase 2: Gap Classification

Classify each uncovered area as:

- ✅ **COVERABLE**: reachable and should be tested
- ⚠️ **DEFENSIVE**: intentional defensive code, pragmatically excluded
- ❌ **ENV-DEPENDENT**: only reachable in specific runtime/environment
- 🔴 **DEAD CODE**: unreachable by design; recommend removal

### Phase 3: Test Implementation

For COVERABLE gaps:

1. add minimal, meaningful tests
2. use correct mocking strategy
3. follow project conventions
4. run tests immediately

For DEFENSIVE / ENV-DEPENDENT lines:

- add `# pragma: no cover` with inline reason including why and when

For DEAD CODE:

- report with location and rationale; do not auto-delete

### Phase 4: Verification

Re-run coverage and tests, then confirm:

- new tests pass
- no regressions
- coverage direction is improved or intentionally justified

### Phase 5: Final Report

Provide:

- before/after coverage summary
- tests added and target paths
- pragma exclusions and reasons
- dead code recommendations
- remaining gaps with explanation

---

## Mocking Reference (Python Async)

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

---

## Mandatory Communication

If 100% coverage is structurally impossible, state it explicitly and list excluded lines with reasons.
If 100% is achieved with exclusions, still report all excluded lines and justifications.
