# Example: a live `skval` full-validation run

> 📂 **Want to browse the actual eval set and every per-trial result?** They're committed
> at [`commit-conventions/`](commit-conventions/) — `evals/evals.json`, the full `runs/`
> tree, judgments, and the scorecard.

A real `skval` **full** (M1) validation of a small example skill,
`commit-conventions`, produced by actually running the behavioral pipeline via
`claude -p` — N=3 trials × 2 evals, with-skill vs no-skill — plus an LLM artifact
judge and a triggering test. (Scaled from the production default of N=5 for a quick
run; bundled `evals/evals.json` exercised the hybrid eval path.)

```
# Skill Scorecard — `commit-conventions`
Source: docs/examples/commit-conventions · mode: full

## █████████████░  95 / 100   Grade: A   Verdict: Ship

| Dimension | Score | Weight | Detail |
|-----------|-------|--------|--------|
| D1 Structural | 1.00 | 0.15 | all checks pass |
| D2 Effectiveness | 1.00 | 0.30 | pass 100% ± 0%, lift +33% (significant) |
| D3 Reliability | 1.00 | 0.20 | pass^1=1.00  pass^3=1.00 |
| D4 Artifact quality | 0.75 | 0.20 | 6/8 rubric criteria |
| D5 Triggering | 1.00 | 0.15 | F1 1.00, P 1.00, R 1.00 |

Safety gate: PASS

No findings — clean.
```

## What this demonstrates
- **The full pipeline runs end-to-end on real model calls** — hybrid (bundled) evals →
  with/no-skill executors → grading → artifact judge → triggering → aggregate → score.
- **D2 lift (+33%) is genuine and significant:** the no-skill baseline produced two
  empty/low-quality outputs across its six runs; the skill eliminated them. The lift
  cleared the standard error of the difference, so it is flagged significant.
- **D4 = 0.75:** the LLM artifact judge passed 6 of 8 binary rubric criteria.
- **Dogfooding caught a real bug:** `claude -p` rejects any prompt beginning with `-`
  (so an injected `---` frontmatter silently failed). The fix is captured in
  `agents/executor.md` and `agents/triggering.md`.
