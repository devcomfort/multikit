---
description: "Propose README updates required by project changes using governance rules, with proposal-based approval workflow."
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Analyze project changes and propose the minimal README updates required to stay accurate.
Operate in proposal mode by default: propose first, apply only after explicit user approval.

---

## Philosophy: Proposal-First Documentation

README updates should be change-driven and reviewable.
The agent must separate **analysis**, **proposal**, and **execution** phases.

---

## Operating Constraints

- **Proposal-based**: Never modify files without explicit approval.
- **No Git mutation**: Do not commit/push unless the user explicitly asks.
- **Rule-bound**: Use `.github/readme-governance.md` as primary policy source.
- **Evidence-based**: Every suggestion must cite concrete project changes.
- **Minimality**: Suggest only necessary README edits.
- **Language**: Follow user language; default to Korean if unclear.
- **Response flow**: Always respond in 3 ordered blocks:
  1. code/project change explanation,
  2. README edit proposals,
  3. final concise change summary.
- **Concise != short**: Keep explanations plain and compact, but include enough detail for review.

---

## Execution Steps

### Phase 1) Gather Change Context

- Inspect current Git changes and changed files.
- Focus on project changes that can impact README accuracy:
  - kit/manifest/registry updates
  - CLI command or behavior changes
  - setup/install/run/test command changes
  - new or removed assets referenced by README

### Phase 2) Load Governance Rules

- Read `.github/readme-governance.md`.
- If missing, return `BLOCKED` with instruction to run `multikit.readme.governance` first.

### Phase 3) Determine README Impact

For each relevant project change, determine:

- impacted README section
- mismatch type (missing, outdated, inconsistent, ambiguous)
- expected value from source of truth

### Phase 4) Build Proposal Set

Create proposal units (atomic, independently reviewable):

- one proposal per logical README change
- include exact target section and minimal edit text
- include rationale and source evidence

### Phase 5) Present Proposal (No Edit Yet)

Output proposals in this format:

```markdown
## README Update Proposal

### 1) Code Change Overview

- Changed files: <list>
- What changed: <factual change summary>
- README impact areas: <sections likely affected>

### 2) Proposed README Edits

### Proposal 1/N: <short title>

- Section: <README section>
- Current: <summary>
- Expected: <value from source>
- Suggested edit: <minimal replacement/addition text>
- Evidence: <files>

### 3) Final Change Summary

- <what changed overall, concise but sufficiently informative>
```

Include final recommendation status:

- `NO_ACTION` (README already aligned)
- `PROPOSAL_READY` (changes recommended)
- `BLOCKED` (missing governance or required context)

### Phase 6) Await User Decision

- If user says `Apply` / `Proceed`: apply approved proposal items to `README.md`.
- If user says revise/split/drop: update proposal set and re-present.
- If user says cancel: stop without edits.

### Phase 7) Execution (Only After Approval)

When approved:

1. edit `README.md` for approved items only
2. show concise change summary
3. optionally propose commit message (do not auto-commit unless requested)

---

## Anti-patterns (Never Do)

- Suggest README edits without evidence from project changes
- Modify README immediately without proposal/approval
- Bundle unrelated README updates into one proposal item
- Ignore governance rules when they exist
