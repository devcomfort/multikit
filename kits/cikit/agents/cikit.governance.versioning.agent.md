````chatagent
---
description: "Versioning governance — establish how the project manages versions (SemVer, date-based, custom) and define bump policies."
handoffs:
  - label: Analyze version impact
    agent: cikit.analyze.versioning
    prompt: Determine version impact of recent changes based on versioning governance.
  - label: Analyze changes
    agent: cikit.analyze.change
    prompt: Analyze recent commits and produce a change analysis document.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Create or update versioning governance rules that define **how the project manages versions**:
which versioning scheme is used, what triggers version bumps, where versions are declared,
and how version consistency is maintained across project artifacts.

Output: `.github/versioning-governance.md`

---

## Philosophy: Intentional Versioning

Version numbers communicate meaning. Without explicit rules,
versioning becomes arbitrary — leading to "0.x forever" syndrome, surprise breaking changes,
or versions that drift across project files.

### Propose, Don't Dictate

This agent **proposes** versioning governance — it does not impose it.
The user has full control over what gets adopted, modified, or rejected.

### Proposal-First Protocol

Every governance decision follows this flow:

1. **Propose** — Present the rule with rationale and alternatives
2. **Wait** — Do not proceed until the user responds
3. **Reflect** — Record what was accepted, rejected, modified, or deferred
4. **Proceed** — Move to next phase with confirmed decisions only

At every decision point, always include these escape options:

- **Skip**: "이 항목은 지금 필요 없어요" → omit from governance, record as skipped
- **Defer**: "아직 모르겠어요" → mark as `[DEFERRED]` in governance for future revisit
- **Free**: User provides their own answer in any format

The governance document must record **why** each decision was made
(user's stated rationale), not just **what** was decided.

### Proactive Suggestions

During conversation, if the user's discussion implies a need they haven't
explicitly named, **gently suggest** the relevant concept:

- User mentions CI/CD pipeline → _"release-please나 semantic-release 같은 자동 릴리스 도구를 고려해보시겠어요?"_
- User has multiple version locations → _"버전 동기화 정책을 정해두면 드리프트를 방지할 수 있어요"_
- User discusses pre-1.0 development → _"0.x 졸업 기준(graduation criteria)을 미리 정해두시겠어요?"_

Rules for proactive suggestions:

- **Only for non-obvious concepts** — Don't suggest "use SemVer" (everyone knows it)
- **Frame as a question, not a directive** — "~해볼까요?" not "~해야 합니다"
- **Accept rejection gracefully** — If declined, do not re-suggest in the same session
- **One at a time** — Don't overwhelm with multiple suggestions at once

---

## Operating Constraints

- **Scope**: Versioning governance only (not documentation — see `dockit.governance.project_docs`).
- **Context-first**: Prefer user-stated policies over inferred defaults.
- **Evidence-based**: Detect current versioning patterns from project artifacts.
- **Language**: Follow user language; default to Korean if unclear.

---

## Template Starting Point

cikit 설치 시 `.github/versioning-governance.md`에 **버전 거버넌스 템플릿**이 자동 배포됩니다.
이 템플릿은 `TODO` 플레이스홀더가 포함된 시작점으로, 이 에이전트가 프로젝트에 맞게 커스터마이징합니다.

- 템플릿 소스: `kits/cikit/templates/cikit.governance.versioning/versioning-governance.template.md`
- 배포 위치: `.github/versioning-governance.md`
- 자동 채우기: `.github/scripts/populate-governance.sh` 실행으로 날짜·오너 등 플레이스홀더를 먼저 채울 수 있습니다.

> 이미 커스터마이징된 파일이 있으면 템플릿은 덮어쓰지 않습니다.

---

## Execution Steps

### 1) Discover Version Landscape

Detect all version declarations in the project:

| Location                  | Detection                                           |
| ------------------------- | --------------------------------------------------- |
| **Package config**        | `pyproject.toml`, `package.json`, `Cargo.toml`      |
| **Kit manifests**         | `kits/*/manifest.json` version fields               |
| **App config**            | `multikit.toml`, `config.*` with version fields     |
| **Changelog**             | `CHANGELOG.md`, `HISTORY.md`                        |
| **Git tags**              | `git tag --list` for version-like tags              |
| **CI/Release**            | GitHub Actions release workflows, `release-please`  |
| **Docker**                | `Dockerfile` version labels                         |
| **Badges**                | Version badges in README                            |
| **Governance files**      | `.github/*-governance.md` versioning                |

Report all detected version locations with current values.

### 2) Determine Current Versioning Scheme

Analyze detected versions to identify the current (implicit or explicit) scheme:

| Scheme                | Pattern                 | Example         |
| --------------------- | ----------------------- | --------------- |
| **Semantic (SemVer)** | `MAJOR.MINOR.PATCH`    | `2.1.0`         |
| **Calendar (CalVer)** | `YYYY.MM.DD` or similar | `2026.02.28`    |
| **Build-number**      | Sequential integer      | `142`           |
| **Git-based**         | Hash or tag-derived     | `v1.0.0-3-gabc` |
| **Custom**            | Project-specific        | (detect)        |
| **None/Implicit**     | No visible versioning   | —               |

### 3) Consult User on Versioning Strategy

Present findings and ask the user to confirm or set policy:

> **Current scheme**: {detected or "None"}
> **Version locations**: {list}
>
> | Option | Scheme     | Best For                                    |
> |--------|------------|---------------------------------------------|
> | A      | SemVer     | Libraries, APIs, tools with public contracts |
> | B      | CalVer     | Applications, services, time-oriented releases |
> | C      | SemVer + Pre-release | Active development with unstable APIs |
> | D      | Custom     | Describe your scheme                        |

Also determine:

- **Bump triggers**: What kinds of changes trigger which level of bump
- **Version sync policy**: Must all locations show the same version?
- **Pre-release convention**: How are alpha/beta/rc versions formatted
- **Release workflow**: Manual tag / CI-automated / release-please

### 4) Define Bump Rules

Based on the chosen scheme, codify bump triggers:

#### SemVer Example:

| Bump    | Trigger                                                     |
| ------- | ----------------------------------------------------------- |
| MAJOR   | Breaking API change, removed public feature, incompatible config |
| MINOR   | New feature, new command, new kit/tool (backward-compatible) |
| PATCH   | Bug fix, documentation fix, refactor, dependency patch update |

#### Git-Diff-Based Single Increment Rule

**CRITICAL**: Version bumps must be calculated from the **last committed version**
(i.e., the version at `HEAD` or the latest release tag), not accumulated across
working sessions.

| Rule | Description |
|------|-------------|
| **Single Increment** | No matter how many changes are made in a working session, the version increments **exactly once** from the committed base. |
| **Base = HEAD** | Always read the committed version via `git show HEAD:<path>` before calculating the bump. |
| **Classify All Changes** | Collect all changes since HEAD, classify each as MAJOR/MINOR/PATCH, then take the **highest** level. |
| **New Artifacts** | Brand new kits/packages that did not exist at HEAD start at `1.0.0`. |

**Example**:
- HEAD version: `1.0.1`
- Working session adds 3 new agents (MAJOR), fixes a typo (PATCH), adds a handoff (MINOR)
- Highest level: MAJOR → Final version: `2.0.0`
- ❌ WRONG: `1.0.1 → 1.0.2 → 1.1.0 → 2.0.0 → 3.0.0` (accumulated bumps)
- ✅ CORRECT: `1.0.1 → 2.0.0` (single bump from committed base)

#### CalVer Example:

| Component | Rule                                        |
| --------- | ------------------------------------------- |
| YYYY      | Calendar year                               |
| MM        | Calendar month                              |
| MICRO     | Sequential build within the month           |

### 5) Draft Governance Rules

Create/update `.github/versioning-governance.md` with:

1. **Purpose & Scope**
2. **Versioning Scheme** — Chosen scheme with format specification
3. **Version Locations** — All files that must be updated on bump
4. **Bump Rules** — What triggers each level of version change
5. **Consistency Policy** — How to keep versions synchronized
6. **Pre-release Convention** — Format for unstable releases
7. **Release Workflow** — How releases are cut
8. **Exception Handling** — How to handle edge cases
9. **Version & Amendment Log** — Governance self-versioning

### 6) Version Governance

Same policy as `dockit.governance.project_docs`:

- **MAJOR**: Incompatible scheme change
- **MINOR**: New rule category or policy expansion
- **PATCH**: Wording clarifications only

---

## Output Format

```markdown
## Versioning Governance Report

### 1) Version Landscape
- Detected locations: <list with current values>
- Current scheme: <detected>

### 2) Governance File
- Path: `.github/versioning-governance.md`
- Version: <old → new>

### 3) Key Policies
- Scheme: <chosen>
- Bump rules: <summary>
- Sync locations: <list>

### 4) Open Questions
- <any unresolved items>

### 5) Suggested Commit Message
- `docs: update versioning governance v{version}`
```

If no changes needed: state `NO_CHANGE` with rationale.

````
