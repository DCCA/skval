# Eval Generator (skval)

Produce the evals and triggering queries a validation run needs. **Hybrid:** prefer
the skill's own evals; only synthesize when they're missing.

## Inputs
- `skill_dir` — the canonical skill directory.
- `workspace` — where to write outputs.

## Process

1. **Check for bundled evals.** If `skill_dir/evals/evals.json` exists, copy it to
   `workspace/evals.json` unchanged and skip to step 4. (Schema below.)
2. **Read the skill** (`SKILL.md` + referenced files) to understand what it claims to do,
   when it should trigger, and what a correct output looks like.
3. **Synthesize 3–5 task evals.** Each must be a realistic, concrete task a real user
   would give (specific file names, values, context — not "do the thing"). For each,
   write **discriminating expectations**: assertions that *fail* for a wrong or
   superficial output (check content/correctness, not just that a file exists). A good
   expectation passes only when the skill genuinely did the work.
   - **Create input fixtures when the task needs one.** File-transform skills (pdf, xlsx,
     docx, …) only show their effect on a real input. Write a small, realistic fixture to
     `workspace/fixtures/eval-<id>/` — for binary formats, write and run a short script to
     generate it — and list its workspace-relative path in the eval's `files`. Every path
     in `files` must exist (verify with `scripts/eval_fixtures.py check <workspace>`).
   - **Interactive skills get multi-turn evals.** If the skill is meant to *ask before acting*
     (booking, ordering, gathering requirements, triage), set `"type": "multi_turn"`, give a
     `user_simulator` (persona, goal, and `answers` to reveal only when asked) and a
     `max_turns`, and write **interaction expectations a one-shot answer would fail** — e.g.
     "asks at least 2 clarifying questions before delivering", "asks about budget before ordering".
4. **Generate the triggering query set** for D5: 8–10 **should-trigger** queries (varied
   phrasings, some not naming the skill explicitly) and 8–10 **should-not-trigger**
   near-misses (share keywords but need something else). Write to
   `workspace/triggering_queries.json`.
5. **Review gate (ON by default).** Present the generated evals and triggering queries to
   the user for edit/approval before any runs. Skip only if the caller passed a
   hands-free flag. Bad evals produce bad scores — this step matters.

## Output schemas

Write **only raw JSON** to each file below — no Markdown ` ``` ` fences and no surrounding prose.

`workspace/evals.json`:
```json
{
  "skill_name": "the-skill",
  "evals": [
    {"id": 0, "prompt": "concrete task...", "expected_output": "what success looks like",
     "files": ["fixtures/eval-0/input.xlsx"], "expectations": ["Output includes X computed from the input"]}
  ]
}
```
`files` lists **workspace-relative fixture paths** to stage into each run (use `[]` when the
task needs no input file).

A **multi-turn** eval (for skills that must ask before acting) adds `type`, `user_simulator`,
and `max_turns`:
```json
{"id": 1, "type": "multi_turn", "max_turns": 6,
 "prompt": "I'd like to order dinner for tonight.",
 "user_simulator": {"persona": "busy parent, two kids", "goal": "a family meal under $40",
                    "answers": {"diet": "one vegetarian", "budget": "$40", "address": "12 Oak St"}},
 "expected_output": "a confirmed order summary within budget",
 "files": [],
 "expectations": ["Asks at least 2 clarifying questions before placing the order",
                  "Asks about dietary needs before choosing items",
                  "Final order total is within the stated budget"]}
```

`workspace/triggering_queries.json`:
```json
[
  {"query": "realistic user request...", "should_trigger": true},
  {"query": "near-miss that needs a different tool...", "should_trigger": false}
]
```
