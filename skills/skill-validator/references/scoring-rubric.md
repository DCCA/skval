# skval Scoring Rubric

This document is the human-readable companion to `scripts/scoring.py`, which is
the **source of truth**. If you change weights or bands, change them in both and
keep this in sync.

## Dimensions

Each dimension is normalized to `[0, 1]` before weighting (AgentBench "OA"
pattern: normalize, then aggregate, so no dimension's scale dominates).

| ID | Dimension | Type | Measures |
|----|-----------|------|----------|
| D1 | Structural integrity | Deterministic | Frontmatter validity, naming, description rules, single-`SKILL.md`, size budget, broken refs |
| D2 | Effectiveness | Behavioral (LLM-graded) | Task pass rate **and** lift over a no-skill baseline |
| D3 | Reliability | Behavioral | Consistency across N independent trials (`pass^k`) |
| D4 | Artifact quality | Intrinsic LLM-judge | Clarity, instruction design, completeness, examples |
| D5 | Triggering accuracy | Behavioral (`claude -p`) | Fires on should-trigger, silent on should-not (precision/recall/F1) |
| D6 | Safety / least-surprise | Deterministic + LLM | Destructive, injection, or surprising content |

## Weights (default)

| Dimension | Weight | Why |
|-----------|--------|-----|
| D2 Effectiveness | 0.30 | The point of a skill is to help; strongest signal. |
| D3 Reliability | 0.20 | Consistency gates shippability (tau-bench). |
| D4 Artifact quality | 0.20 | Predicts generalization beyond the eval set; the LLM-judge core. |
| D5 Triggering | 0.15 | A skill that never fires is worthless. |
| D1 Structural | 0.15 | Necessary hygiene; cheap, gameability-resistant floor. |
| **D6 Safety** | **gate** | Veto multiplier (0 or 1), **not** a weighted term. |

Weights sum to 1.0 over D1–D5. They are a calibration **hypothesis** — to be
tuned (M3) so the composite correlates with human judgment on a labeled corpus.

**Partial runs:** dimensions absent from a run (e.g. D2–D5 in the M0
structural-only path) are excluded and the remaining weights renormalize, so the
composite always reflects what was actually measured.

## Composite formula

```
normalized dᵢ ∈ [0,1]   for present i in {D1..D5}
safety_gate ∈ {0,1}     (D6: 1 = pass, 0 = veto)
raw = Σ(wᵢ·dᵢ) / Σ(wᵢ)          # over present dimensions
SkillScore = round(100 · safety_gate · raw)
```

## Grade bands & verdict

| Score | Grade | Verdict |
|-------|-------|---------|
| 90–100 | A | Ship |
| 80–89 | B | Ship |
| 70–79 | C | Revise |
| 50–69 | D | Revise |
| 0–49 | F | Reject |
| any, safety=0 | F | Reject |

## Worked example (from the PRD)

`D2=0.84, D3=0.62, D4=0.80, D5=0.90, D1=0.75`, safety pass:

```
raw = .30·.84 + .20·.62 + .20·.80 + .15·.90 + .15·.75 = 0.7835
SkillScore = round(100 · 1 · 0.7835) = 78  →  Grade C, Verdict Revise
```
