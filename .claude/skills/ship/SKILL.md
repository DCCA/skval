---
name: ship
description: Ship the current branch end-to-end — create a PR to main, review the diff, wait for GitHub Actions to pass, merge, and confirm the deploy. Use when the user says "ship it", "ship this", "create a PR and merge", "release this", or wants the full PR→CI→merge→deploy loop in one step.
---

# /ship — create PR → review → verify CI → merge → confirm deploy

Run the full release loop for the **current branch** of this repo (`DCCA/skval`).
Use the GitHub MCP tools (`mcp__github__*`); load them with ToolSearch if they are
not already available. Never use `sleep` loops to wait on CI — check status, and if
it is still running, check again.

## Steps

1. **Pre-flight.**
   - `git status` — commit anything outstanding with a clear message (identity
     `Claude <noreply@anthropic.com>`).
   - Run the gate: `uv run pytest` **and** the skill self-validation
     (`validate_structural.py skills/skill-validator` → must be **100 / A**).
   - `git push -u origin <current-branch>` (retry on network errors).
2. **Open the PR.** `create_pull_request` with base `main`, head = current branch,
   and a title + body describing the change.
3. **Review the diff.** `pull_request_read method=get_diff` — confirm it contains
   only the intended changes and post a short review (flag anything surprising).
4. **Verify CI.** Poll `actions_list` / `actions_get` for the PR's check runs until
   they complete. If a check fails: fetch logs (`get_job_logs`), diagnose, fix,
   push, and re-check. Repeat until green.
5. **Merge.** Once all checks pass, `merge_pull_request` (merge commit titled
   `Merge PR #<n>: <title>`).
6. **Confirm deploy.** If the change touched `docs/`, the Pages workflow
   (`pages.yml`) redeploys on push to `main` — verify that run concludes
   `success` via `actions_get`, then report the live status
   (<https://dcca.github.io/skval/>).

## When to stop and ask

Pause and use `AskUserQuestion` only if: the diff is ambiguous or larger than
expected, CI fails for a reason that needs a product decision, or the merge would
do something the user wouldn't expect. Otherwise drive the loop to a merged,
deployed state and report the result.
