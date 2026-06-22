# skval pre-run cost estimate — design

**Date:** 2026-06-22 · **Status:** approved, implementing

## Problem

Enterprise users pay by tokens and want to know what a **full** skval run
(`skval full`, the model-driven D2–D5 path) will cost **before** they kick it off.
Today only the deterministic structural scan is free and instant; the behavioral
stage spawns dozens of subagents (~1M tokens for a default run) with no upfront
projection.

## Decisions (from brainstorming)

- **Estimate only** — decision support, no enforcement / gate / cap.
- **Tokens + $** — report projected input/output tokens *and* a dollar figure.
- **Surface:** a deterministic `skval estimate` CLI subcommand **and** a SKILL.md
  step (one shared estimator module powers both). No model calls.
- **Method:** heuristic **low / expected / high** range from per-stage token
  assumptions × the run plan, anchored to observed run data.

## Architecture

Three new pure-Python pieces under `skills/skill-validator/scripts/`, no
network/model calls (consistent with the `structural` path):

| File | Responsibility |
|---|---|
| `pricing.py` | Per-model `{model_id: (input_$/MTok, output_$/MTok)}` table, sourced from the `claude-api` reference. `rate(model)` lookup; unknown model → `ValueError`. Isolated so price drift is a one-file edit. |
| `cost_estimate.py` | The estimator. `measure_skill_tokens(dir)`, `build_plan(...)`, `estimate(skill_dir, plan, prices)` → structured per-stage + total token/$ ranges, and `render_markdown(est)`. No I/O beyond reading the skill files. |
| `skval_cli.py` (edit) | New `estimate` subcommand: resolve source → build plan from flags/defaults → render markdown to stdout, optionally write `estimate.json`. |

Data flow: `source → resolve_skill → measure_skill_tokens → estimate(plan, pricing.rate) → markdown / JSON`.

## Cost model

Token-consuming stages of a full run (resolve / structural / safety / assemble are free):

| Stage | Count (default plan) | Model | Input tok (exp) | Output tok (exp) | Skill loaded |
|---|---|---|---|---|---|
| Eval generation | 1 | judge | 3000 + S | 2000 | yes |
| Executor — with-skill | E×T = 20 | executor | 14000 + S | 3000 | yes |
| Executor — baseline | E×T = 20 (if configs≥2) | executor | 14000 | 3000 | no |
| Grader | E×C×T = 40 | judge | 5000 | 1000 | no |
| Artifact judge | 1 | judge | 4000 + S | 3000 | yes |
| Triggering | Q×R = 48 | judge | 1000 | 100 | no |

- **S = skill tokens** (`len(text)//4`, the heuristic already in `static_checks`):
  `S_low` = SKILL.md only; `S_high` = SKILL.md + `references/`; `S_exp` = SKILL.md + ½·references.
- **Default plan** (all flag-overridable): E=4, T=5, C=2, Q=16, R=3;
  executor `claude-sonnet-4-6`, judge `claude-opus-4-8`. The model supports **C ∈ {1, 2}**
  only (with-skill, optionally + one no-skill baseline — the two configs of a real run);
  `estimate()` validates the plan (E≥1, T≥1, C∈{1,2}, Q≥0, R≥1) and raises `ValueError`
  on anything out of range, so every reachable estimate stays coherent.
- **Range:** per stage and scenario `∈ {low, exp, high}`,
  `input_each = round(base_input × f) + (S_scenario if skill_loaded)`,
  `output_each = round(base_output × f)`, with `f = {low:0.65, exp:1.0, high:2.0}`.
- **Cost:** `Σ count × (input_each × in_rate + output_each × out_rate) / 1e6`, per scenario.
- A model with no price entry contributes `$0` and is listed under `pricing_unknown`
  with a note (tokens are still counted).

Constants live as documented top-of-file values in `cost_estimate.py`, tunable and
later calibratable from `history.json`. Anchored to the real `ship` run
(~18–20k tokens/executor, ~22–24k/judge).

## Output

- Markdown table to stdout: per-stage (model, count, expected tokens, $ range) +
  a totals row with the token range and the **$ low–expected–high** headline.
- `estimate.json` written to `--out` only when `--write` is passed (machine-readable,
  same numbers). Without `--write` the command is read-only: it resolves the skill into a
  temp dir and prints the markdown, leaving nothing on disk.
- A disclaimer line: heuristic ranges; prompt caching not modeled (estimates run
  slightly conservative/high); excludes the free deterministic structural scan.

## Testing

`tests/test_pricing.py` + `tests/test_cost_estimate.py` (deterministic, no network):
ranges monotonic (low ≤ exp ≤ high); totals = sum of stage tokens; cost scales with
evals/trials/configs; bigger skill ⇒ bigger estimate; unknown model flagged not crashed;
`pricing.rate` known/unknown. Plus the existing self-validation gate must stay 100/A.

## Out of scope (YAGNI)

Budget caps / approval gates / auto-scaling; calibration from history (constants are
calibration-ready but the loop is deferred); prompt-cache modeling.
