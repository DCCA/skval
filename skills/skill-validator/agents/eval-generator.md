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
     "files": [], "expectations": ["Output includes X computed from the input", "Used script Y"]}
  ]
}
```

`workspace/triggering_queries.json`:
```json
[
  {"query": "realistic user request...", "should_trigger": true},
  {"query": "near-miss that needs a different tool...", "should_trigger": false}
]
```
