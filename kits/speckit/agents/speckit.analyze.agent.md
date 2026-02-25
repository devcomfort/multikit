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

#### Presentation Mode

The agent supports two output modes:

- **Batch Mode** (default): Present all N-\* and D-\* findings at once. This is the standard report format.
- **Sequential Mode**: Present findings one at a time, collecting user response before proceeding to the next. Activated when user explicitly requests (e.g., "하나씩 보여줘", "one at a time", "하나씩 처리하자").

**Mode switching:**

- Default is Batch unless user requests otherwise. User can switch at any time ("나머지 전부 보여줘" → Batch, "하나씩 보자" → Sequential).
- Acknowledge the mode switch briefly and continue with remaining items in the new mode.

**Sequential Mode ordering (N-\* then D-\*):**

1. N-\* items first (no decision needed), one at a time, asking approval per item.
2. D-\* items next: independent items first, then dependent items after their predecessors are resolved.
3. If a dependency cluster must be decided simultaneously, present the entire cluster as one unit and explain why they are grouped.
4. Between items, briefly state remaining count (e.g., "N-03 완료. 남은 항목: N-04, N-05, D-01~D-03").

---

## Specification Analysis Report

### 6-A. No Decision Needed

Issues with a single clear fix that the agent (or developer) can apply without ambiguity.

`Summary` writing rules (mandatory):

- Do not use vague evaluative phrases (e.g., "misaligned", "insufficient", "contradictory") in isolation.
- Always use a **cause-effect structure**.
- Recommended template: `The statement B in artifact A and the statement D in artifact C cause effect E.`
- Each sentence must cite all relevant source references (artifact/section) exhaustively, and clearly state the resulting impact from their combination.
- Example: `The minimum observable signal definition in spec.md FR-019 and the MUST requirement in constitution.md Principle V cause a conflict in observability contract interpretation.`

**Interpretability principle**: A reader of the Summary must understand "why this is a problem" without re-opening the original artifacts. The standard is completeness of causal reasoning, not the number of cited references.

| ID   | Category      | Severity | Location(s) | Summary              | Proposed Fix         |
| ---- | ------------- | -------- | ----------- | -------------------- | -------------------- |
| N-01 | Inconsistency | MEDIUM   | plan.md:L42 | Stale reference to X | Replace "X" with "Y" |

(One row per finding. Stable IDs prefixed `N-` for no-decision.)

### 6-B. Decision Needed / Decision Possible

Issues where multiple valid resolutions exist. Present **mutually exclusive options** plus a free-form fallback for each.
Include items where a decision is not strictly required but the developer may benefit from choosing.

`Summary` writing rules (mandatory):

- Do not use abstract evaluations like "ambiguous", "conflicting", or "unclear" in isolation.
- Always write a **deductive explanation** following this order: `evidence (observed fact) → interpretation (problem) → impact (risk/consequence) → why a decision is needed`.
- Each paragraph must cite all relevant source references (artifact/section) exhaustively, and state the resulting impact from their combination.
- Explain why no single correct answer exists (why alternatives coexist) and identify the key comparison axis between options (e.g., accuracy / complexity / operational cost).
- Recommended template: `The statement B in artifact A and the statement D in artifact C cause effect E; approaches F and G are both viable resolutions, so a decision is needed.`

**Interpretability principle**: A reader of the Summary must understand "why this issue requires a decision" and "what criteria to use when comparing options" without re-opening the original artifacts. The standard is completeness of causal reasoning, not the number of cited references.

**Dependency grouping:** Before presenting D-\* items, classify each as independent or dependent:

- **Independent**: Answering this item does NOT change, invalidate, or create other D-\* items.
- **Dependent**: Answering this item changes the options, relevance, or existence of other D-\* items. Mark with `⚠️ depends on: D-{predecessor_id}`.

If all items are independent, present them all at once. If dependency chains exist, note them so the user can answer predecessors first. Items that depend on others should include the dependency annotation in their block header.

For each finding, output this block:

> **D-{id}** | {Category} | {Severity} | {Location(s)}
> **Summary:** {description}
>
> | Option           | Description                           |
> | ---------------- | ------------------------------------- |
> | A                | …                                     |
> | B                | …                                     |
> | C                | …                                     |
> | (more as needed) | …                                     |
> | Free-form        | Provide your own answer if none apply |
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

**Visual Concreteness Principle (mandatory):** When presenting proposed fixes for approval, the user must be able to evaluate each fix **purely by reading the presented text**—without mentally composing what the result would look like. Choose the most effective presentation format per item:

- **Fenced code block** (` ```markdown `): Multi-line insertions/replacements, new sections, or structural changes.
- **Inline diff** (` `old`→`new` `): Single-term renames, short phrase replacements, or value swaps.
- **Bullet summary with quoted excerpt**: When the change is a minor addition to an existing list or table row.

The agent selects the format that maximizes readability for the specific change size and type. The invariant is: **the user sees the exact final text**, not an abstract description of it.

This applies to:

- **N-\* items**: Show the concrete insertion/replacement text for every fix.
- **D-\* items**: Show the concrete text for the **recommended option**. If the user selects a different option, regenerate the snippet for confirmation before applying.

After presenting the report:

1. **No-Decision items (N-\*)**: For each N-\* item, present a labeled heading (e.g., `### N-01: …`) with the exact text to add or replace using the most appropriate format above. After all items, ask: "Batch-apply all N-\* fixes?" (the user may exclude specific IDs).
2. **Decision items (D-\*)**: Collect the user's option choices (letter or free-form) for each D-\* item. The user may answer all at once (e.g., "D-01: B, D-02: A, D-03: free-form—my reasoning is…") or answer incrementally. If dependency chains were annotated, remind the user to answer predecessor items first. After predecessors are resolved, re-evaluate dependent items (options may change or items may become unnecessary) and present updated D-\* blocks for the next round.
3. Do NOT apply any edits until the user explicitly approves. Present a final confirmation summary before writing.

**In Sequential Mode**, the above batch flow is replaced:

- Present one N-\* fix at a time with its concrete text. After user approves/rejects, proceed to the next.
- Then present one D-\* item at a time (independent first). Collect choice, then proceed.
- For dependent D-\* clusters, present the cluster as a unit.
- After all items (or user signals "done"), apply approved edits in a single batch.

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Exhaustive output**: Report ALL detected findings without artificial row limits; prefer concise per-row descriptions to stay readable
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts
- **Self-contained references**: Every cross-reference ID (FR-015, SC-008, T035, US6, etc.) MUST include a brief inline description on first mention in each section so the reader never needs to open another file to understand the reference. Format: `ID(short description)` — e.g., `US6(설치된 킷 업데이트)`, `FR-015(update --force/--registry)`, `SC-008(재시도 백오프 검증)`, `T035(update retry/backoff 테스트)`. Subsequent mentions in the same section may use the bare ID.

### Response Language

- If the user explicitly requests a language, use that language for the entire report.
- Otherwise, infer the user's preferred language from recent conversation messages (e.g., if the user writes in Korean, respond in Korean).
- Technical identifiers (IDs, file paths, code snippets) remain in their original form regardless of response language.

### Analysis Guidelines

- **NEVER modify files** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero issues gracefully** (emit success report with coverage statistics)

## Context

$ARGUMENTS
