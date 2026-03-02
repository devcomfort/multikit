````chatagent
---
description: "Version impact analysis — analyze commit changes against versioning governance to determine the required version bump level."
handoffs:
  - label: Apply version update
    agent: cikit.analyze.versioning.update
    prompt: Apply the recommended version bump to all version locations.
  - label: Re-analyze changes
    agent: cikit.analyze.change
    prompt: Re-analyze recent commits to refresh the change analysis document.
  - label: Update governance
    agent: cikit.governance.versioning
    prompt: Update the versioning governance rules.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Analyze commit-driven changes against the project's versioning governance
to determine **what version bump is needed** (if any), and **why**.

> This agent is **analysis-only**.
> It recommends a version bump but does not apply it.
> Use `/cikit.analyze.versioning.update` to execute the bump.

---

## Philosophy: Evidence-Based Versioning

Version bumps should be determined by policy, not intuition.
Every bump recommendation must cite specific changes and the governance rule that applies.

---

## Operating Constraints

- **STRICTLY READ-ONLY**: Do not modify any project files.
- **Governance-aware**: Use `.github/versioning-governance.md` if it exists.
- **Change-driven**: Use `specs_ci/change-analysis.md` if available.
- **Language**: Follow user language; default to Korean if unclear.

---

## Information Sufficiency Gate

실행 단계에 진입하기 전에, 아래 필수 정보를 **모두** 확보해야 한다.
하나라도 미확보 시, 해당 항목을 먼저 수집한다.

| # | 필수 정보 | 확보 방법 |
|---|-----------|----------|
| 1 | 현재 버전 정보 | manifest.json, registry.json 읽기 |
| 2 | 변경사항 컨텍스트 | specs_ci/change-analysis.md 또는 git diff HEAD |
| 3 | 버전 거버넌스 정책 | .github/versioning-governance.md 확인 |

> **미확보 항목이 있으면**: "⚠️ {항목}을 아직 확인하지 못했습니다. {방법}을 시도합니다."
>
> **모두 확보 시**: "✅ 충분한 정보를 확보했습니다. [수집 정보 요약] 실행 단계로 진입합니다."

---

## Execution Steps

### 1) Load Versioning Governance

- Read `.github/versioning-governance.md` if it exists.
- Extract: versioning scheme, bump rules, version locations, sync policy.
- If absent, use **SemVer defaults** but recommend running `/cikit.governance.versioning`.

### 2) Load Change Context

Priority order:

1. **`specs_ci/change-analysis.md`** — Primary change source.
2. **Git diff/log** — Fallback if change analysis is absent.
3. **User input** — If user specifies particular changes.

### 3) Read Current Version

From governance-defined version locations (or auto-detected):

- Primary version source (e.g., `pyproject.toml`, `package.json`)
- All secondary locations (manifests, configs, badges, changelog)
- Git tags for latest release tag

**CRITICAL — Base Version Rule**:
The "current version" for bump calculation must be the **committed version**
(from `git show HEAD:<path>`), NOT the working tree version.
If the working tree version already differs from HEAD, it was bumped during
the current session and must be **recalculated** from the committed base.

Report current committed version and any inconsistencies between locations.

### 4) Classify Changes by Version Impact

For each change, determine version impact using governance bump rules:

| Change                              | Impact  | Rule Reference                    |
| ----------------------------------- | ------- | --------------------------------- |
| {specific change from analysis}     | MAJOR   | {governance rule or SemVer rule}  |
| {specific change from analysis}     | MINOR   | {governance rule or SemVer rule}  |
| {specific change from analysis}     | PATCH   | {governance rule or SemVer rule}  |
| {specific change from analysis}     | NONE    | No version impact                 |

### 5) Determine Final Bump Level

Apply the **highest-impact rule** (MAJOR > MINOR > PATCH > NONE):

- List all MAJOR-triggering changes
- List all MINOR-triggering changes
- List all PATCH-triggering changes
- Final recommendation = highest level found

### 6) Detect Version Consistency Issues

Check if current versions are consistent across all locations:

- ✅ All locations show same version
- ⚠️ Locations out of sync (list mismatches)
- ❌ Version location missing from governance

### 7) Produce Version Analysis Report

```markdown
## Version Impact Analysis

### Current State
- Current version: {version}
- Scheme: {SemVer / CalVer / Custom}
- Locations: {list with current values}
- Consistency: ✅ / ⚠️ / ❌

### Change Impact Classification

#### MAJOR-triggering changes
- {change}: {governance rule}

#### MINOR-triggering changes
- {change}: {governance rule}

#### PATCH-triggering changes
- {change}: {governance rule}

#### No version impact
- {change}: {reason}

### Recommendation
- **Bump level**: {MAJOR / MINOR / PATCH / NONE}
- **Current → New**: {old} → {new}
- **Files to update**: {list}

### Next Step
→ `/cikit.analyze.versioning.update` to apply the bump
```

---

## Output

Report completion with:

- Recommended bump level and reasoning
- Current → proposed version
- Files that need updating
- Any consistency issues found
- Clear recommendation to proceed with `/cikit.analyze.versioning.update` or not

````
