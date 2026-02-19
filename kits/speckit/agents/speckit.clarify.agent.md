---
description: Identify ALL underspecified areas in the current feature spec, classify them as no-decision-needed vs decision-needed (with 3-5 options + free-form), and encode answers back into the spec.
handoffs:
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Detect and reduce ambiguity or missing decision points in the active feature specification and record the clarifications directly in the spec file.

Note: This clarification workflow is expected to run (and be completed) BEFORE invoking `/speckit.plan`. If the user explicitly states they are skipping clarification (e.g., exploratory spike), you may proceed, but must warn that downstream rework risk increases.

Execution steps:

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` from repo root **once** (combined `--json --paths-only` mode / `-Json -PathsOnly`). Parse minimal JSON payload fields:
   - `FEATURE_DIR`
   - `FEATURE_SPEC`
   - (Optionally capture `IMPL_PLAN`, `TASKS` for future chained flows.)
   - If JSON parsing fails, abort and instruct user to re-run `/speckit.specify` or verify feature branch environment.
   - For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. Load the current spec file. Perform a structured ambiguity & coverage scan using this taxonomy. For each category, mark status: Clear / Partial / Missing. Produce an internal coverage map used for prioritization (do not output raw map unless no questions will be asked).

   Functional Scope & Behavior:
   - Core user goals & success criteria
   - Explicit out-of-scope declarations
   - User roles / personas differentiation

   Domain & Data Model:
   - Entities, attributes, relationships
   - Identity & uniqueness rules
   - Lifecycle/state transitions
   - Data volume / scale assumptions

   Interaction & UX Flow:
   - Critical user journeys / sequences
   - Error/empty/loading states
   - Accessibility or localization notes

   Non-Functional Quality Attributes:
   - Performance (latency, throughput targets)
   - Scalability (horizontal/vertical, limits)
   - Reliability & availability (uptime, recovery expectations)
   - Observability (logging, metrics, tracing signals)
   - Security & privacy (authN/Z, data protection, threat assumptions)
   - Compliance / regulatory constraints (if any)

   Integration & External Dependencies:
   - External services/APIs and failure modes
   - Data import/export formats
   - Protocol/versioning assumptions

   Edge Cases & Failure Handling:
   - Negative scenarios
   - Rate limiting / throttling
   - Conflict resolution (e.g., concurrent edits)

   Constraints & Tradeoffs:
   - Technical constraints (language, storage, hosting)
   - Explicit tradeoffs or rejected alternatives

   Terminology & Consistency:
   - Canonical glossary terms
   - Avoided synonyms / deprecated terms

   Completion Signals:
   - Acceptance criteria testability
   - Measurable Definition of Done style indicators

   Misc / Placeholders:
   - TODO markers / unresolved decisions
   - Ambiguous adjectives ("robust", "intuitive") lacking quantification

   For each category with Partial or Missing status, add a candidate question opportunity unless:
   - Clarification would not materially change implementation or validation strategy
   - Information is better deferred to planning phase (note internally)

3. From the coverage scan, compile a **complete list** of all detected ambiguities and missing decisions. Do NOT apply artificial count limits (no top-5, top-N caps). Classify each finding into one of two categories:

   **Category A — 의사결정 불필요 (No Decision Needed):**
   Issues with a single, objectively correct fix (e.g., remove stale placeholder, normalize terminology, add missing section mandated by constitution). These will be applied directly after user batch-approval.

   **Category B — 의사결정 필요/가능 (Decision Needed / Decision Possible):**
   Issues where multiple valid resolutions exist, or where a decision is not strictly required but the developer may benefit from choosing. Each gets structured options (see Step 4).

   **Dependency analysis for Category B items:**
   After classifying all D-\* items, perform a dependency check:
   - **Independent (독립)**: Answering this item does NOT change, invalidate, or create other D-\* items. These can be presented in one batch.
   - **Dependent (종속)**: Answering this item changes the options, relevance, or existence of one or more other D-\* items. These must wait until the predecessor is answered.

   Group D-\* items into **rounds**:
   - **Round 1**: All independent items + items that are predecessors (but not dependents of anything).
   - **Round 2+**: Items that depend on Round 1 answers. Re-evaluate and present after Round 1 answers are collected. Some items may become unnecessary or change options based on prior answers.
   - If ALL D-\* items are independent, present them in a single round.

   Apply these constraints per finding:
   - Only include findings whose answers materially impact architecture, data modeling, task decomposition, test design, UX behavior, operational readiness, or compliance validation.
   - Ensure category coverage balance: prioritize highest-impact unresolved categories first.
   - Exclude questions already answered, trivial stylistic preferences, or plan-level execution details (unless blocking correctness).
   - Favor clarifications that reduce downstream rework risk or prevent misaligned acceptance tests.

4. Batch presentation (present findings grouped by dependency, then collect answers per round):

   **First, output Category A (의사결정 불필요) as a table:**

   | ID   | Category    | Location    | Summary               | Proposed Fix     |
   | ---- | ----------- | ----------- | --------------------- | ---------------- |
   | N-01 | Terminology | spec.md:L30 | Inconsistent term "X" | Normalize to "Y" |

   (Stable IDs prefixed `N-`.)

   Then output: `N-* 수정사항을 일괄 적용할까요? (특정 ID 제외 가능)`

   **Then, output Category B (의사결정 필요/가능) grouped by round:**

   If all D-\* items are independent, present them all at once under a single heading.
   If dependency rounds exist, present only Round 1 items first with a note:
   `ℹ️ 아래 항목의 답변에 따라 추가 질문이 있을 수 있습니다 (Round 2).`

   For each finding, present exactly this structure:

   > **D-{id}** | {Taxonomy Category} | {Location}
   > **Question:** {clear, specific question}
   >
   > | Option                     | Description                              |
   > | -------------------------- | ---------------------------------------- |
   > | A                          | …                                        |
   > | B                          | …                                        |
   > | C                          | …                                        |
   > | (D/E as needed, 3–5 total) | …                                        |
   > | 서술형                     | 위 선택지에 해당하지 않는 경우 직접 작성 |
   >
   > **Recommended:** Option {X} — {1-2 sentence reasoning}

   (Stable IDs prefixed `D-`.)

   After all D-_ blocks in the current round, output:
   `각 D-_ 항목에 대해 옵션 문자(A/B/C/...) 또는 서술형 답변을 작성해주세요. (e.g., "D-01: B, D-02: A, D-03: 서술형—내 의견은...")`

   The user may answer:
   - All at once: `D-01: B, D-02: A, D-03: C`
   - Incrementally: answer a subset, then the rest later
   - Accept recommendations: `모두 추천대로` or `recommended`
   - Mix: `D-01: B, D-02: 추천, D-03: 서술형—XYZ`

   After receiving answers for the current round:
   - If ambiguous, ask for a quick disambiguation for that specific item only.
   - If dependent items exist (Round 2+), re-evaluate them based on collected answers:
     - Drop items that became irrelevant.
     - Update options for items whose choices changed.
     - Present the next round of D-\* items using the same format.
   - Repeat until all rounds are resolved or user signals completion.
   - Once all D-\* items across all rounds are resolved (or user signals "done"/"good"/"끝"), proceed to integration.
   - Respect user early termination signals ("stop", "done", "proceed", "끝", "다음").

5. Integration after collecting answers (batch or incremental):
   - Maintain in-memory representation of the spec (loaded once at start) plus the raw file contents.
   - For the first integration in this session:
     - Ensure a `## Clarifications` section exists (create it just after the highest-level contextual/overview section per the spec template if missing).
     - Under it, create (if not present) a `### Session YYYY-MM-DD` subheading for today.
   - For each N-\* (approved no-decision fix): apply the proposed fix directly.
   - For each D-\* (answered decision): append a bullet line: `- Q: <question> → A: <final answer>`.
   - Then apply each clarification to the most appropriate section(s):
     - Functional ambiguity → Update or add a bullet in Functional Requirements.
     - User interaction / actor distinction → Update User Stories or Actors subsection (if present) with clarified role, constraint, or scenario.
     - Data shape / entities → Update Data Model (add fields, types, relationships) preserving ordering; note added constraints succinctly.
     - Non-functional constraint → Add/modify measurable criteria in Non-Functional / Quality Attributes section (convert vague adjective to metric or explicit target).
     - Edge case / negative flow → Add a new bullet under Edge Cases / Error Handling (or create such subsection if template provides placeholder for it).
     - Terminology conflict → Normalize term across spec; retain original only if necessary by adding `(formerly referred to as "X")` once.
   - If the clarification invalidates an earlier ambiguous statement, replace that statement instead of duplicating; leave no obsolete contradictory text.
   - Save the spec file after integrating all answers to minimize risk of context loss (atomic overwrite).
   - If many answers were collected, apply them in a single batch write for efficiency.
   - Preserve formatting: do not reorder unrelated sections; keep heading hierarchy intact.
   - Keep each inserted clarification minimal and testable (avoid narrative drift).

6. Validation (performed after integration pass):
   - Clarifications session contains exactly one bullet per accepted D-\* answer (no duplicates).
   - All approved N-\* fixes have been applied.
   - Updated sections contain no lingering vague placeholders the new answer was meant to resolve.
   - No contradictory earlier statement remains (scan for now-invalid alternative choices removed).
   - Markdown structure valid; only allowed new headings: `## Clarifications`, `### Session YYYY-MM-DD`.
   - Terminology consistency: same canonical term used across all updated sections.

7. Write the updated spec back to `FEATURE_SPEC`.

8. Report completion (after all answers collected or early termination):
   - Number of N-_ fixes applied & D-_ questions answered.
   - Path to updated spec.
   - Sections touched (list names).
   - Coverage summary table listing each taxonomy category with Status: Resolved (was Partial/Missing and addressed), Deferred (user chose to skip or better suited for planning), Clear (already sufficient), Outstanding (still Partial/Missing but low impact).
   - If any Outstanding or Deferred remain, recommend whether to proceed to `/speckit.plan` or run `/speckit.clarify` again later post-plan.
   - Suggested next command.

Behavior rules:

- If no meaningful ambiguities found (or all potential questions would be low-impact), respond: "No critical ambiguities detected worth formal clarification." and suggest proceeding.
- If spec file missing, instruct user to run `/speckit.specify` first (do not create a new spec here).
- Never exceed the user's patience; if user signals early termination, stop and integrate what has been answered.
- If no questions asked due to full coverage, output a compact coverage summary (all categories Clear) then suggest advancing.
- If user terminates with unresolved high-impact categories remaining, explicitly flag them under Deferred with rationale.

Context for prioritization: $ARGUMENTS
