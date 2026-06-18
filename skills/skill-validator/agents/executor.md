# Executor (skval)

Run one eval, once, in one configuration. Dispatch this as a **fresh subagent** per
(eval × configuration × trial) so runs are independent.

## Inputs (in your prompt)
- `eval` — the prompt, input files, and expectations.
- `configuration` — `with_skill` or `without_skill`.
- `skill_dir` — only provided for `with_skill`; load and follow the skill.
- `run_dir` — where to save outputs, e.g. `workspace/runs/eval-<id>/<configuration>/run-<k>/`.

## Process
1. **Stage inputs.** If the eval declares `files`, copy them into `run_dir/inputs/` first
   (`scripts/eval_fixtures.py:stage(eval, workspace, run_dir)`) and work from there, so both
   configurations act on the **same** input. Skip if `files` is empty.
2. If `with_skill`, read the skill (`SKILL.md` + referenced resources) and follow it. If
   `without_skill`, do **not** read the skill — solve the task with your default ability.
   This baseline is what proves the skill's lift; keep it honest.
3. Perform the eval's task using the staged input files in `run_dir/inputs/`.
4. Save all deliverables to `run_dir/outputs/`.
5. Write `run_dir/outputs/metrics.json`: `{tool_calls, total_tool_calls, total_steps, files_created, errors_encountered, output_chars}`.
6. Write `run_dir/transcript.md` — a terse log of what you did (the grader reads this).
7. If anything was uncertain or you worked around a gap, note it in `run_dir/outputs/user_notes.md`.

## Rules
- Same prompt and same input files across both configurations — the **only** difference is
  whether the skill is present.
- Don't grade yourself; just produce the outputs and an honest transcript.
- Capture timing/tokens from the task-completion notification into `run_dir/timing.json`
  if the harness provides them.

## Multi-turn evals (`type: multi_turn`)
Some skills must **ask before acting**. For these, run a loop instead of one shot:
1. Seed the transcript with the eval `prompt` as the first user turn.
2. Produce the assistant turn (`with_skill`: follow the skill; `without_skill`: default ability).
3. If the assistant **asked a question** (didn't deliver), get the next user turn from the
   **user-simulator** ([user-simulator.md](user-simulator.md)) using the eval's `user_simulator`
   persona/goal/answers, append it, and repeat — up to `max_turns`.
4. Stop when the assistant delivers the final result, the simulator returns `[[DONE]]`, or
   `max_turns` is hit.

Save the exchange to `run_dir/transcript.json` (a list of `{role, content}`) and record the
delivery turn index. The grader scores interaction expectations from this with
`scripts/conversation.py` (e.g. `questions_before_delivery`, `asked_about`).

## Headless fallback
Without subagents, run each configuration with `claude -p` instead. Inject the skill by
**stripping its `---` frontmatter** and prefixing plain text — never start a `claude -p`
prompt with `-`/`---`, which the CLI parses as a flag (it errors and returns nothing).
