# gitkit.commit Prompt

Analyze the current git changes and suggest well-structured commits
following the Conventional Commits specification.

## Rules

- Group related changes into logical commits
- Use the format: `<type>(<scope>): <description>`
- Keep subject line under 72 characters
- Add body for complex changes explaining WHY, not WHAT
- Reference issues when applicable (e.g., `Closes #123`)

## Example Output

```
feat(auth): add OAuth2 login support

Implement Google and GitHub OAuth2 providers using the
passport.js library. This replaces the legacy session-based
authentication.

Closes #42
```
