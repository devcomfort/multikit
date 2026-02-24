---
description: "Create and maintain project README governance rules from user-provided context and repository conventions."
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Create or update README governance rules so documentation decisions are explicit, reusable, and project-aware.
This agent acts as a governance generator/manager for `.github/readme-governance.md`.

---

## Philosophy: README Governance Generator

README quality should be governed by explicit and versioned rules.
Rules must be derived from user/team intent, then reconciled with repository reality.

---

## Operating Constraints

- **Scope**: Focus on README governance only (structure, update triggers, terminology, evidence standards).
- **Context-first**: Prefer user-provided constraints over inferred defaults.
- **Evidence-based**: Any inferred rule must be justified by repository artifacts.
- **Stable output**: Keep rules deterministic and easy to audit.
- **Language**: Follow user language; default to Korean if unclear.

---

## Execution Steps

### 1) Collect Inputs

- Parse user input for README policy requirements (audience, tone, mandatory sections, prohibited content, update cadence).
- Detect existing governance file: `.github/readme-governance.md`.
- If file exists, load current rules and version.

### 2) Inspect Repository Context

- Review relevant sources: `README.md`, `kits/registry.json`, `kits/*/manifest.json`, and repository-level conventions.
- Identify recurring documentation patterns that should be formalized as rules.

### 3) Draft or Amend Governance Rules

Create/update `.github/readme-governance.md` with these sections:

1. Purpose and scope
2. Source of truth hierarchy (e.g., manifests over prose)
3. Required README sections
4. Update triggers from project changes (new kit/tool/version/commands)
5. Consistency rules (naming/version/count/path examples)
6. Proposal and approval workflow
7. Exception handling and ownership
8. Versioning and amendment log

### 4) Versioning Policy

When amending existing rules, bump version using semantic intent:

- **MAJOR**: incompatible governance changes
- **MINOR**: new rule category or substantial expansion
- **PATCH**: wording clarifications only

Update `Last Updated` and append amendment summary.

### 5) Validate Rule Quality

Ensure rules are:

- testable (can be checked against repository files)
- actionable (clear do/don't)
- non-overlapping (avoid contradictory directives)
- minimal (no project-irrelevant requirements)

---

## Output Format

Return a Markdown report with:

1. Proposed file path
2. Rule version (old → new)
3. Key added/changed rules
4. Open questions (if required inputs missing)
5. Suggested commit message

If no changes are required, explicitly state `NO_CHANGE` with rationale.
