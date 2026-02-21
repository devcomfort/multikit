---
description: "Analyze Git changes, group them into logical commit units, and propose Conventional Commits. Execute commits only after user review."
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Analyze changes in the Git working directory, group them into **logically separated commit units**, and propose a **Conventional Commits** message for each group.

> **This agent is proposal-based.**
> It does not auto-commit. It first produces proposals.
> After user review and feedback, it revises or executes as instructed.

---

## Operating Constraints

- **Language**: Follow the user's language. If unclear, respond in English.
- **NO AUTO-COMMIT**: Never run `git commit` without explicit user approval.
- **NO FORCE PUSH**: Never use `git push --force`.
- **Atomic Commits**: Each commit must represent one logical unit of change.
- **Convention**: Follow Conventional Commits 1.0.0.

---

## Conventional Commits Reference

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type Reference

| Type       | When to Use                                | Example                                           |
| ---------- | ------------------------------------------ | ------------------------------------------------- |
| `feat`     | Add a new feature                          | `feat: add parallel download retry logic`         |
| `fix`      | Fix a bug                                  | `fix: handle timeout in download_file`            |
| `docs`     | Documentation-only changes                 | `docs: update API usage examples`                 |
| `style`    | Formatting only (no behavior change)       | `style: apply ruff formatting`                    |
| `refactor` | Code restructuring without behavior change | `refactor: extract filename validation to helper` |
| `test`     | Add or update tests                        | `test: add coverage for error paths`              |
| `chore`    | Build/config/tooling changes               | `chore: update pytest configuration`              |
| `ci`       | CI changes                                 | `ci: add multi-version Python matrix`             |
| `perf`     | Performance improvements                   | `perf: use streaming for large file downloads`    |

### Scope

Optional, but useful when clarifying change boundaries:

- `feat(downloader)`
- `test(coverage)`
- `docs(agents)`

### Breaking Changes

For backward-incompatible changes:

- Add `!` after type/scope: `feat!: change download API signature`
- Include `BREAKING CHANGE:` in footer

---

## Execution Steps

### Phase 1: Analyze Changes

1. Run `git status` and `git diff` to collect all changes.
2. For each changed file, identify:
   - **Which file** changed
   - **What** changed (add/modify/delete)
   - **Why** it changed (intent/purpose)
   - **Relationship to other changes**

### Phase 2: Group into Logical Units

Group changes into logical commit units using these criteria:

| Criterion          | Description                            | Example                        |
| ------------------ | -------------------------------------- | ------------------------------ |
| **Shared purpose** | Same feature/fix intent                | source + related tests         |
| **Module scope**   | Related changes in same module/package | files under `errors/`          |
| **Dependency**     | B is meaningless without A             | pragma comment + coverage test |
| **Infra/config**   | Build/CI/config changes                | `pyproject.toml`, `.github/`   |

### Phase 3: Determine Commit Order

Resolve dependencies between groups and order commits correctly:

1. **Infra/config changes**
2. **Source changes** (feature/refactor)
3. **Test changes**
4. **Documentation updates**

### Phase 4: Compose Commit Messages

Create a Conventional Commit message for each group.

#### Message Quality Checklist

- [ ] Does **Type** match the nature of the change?
- [ ] Does **Scope** clarify the affected area? (optional)
- [ ] Is **Description** concise (preferably ≤ 50 chars)?
- [ ] Does **Body** explain WHY for complex changes?
- [ ] For English descriptions: lowercase start, no trailing period, imperative mood?
- [ ] Is any breaking change clearly marked?

### Phase 5: Present Proposal

Output commit proposals in this format:

```markdown
## Commit Proposal

### Commit 1/N: `<type>[scope]: <description>`

**Files:**

- `path/to/file1.py` — (summary)
- `path/to/file2.py` — (summary)

**Message:**
```

<type>[scope]: <description>

<optional body explaining WHY>
```

**Rationale:** Why these changes belong in one commit

---

### Commit 2/N: ...

```

### Phase 6: Await User Review

Wait for user response after proposal:

| User Response | Agent Action |
|---------------|-------------|
| "Looks good" / "LGTM" / "Proceed" | Execute `git add` + `git commit` in proposed order |
| "Revise message for commit N" | Update only that commit message and re-propose |
| "Merge commits N and M" | Merge those groups and re-propose |
| "Split commit N" | Further split that group and re-propose |
| "Drop commit N" | Exclude that group from proposal |
| Other feedback | Incorporate feedback and re-propose |

### Phase 7: Execute Commits

After explicit approval:

1. Stage files per commit group using `git add`
2. Run `git commit` with approved messages
3. Report results using `git log --oneline -N`

---

## Anti-patterns (Never Do)

| Anti-pattern | Why |
|-------------|-----|
| Put all changes in one commit | Hard to review/revert/understand |
| `git add .` then immediate commit | Can include unrelated changes |
| Messages like "update files" | Low information, poor history quality |
| Commit without user confirmation | Violates proposal-based workflow |
| Force push | Risk of destructive history rewrite |
```
