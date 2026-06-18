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

## Full validation workflow

Run these stages, then compute the score with the bundled engine. Create a todo per stage.

0. **Resolve** the input → canonical skill dir (`scripts/resolve_skill.py`).
1. **Structural + safety** → run the quick-start script to get D1, the D6 gate, and a
   partial scorecard. If the safety gate fails, stop and report Reject.
2. **Resolve evals (hybrid):** if the skill has `evals/evals.json`, use it; otherwise
   **auto-generate** 3–5 task prompts with *discriminating* expectations (assertions a
   wrong output would fail) and a triggering query set (8–10 should-trigger + 8–10
   near-miss should-not). **Review gate is ON** — show generated evals to the user for
   edit/approval before running.
3. **Behavioral runs (D2/D3):** for each eval, dispatch subagents — one executor *with*
   the skill, one *baseline without* — **N=5 trials each**. Capture output, transcript,
   tokens, time.
4. **Grade + judge (D2/D4):** an LLM judge grades each run's expectations (pass/fail +
   cited evidence, reference-guided where a gold output exists) and scores the SKILL.md
   artifact against the D4 rubric. Apply the bias mitigations below.
5. **Triggering (D5):** present the query set via `claude -p` with and without the skill
   available; compute precision/recall/F1 on activation.
6. **Aggregate:** per dimension, compute mean ± stddev and standard error
   (`scripts/stats.py`); `pass^k` for D3; baseline lift for D2, flagged *significant*
   only if the delta exceeds the standard error of the difference.
7. **Score + report:** normalize each dimension to 0–1, then
   `scripts/scoring.py:score_skill(dims, safety_pass)` → composite/grade/verdict;
   `scripts/scorecard.py:build_scorecard(...)` + `write_scorecard(...)` → the final
   `scorecard.json` + `scorecard.md`. Set `metadata.mode = "full"`.

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
