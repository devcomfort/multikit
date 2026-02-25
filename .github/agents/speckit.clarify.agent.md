---
description: Identify ALL underspecified areas in the current feature spec, classify them as no-decision-needed vs decision-needed (with structured options + free-form), and encode answers back into the spec.
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

   **Category A — No Decision Needed:**
   Issues with a single, objectively correct fix (e.g., remove stale placeholder, normalize terminology, add missing section mandated by constitution). These will be applied directly after user batch-approval.

   **Category B — Decision Needed / Decision Possible:**
   Issues where multiple valid resolutions exist, or where a decision is not strictly required but the developer may benefit from choosing. Each gets structured options (see Step 4).

   **Dependency analysis for Category B items:**
   After classifying all D-\* items, perform a dependency check:
   - **Independent**: Answering this item does NOT change, invalidate, or create other D-\* items. These can be presented in one batch.
   - **Dependent**: Answering this item changes the options, relevance, or existence of one or more other D-\* items. These must wait until the predecessor is answered.

   Group D-\* items into **rounds**:
   - **Round 1**: All independent items + items that are predecessors (but not dependents of anything).
   - **Round 2+**: Items that depend on Round 1 answers. Re-evaluate and present after Round 1 answers are collected. Some items may become unnecessary or change options based on prior answers.
   - If ALL D-\* items are independent, present them in a single round.

   Apply these constraints per finding:
   - Only include findings whose answers materially impact architecture, data modeling, task decomposition, test design, UX behavior, operational readiness, or compliance validation.
   - Ensure category coverage balance: prioritize highest-impact unresolved categories first.
   - Exclude questions already answered, trivial stylistic preferences, or plan-level execution details (unless blocking correctness).
   - Favor clarifications that reduce downstream rework risk or prevent misaligned acceptance tests.

4. Findings presentation (mode-aware):

   #### Presentation Mode

   The agent supports two output modes:
   - **Batch Mode** (default): Present all findings at once as described below.
   - **Sequential Mode**: Present one finding at a time, collecting user response before proceeding. Activated when user explicitly requests (e.g., "하나씩 보여줘", "one at a time", "하나씩 처리하자").

   **Mode switching:** User can switch at any time ("나머지 전부 보여줘" → Batch, "하나씩 보자" → Sequential). Acknowledge the switch briefly and continue with remaining items in the new mode.

   **Sequential Mode rules:**
   - N-\* items first, one at a time, asking approval per item.
   - D-\* items next: independent items first, then dependent items after predecessors resolve.
   - Dependency clusters that must be decided simultaneously are presented as one unit with explanation.
   - Between items, briefly state remaining count (e.g., "N-02 완료. 남은 항목: D-01~D-03").

   **Batch Mode presentation (default):**

   **First, output Category A (No Decision Needed) as a table:**

   | ID   | Category    | Location    | Summary               | Proposed Fix     |
   | ---- | ----------- | ----------- | --------------------- | ---------------- |
   | N-01 | Terminology | spec.md:L30 | Inconsistent term "X" | Normalize to "Y" |

   (Stable IDs prefixed `N-`.)

   **Visual Concreteness Principle (mandatory):** After the summary table, present each proposed fix so the user can evaluate it **purely by reading the presented text**—without mentally composing what the result would look like. Choose the most effective format per item:
   - **Fenced code block** (` ```markdown `): Multi-line insertions/replacements, new sections, or structural changes.
   - **Inline diff** (` `old`→`new` `): Single-term renames, short phrase replacements, or value swaps.
   - **Bullet summary with quoted excerpt**: Minor additions to an existing list or table row.

   The agent selects the format that maximizes readability for the specific change size and type. The invariant is: **the user sees the exact final text**, not an abstract description of it. For D-\* items, show the concrete spec text for the **recommended option**; if the user selects a different option, regenerate the snippet for confirmation before applying.

   Then output: `Batch-apply all N-* fixes? (You may exclude specific IDs.)`

   **Then, output Category B (Decision Needed) grouped by round:**

   `Question` writing rules (mandatory):
   - Questions must not be simple selection requests; they must enable the user to deductively understand the root cause of the problem.
   - Always follow this structure: **evidence (observed fact) → interpretation (problem) → impact (risk/consequence) → decision axis (what needs to be decided)**.
   - Cite all relevant source references (artifact/section) exhaustively, and describe the concrete impact their combination has on implementation or validation.
   - Do not use abstract terms like "ambiguity" or "conflict" in isolation; specify what is affected and why it impacts implementation or validation.

   **Interpretability principle**: A user reading the Question must understand "why a decision is needed" and "what criteria to use when comparing options" without re-checking the original artifacts. The standard is completeness of causal reasoning, not the number of cited references.

   **Self-contained references (mandatory)**: Every cross-reference ID (FR-015, SC-008, T035, US6, etc.) MUST include a brief inline description on first mention in each section so the reader never needs to open another file to understand the reference. Format: `ID(short description)` — e.g., `US6(설치된 킷 업데이트)`, `FR-015(update --force/--registry)`, `SC-008(재시도 백오프 검증)`, `T035(update retry/backoff 테스트)`. Subsequent mentions in the same section may use the bare ID.

   If all D-\* items are independent, present them all at once under a single heading.
   If dependency rounds exist, present only Round 1 items first with a note:
   `ℹ️ Additional questions may follow depending on your answers below (Round 2).`

   For each finding, present exactly this structure:

   > **D-{id}** | {Taxonomy Category} | {Location}
   > **Question:** {clear, specific question}
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

   (Stable IDs prefixed `D-`.)

   After all D-\_ blocks in the current round, output:
   `For each D-* item, provide an option letter (A/B/C/…) or a free-form answer. (e.g., "D-01: B, D-02: A, D-03: free-form—my reasoning is…")`

   The user may answer:
   - All at once: `D-01: B, D-02: A, D-03: C`
   - Incrementally: answer a subset, then the rest later
   - Accept recommendations: `all recommended` or `recommended`
   - Mix: `D-01: B, D-02: recommended, D-03: free-form—XYZ`

   After receiving answers for the current round:
   - If ambiguous, ask for a quick disambiguation for that specific item only.
   - If dependent items exist (Round 2+), re-evaluate them based on collected answers:
     - Drop items that became irrelevant.
     - Update options for items whose choices changed.
     - Present the next round of D-\* items using the same format.
   - Repeat until all rounds are resolved or user signals completion.
   - Once all D-\* items across all rounds are resolved (or user signals "done"/"good"), proceed to integration.
   - Respect user early termination signals ("stop", "done", "proceed", "next").

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

- **Response Language**: If the user explicitly requests a language, use that language for all output. Otherwise, infer the user's preferred language from recent conversation messages (e.g., if the user writes in Korean, respond in Korean). Technical identifiers (IDs, file paths, code snippets) remain in their original form regardless of response language.
- If no meaningful ambiguities found (or all potential questions would be low-impact), respond: "No critical ambiguities detected worth formal clarification." and suggest proceeding.
- If spec file missing, instruct user to run `/speckit.specify` first (do not create a new spec here).
- Never exceed the user's patience; if user signals early termination, stop and integrate what has been answered.
- If no questions asked due to full coverage, output a compact coverage summary (all categories Clear) then suggest advancing.
- If user terminates with unresolved high-impact categories remaining, explicitly flag them under Deferred with rationale.

Context for prioritization: $ARGUMENTS
