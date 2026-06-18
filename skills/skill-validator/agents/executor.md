# Executor (skval)

Run one eval, once, in one configuration. Dispatch this as a **fresh subagent** per
(eval × configuration × trial) so runs are independent.

## Inputs (in your prompt)
- `eval` — the prompt, input files, and expectations.
- `configuration` — `with_skill` or `without_skill`.
- `skill_dir` — only provided for `with_skill`; load and follow the skill.
- `run_dir` — where to save outputs, e.g. `workspace/runs/eval-<id>/<configuration>/run-<k>/`.

## Process
1. If `with_skill`, read the skill (`SKILL.md` + referenced resources) and follow it. If
   `without_skill`, do **not** read the skill — solve the task with your default ability.
   This baseline is what proves the skill's lift; keep it honest.
2. Perform the eval's task using the provided input files.
3. Save all deliverables to `run_dir/outputs/`.
4. Write `run_dir/outputs/metrics.json`: `{tool_calls, total_tool_calls, total_steps, files_created, errors_encountered, output_chars}`.
5. Write `run_dir/transcript.md` — a terse log of what you did (the grader reads this).
6. If anything was uncertain or you worked around a gap, note it in `run_dir/outputs/user_notes.md`.

## Rules
- Same prompt and same input files across both configurations — the **only** difference is
  whether the skill is present.
- Don't grade yourself; just produce the outputs and an honest transcript.
- Capture timing/tokens from the task-completion notification into `run_dir/timing.json`
  if the harness provides them.

## Headless fallback
Without subagents, run each configuration with `claude -p` instead. Inject the skill by
**stripping its `---` frontmatter** and prefixing plain text — never start a `claude -p`
prompt with `-`/`---`, which the CLI parses as a flag (it errors and returns nothing).
