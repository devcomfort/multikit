---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This command MUST run only after `/speckit.tasks` has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The project constitution (`.specify/memory/constitution.md`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `/speckit.analyze`.

## Execution Steps

### 1. Initialize Analysis Context

Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` once from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS. Derive absolute paths:

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md

Abort with an error message if any required file is missing (instruct the user to run missing prerequisite command).
For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**

- Overview/Context
- Functional Requirements
- Non-Functional Requirements
- User Stories
- Edge Cases (if present)

**From plan.md:**

- Architecture/stack choices
- Data Model references
- Phases
- Technical constraints

**From tasks.md:**

- Task IDs
- Descriptions
- Phase grouping
- Parallel markers [P]
- Referenced file paths

**From constitution:**

- Load `.specify/memory/constitution.md` for principle validation

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" → `user-can-upload-file`)
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Task coverage mapping**: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases)
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements

### 4. Detection Passes (Token-Efficient Analysis)

Enumerate ALL detected findings without artificial limits. Focus on high-signal, actionable findings.

#### A. Duplication Detection

- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection

- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.)

#### C. Underspecification

- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Tasks referencing files or components not defined in spec/plan

#### D. Constitution Alignment

- Any requirement or plan element conflicting with a MUST principle
- Missing mandated sections or quality gates from constitution

#### E. Coverage Gaps

- Requirements with zero associated tasks
- Tasks with no mapped requirement/story
- Non-functional requirements not reflected in tasks (e.g., performance, security)

#### F. Inconsistency

- Terminology drift (same concept named differently across files)
- Data entities referenced in plan but absent in spec (or vice versa)
- Task ordering contradictions (e.g., integration tasks before foundational setup tasks without dependency note)
- Conflicting requirements (e.g., one requires Next.js while other specifies Vue)

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates constitution MUST, missing core spec artifact, or requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Structured Analysis Report

Output a Markdown report (no file writes) split into two actionable sections. Report ALL findings—do not cap at a fixed number.

---

## Specification Analysis Report

### 6-A. 의사결정 불필요 수정사항 (No Decision Needed)

Issues with a single clear fix that the agent (or developer) can apply without ambiguity.

| ID   | Category      | Severity | Location(s) | Summary              | Proposed Fix         |
| ---- | ------------- | -------- | ----------- | -------------------- | -------------------- |
| N-01 | Inconsistency | MEDIUM   | plan.md:L42 | Stale reference to X | Replace "X" with "Y" |

(One row per finding. Stable IDs prefixed `N-` for no-decision.)

### 6-B. 의사결정 필요/가능 수정사항 (Decision Needed / Decision Possible)

Issues where multiple valid resolutions exist. Present **3–5 mutually exclusive options** plus a free-form fallback for each.
Include items where a decision is not strictly required but the developer may benefit from choosing.

**Dependency grouping:** Before presenting D-\* items, classify each as independent or dependent:

- **Independent**: Answering this item does NOT change, invalidate, or create other D-\* items.
- **Dependent**: Answering this item changes the options, relevance, or existence of other D-\* items. Mark with `⚠️ depends on: D-{predecessor_id}`.

If all items are independent, present them all at once. If dependency chains exist, note them so the user can answer predecessors first. Items that depend on others should include the dependency annotation in their block header.

For each finding, output this block:

> **D-{id}** | {Category} | {Severity} | {Location(s)}
> **Summary:** {description}
>
> | Option                 | Description                              |
> | ---------------------- | ---------------------------------------- |
> | A                      | …                                        |
> | B                      | …                                        |
> | C                      | …                                        |
> | (D/E as needed, max 5) | …                                        |
> | 서술형                 | 위 선택지에 해당하지 않는 경우 직접 작성 |
>
> **Recommended:** Option {X} — {1-2 sentence reasoning}

(Stable IDs prefixed `D-` for decision-needed.)

---

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
| --------------- | --------- | -------- | ----- |

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**

- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count
- No-Decision Issues Count
- Decision-Needed Issues Count

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `/speckit.implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /speckit.specify with refinement", "Run /speckit.plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'"

### 8. Offer Remediation

After presenting the report:

1. **No-Decision items (N-\*)**: Ask the user "N-\* 수정사항을 일괄 적용할까요?" (batch-apply all, or let the user exclude specific IDs).
2. **Decision items (D-\*)**: Collect the user's option choices (letter or free-form) for each D-\* item. The user may answer all at once (e.g., "D-01: B, D-02: A, D-03: 서술형—내 의견은…") or answer incrementally. - If dependency chains were annotated, remind the user to answer predecessor items first. After predecessors are resolved, re-evaluate dependent items (options may change or items may become unnecessary) and present updated D-\* blocks for the next round.3. Do NOT apply any edits until the user explicitly approves. Present a final confirmation summary before writing.

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Exhaustive output**: Report ALL detected findings without artificial row limits; prefer concise per-row descriptions to stay readable
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

### Analysis Guidelines

- **NEVER modify files** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero issues gracefully** (emit success report with coverage statistics)

## Context

$ARGUMENTS
