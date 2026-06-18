# Example run — `commit-conventions`

A complete, real `skval` **full** validation you can browse end-to-end. The skill
([`SKILL.md`](SKILL.md)) teaches Conventional Commits; it was validated with **N=3
trials over 2 evals, with and without the skill**.

**Result: 95 / 100 · A · Ship** — [`workspace/scorecard.md`](workspace/scorecard.md).

## What to open
| File | What it is |
|---|---|
| [`evals/evals.json`](evals/evals.json) | **The eval set** — the tasks + their pass/fail expectations |
| [`workspace/scorecard.md`](workspace/scorecard.md) | The headline scorecard (human-readable) |
| [`workspace/scorecard.json`](workspace/scorecard.json) | Same, machine-readable (full per-dimension detail) |
| [`workspace/runs/`](workspace/runs) | **Per-trial evidence** — `eval-<id>/<with_skill \| without_skill>/run-<k>/` with `grading.json` + the model's `outputs/` |
| [`workspace/artifact_judgment.json`](workspace/artifact_judgment.json) | D4 — the artifact rubric (8 criteria) |
| [`workspace/triggering.json`](workspace/triggering.json) | D5 — every test query and whether it fired |
| [`workspace/benchmark.json`](workspace/benchmark.json) | Ready to open in skill-creator's eval-viewer |

## See the lift for yourself
Open one with-skill output next to a without-skill output for the same eval:

- [`workspace/runs/eval-0/with_skill/run-1/outputs/commit.txt`](workspace/runs/eval-0/with_skill/run-1/outputs/commit.txt)
- [`workspace/runs/eval-0/without_skill/run-2/outputs/commit.txt`](workspace/runs/eval-0/without_skill/run-2/outputs/commit.txt)

Comparing the two configurations, trial by trial, is exactly what produces the
**+33% effectiveness lift** reported in the scorecard.

## Reproduce
```bash
uv run python skills/skill-validator/scripts/validate_full.py \
    docs/examples/commit-conventions docs/examples/commit-conventions/workspace
```
