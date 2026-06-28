---
name: skill-validator
description: Use when you need to validate, score, grade, or benchmark a Claude Code skill — to decide whether a skill is good enough to ship, to compare two versions of a skill, or to check whether a skill triggers correctly. Use when someone asks to evaluate a skill, review a SKILL.md, score a skill against evals, run a skill through benchmarks, or check a skill's quality, reliability, effectiveness, or safety before publishing.
---

# Skill Validator (skval)

## Overview

skval takes a skill — a directory, a `SKILL.md`, or a packaged `.skill` — runs it
through evals and benchmarks, and returns a **Skill Score (0–100)** with a letter
grade, a per-dimension breakdown, ranked findings, and a **Ship / Revise / Reject**
verdict.

**Core principle — two-tier, gated scoring:** cheap deterministic checks first, then
LLM-as-judge for everything qualitative; combine into a *normalized weighted
composite* where **safety is a veto gate**, not a weighted term. Always report the
per-dimension vector beside the headline number so trade-offs stay visible.

## When to use

- "Is this skill good enough to ship?" / "grade/score/validate this skill"
- "Did my edit make the skill better or did it regress?" (version comparison)
- "Does my skill trigger when it should (and stay quiet when it shouldn't)?"
- Reviewing a submitted `SKILL.md`; checking a skill's quality, reliability, or safety.

**Not for:** *writing* or *improving* skills (use skill-creator / writing-skills) —
skval judges and hands findings back. It is not a security sandbox; safety scanning is
best-effort.

## Quick start — deterministic structural scan (fast, no model calls)

Run this first. It scores structure (D1) and runs the safety gate (D6), and is the
floor every full run builds on:

```bash
uv run python skills/skill-validator/scripts/validate_structural.py <skill-source> --out skval-runs/<name>
```

Writes `scorecard.json` + `scorecard.md` to the out dir; exits non-zero if the verdict
is Reject (e.g. a safety veto). `<skill-source>` is a directory, a `SKILL.md`, or a
`.skill`/`.zip`.

## The scoring model

Six dimensions; D1/D6 are deterministic, D2–D5 are model-driven. See
[references/scoring-rubric.md](references/scoring-rubric.md) (the source of truth for
weights and bands) and [references/schemas.md](references/schemas.md) for the output
shape.

| Dim | Dimension | Weight | How it's measured |
|-----|-----------|--------|-------------------|
| D2 | Effectiveness | 0.30 | with-skill vs no-skill eval pass rate + baseline lift |
| D3 | Reliability | 0.20 | `pass^k` across N independent trials |
| D4 | Artifact quality | 0.20 | LLM judge, decomposed binary rubric + evidence |
| D5 | Triggering | 0.15 | precision/recall/F1 on should/should-not queries |
| D1 | Structural | 0.15 | deterministic static checks |
| D6 | Safety | **gate** | unsafe ⇒ score 0, verdict Reject |

Bands: A≥90, B≥80 (Ship); C≥70, D≥50 (Revise); else F (Reject). Default trials **N=5**.

## Pick the eval strategy (classify first)

Different skills need different evals, so **classify the skill before generating evals.**
Run `scripts/classify.py <skill-source>` for a transparent first pass (it prints the type,
the runner-up `also`, and the matched signals), then confirm with your own read and route.
The scorecard shows the detected `Type` + confidence and flags a low-confidence (ambiguous)
classification as a finding; force the type with `--type <type>` on `validate_structural`/`validate_full`.

| Type | Tell-tale | Eval strategy & tools |
|------|-----------|-----------------------|
| **task** (default) | one-shot input → output | standard single-turn executor + grader |
| **file_transform** | acts on / produces files (pdf, xlsx, docx, …) | eval-generator creates **fixtures** (`scripts/eval_fixtures.py`); executor stages inputs; grader opens & **evaluates output files** (recalc formulas) |
| **interactive** | must ask / confirm / gather before acting | **`type: multi_turn`** evals + the **[user-simulator](agents/user-simulator.md)**; grade interaction via `scripts/conversation.py` |
| **discipline / process** | shapes *how* you work (TDD, debugging, review) | scenario evals; weight **D4 artifact quality**; expect a small single-task lift — judge adherence |
| **reference / knowledge** | provides facts / answers | Q&A evals graded against `expected_output` |

A skill can be more than one (e.g. file_transform **and** interactive) — combine strategies.
`scripts/classify.py:recommend_strategy(type)` returns the executor mode / fixtures / grading
focus / agents for each.

## Full validation workflow

Make a workspace dir, run these stages (each has a guide in `agents/`), then let
`validate_full.py` assemble the scorecard. Create a todo per stage.

0. **Resolve** the input → canonical skill dir (`scripts/resolve_skill.py`).
1. **Structural + safety** → run `scripts/validate_structural.py` (D1 + D6 gate). If the
   safety gate fails, stop and report Reject.
2. **Classify & evals (hybrid)** → classify the skill (above) to pick the strategy, then
   follow [agents/eval-generator.md](agents/eval-generator.md): use the skill's bundled
   `evals/evals.json` if present, else synthesize discriminating evals **of the right kind for
   the type** (fixtures for file_transform, `multi_turn` for interactive, …); also build the
   triggering query set. **Review gate is ON.**
3. **Behavioral runs (D2/D3)** → for each eval, dispatch [agents/executor.md](agents/executor.md)
   subagents — with-skill and without-skill baseline, **N=5 trials each** — into
   `workspace/runs/eval-<id>/<config>/run-<k>/`.
4. **Grade + judge (D2/D4)** → [agents/grader.md](agents/grader.md) writes a `grading.json`
   per run; [agents/artifact-judge.md](agents/artifact-judge.md) writes
   `workspace/artifact_judgment.json`. Apply the bias mitigations below.
5. **Triggering (D5)** → [agents/triggering.md](agents/triggering.md) writes
   `workspace/triggering.json`.
6. **Assemble & score** → `uv run python skills/skill-validator/scripts/validate_full.py <skill-source> <workspace>`.
   It aggregates the runs (`pass^k`, baseline lift, significance), maps every signal to
   D1–D5, applies the safety gate, and writes `scorecard.json` + `scorecard.md`
   (`metadata.mode = "full"`).

## Comparing versions, batches & regressions

- **Version A/B** — validate both versions, then `scripts/compare.py:compare_scorecards(a, b)`
  for a per-dimension diff with significance. For output-level judging, follow
  [agents/comparator.md](agents/comparator.md): it blinds provenance and **position-swaps**,
  then `compare.py:decide_pairwise(...)` collapses both orders to a verdict.
- **Regression tracking** — `scripts/history.py:append_run(history.json, scorecard)` after
  each run; `detect_regression(history)` flags a drop vs. the best prior run.
- **Batch** — rank many scorecards with `scripts/batch.py:rank_scorecards([...])`.
- **Eval-viewer** — `scripts/benchmark_export.py` emits a skill-creator-compatible
  `benchmark.json` so runs render in that project's viewer.
- **SkillsBench-style paired evals** — when reporting D2 lift, preserve no-skill pass
  rate, with-skill pass rate, absolute lift, and normalized gain; see
  [`docs/references/skillsbench.md`](../../docs/references/skillsbench.md) for the
  research note that motivates this future scorecard improvement.
- **Calibration** — tune dimension weights against a labeled corpus with
  `scripts/calibrate.py:suggest_weights(examples)`.

## LLM-as-judge: bias mitigations (required)

- **Blind provenance / cross-family:** never tell the judge which model or version made
  an output; prefer a judge from a different model family than the executor.
- **Position-swap** every pairwise comparison (version A/B, with/without); require a
  consistent verdict across both orders or score a tie.
- **Reference-guided** grading when a gold/expected output exists.
- **Atomic binary criteria** with cited evidence — no holistic 1–5 scores.
- **Variance is a metric:** N=5 trials; report error bars; a delta isn't real unless it
  beats the noise.

## Output

`scorecard.json` (machine-readable) + `scorecard.md` (the report: score bar, dimension
table, ranked findings, verdict). Findings are ordered by estimated score impact so the
highest-value fix is first.
