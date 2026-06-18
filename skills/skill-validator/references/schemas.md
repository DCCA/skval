# skval JSON Schemas

## `scorecard.json`

The machine-readable result of a validation run.

```json
{
  "score": 78,
  "grade": "C",
  "verdict": "Revise",
  "safety_pass": true,
  "dimensions": {
    "D1": {
      "score": 0.75,
      "weight": 0.15,
      "checks": [
        {"id": "name_kebab_case", "passed": true, "severity": "major", "detail": ""}
      ]
    },
    "D2": {"score": 0.84, "weight": 0.30, "pass_rate": {"mean": 0.86, "stddev": 0.04, "std_error": 0.02, "n": 5},
           "baseline_lift": "+0.45", "significant": true}
  },
  "safety": {"safety_pass": true, "findings": []},
  "findings": [
    {"dimension": "D1", "impact_estimate": 2, "message": "name 'Bad_Name' must be kebab-case"}
  ],
  "provenance": {"source": "./my-skill", "kind": "dir", "resolved_path": "/abs/path"},
  "metadata": {
    "mode": "structural-only",
    "skipped_dimensions": ["D2", "D3", "D4", "D5"],
    "skill_name": "my-skill",
    "executor_model": "",
    "judge_model": "",
    "trials": 5,
    "timestamp": "2026-06-18T00:00:00Z"
  }
}
```

**Fields**
- `score` — composite 0–100 (`scoring.composite`).
- `grade` / `verdict` — `scoring.grade` / `scoring.verdict`.
- `safety_pass` — D6 gate; `false` ⇒ score 0, grade F, verdict Reject.
- `dimensions[D*]` — per-dimension `score` (0–1) and `weight`. D1 carries its raw `checks`;
  behavioral dims (M1+) carry `pass_rate` summary (`stats.summarize`), `baseline_lift`, and a
  `significant` flag (delta vs. standard error of the difference).
- `findings[]` — ranked `{dimension, impact_estimate, message}` (highest impact first).
- `metadata.mode` — `"structural-only"` (M0, deterministic) or `"full"` (M1+).
- `metadata.skipped_dimensions` — dimensions not measured in this run.

## `benchmark.json` (M2)

For per-run behavioral detail, skval emits a file compatible with the
`skill-creator` `eval-viewer` (see that project's `references/schemas.md`):
`runs[]` with `configuration` ∈ {`with_skill`, `without_skill`}, nested `result`
(pass_rate, time_seconds, tokens), and `run_summary` with mean/stddev per config
plus a `delta`. skval extends each config summary with `pass_hat_k` and
`std_error` from `stats.py`.
