````chatagent
---
description: "Version update execution — apply recommended version bumps to all declared version locations with approval workflow."
handoffs:
  - label: Re-analyze version impact
    agent: cikit.analyze.versioning
    prompt: Re-analyze version impact before applying updates.
  - label: Update governance
    agent: cikit.governance.versioning
    prompt: Update the versioning governance rules.
  - label: Check README impact
    agent: dockit.analyze.readme
    prompt: Analyze if README needs updates after version bump.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Apply a version bump to **all declared version locations** in the project,
ensuring consistency across all files.

**Apply changes only after explicit user approval.**

---

## Philosophy: Atomic Version Consistency

A version bump is not a single-file edit. It's a coordinated update across every file
that declares a version. Missing even one location creates drift and confusion.

---

## Operating Constraints

- **Proposal-based**: Never modify files without explicit user approval.
- **No Git mutation**: Do not commit/push unless the user explicitly asks.
- **Governance-aware**: Use `.github/versioning-governance.md` for version locations and sync policy.
- **Language**: Follow user language; default to Korean if unclear.

---

## Execution Steps

### 1) Load Context

- Read `.github/versioning-governance.md` for version locations and bump rules.
- Read version impact analysis from `/cikit.analyze.versioning` output (if in conversation context).
- If no prior analysis exists, recommend running `/cikit.analyze.versioning` first.

### 2) Determine Target Version

From the version impact analysis or user input:

- **Current version**: {read from primary source}
- **Bump level**: MAJOR / MINOR / PATCH (from analysis or user-specified)
- **New version**: {calculated}

If user specifies an exact version, use that instead of calculating.

### 3) Locate All Version Files

From governance (or auto-detect):

| File                     | Field/Location          | Current Value |
| ------------------------ | ----------------------- | ------------- |
| `pyproject.toml`         | `[project].version`     | {value}       |
| `package.json`           | `version`               | {value}       |
| `kits/*/manifest.json`   | `version`               | {value}       |
| `multikit.toml`          | `[multikit].version`    | {value}       |
| `CHANGELOG.md`           | Latest entry header     | {value}       |
| `README.md`              | Badge / version mention | {value}       |
| ... (per governance)     |                         |               |

### 4) Build Update Proposal

For each version location, propose the exact edit:

```markdown
### Proposal {n}/{total}: {file path}

- **File**: {path}
- **Field**: {field name or location}
- **Current**: {old version}
- **Proposed**: {new version}
- **Edit**: {exact text replacement}
```

### 5) Present Proposal

Output in 3 ordered blocks:

1. **Version Bump Summary** — What's changing and why
2. **File Update Proposals** — Each file to be updated
3. **Consistency Check** — Confirmation all locations are covered

Status:

- `PROPOSAL_READY` — Updates recommended, awaiting approval
- `ALREADY_CURRENT` — All locations already at target version
- `BLOCKED` — Missing governance or conflicting version information

### 6) Await User Decision

- **"Apply"**: Update all version locations.
- **"Apply except N"**: Skip specific files.
- **Custom version**: Override the calculated version.
- **"Cancel"**: Stop without edits.

### 7) Execute (Only After Approval)

When approved:

1. Update each version location atomically.
2. Verify all locations now show the new version.
3. Show summary of all changes.
4. If `CHANGELOG.md` exists, offer to add a new entry (or remind user to do so).
5. Propose commit message: `chore: bump version {old} → {new}`.

### 8) Post-Update Suggestions

After version bump, suggest:

- Check if README needs updates: `/dockit.analyze.readme`
- Check if documentation needs updates: `/dockit.analyze.project_docs`
- Tag the release: `git tag v{new_version}`

---

## Anti-Patterns (Do Not)

| # | Anti-Pattern                                       | Why                                          |
|---|----------------------------------------------------|----------------------------------------------|
| 1 | Bump without knowing the current version           | Must read before writing                     |
| 2 | Update only one file when multiple declare version | Version drift is worse than no versioning    |
| 3 | Auto-commit without user approval                  | Commits are irreversible in shared repos     |
| 4 | Skip changelog update                              | At minimum, remind the user                  |
| 5 | Guess the bump level without analysis              | Use governance rules or `/cikit.analyze.versioning` |

````
