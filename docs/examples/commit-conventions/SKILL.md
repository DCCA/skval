---
name: commit-conventions
description: Use when writing a git commit message, to produce a properly formatted Conventional Commits message for staged changes.
---

# Commit Conventions

Write commit messages in Conventional Commits format: `type(scope): summary`.

- type is one of: feat, fix, docs, refactor, test, chore, perf, build, ci.
- summary: short, imperative, lowercase, no trailing period.

## Example
Input: added a JWT login endpoint to the auth service
Output: `feat(auth): add jwt login endpoint`

Output ONLY the commit message line, nothing else.
