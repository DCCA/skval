# Triggering Tester (skval) — D5

Measure whether the skill activates at the right times: high recall on should-trigger
queries, high precision against near-miss should-not-trigger queries.

## Inputs
- `skill_dir` — for the skill's `name` + `description` (the triggering surface).
- `workspace/triggering_queries.json` — labeled queries from the eval generator.

## Method
The `description` is what an agent sees when deciding whether to consult a skill, so test
against it. For each query, simulate the decision with `claude -p`:

```bash
claude -p "You are deciding whether to consult a skill for a user request.
Available skill —
  name: <name>
  description: <description>
User request: \"<query>\"
Would you consult this skill? Answer exactly YES or NO." --model <session-model>
```

- Run each query **3 times**; take the majority answer (reduces nondeterminism).
- Use the **model id powering this session** so the test matches real behavior.
- Classify against the label: should_trigger=true & YES → TP; true & NO → FN;
  false & YES → FP; false & NO → TN.

## Output — `workspace/triggering.json`
```json
{
  "tp": 8, "fp": 1, "fn": 2, "tn": 9,
  "precision": 0.889, "recall": 0.800, "f1": 0.842,
  "per_query": [{"query": "...", "should_trigger": true, "fired": true}]
}
```
`dimensions.d5_triggering` uses `f1` (or computes it from tp/fp/fn). If `claude -p` is
unavailable, skip D5 — the scorer renormalizes over the remaining dimensions and the
scorecard notes D5 as skipped.
