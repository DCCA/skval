"""skval scoring engine.

The single source of truth for turning per-dimension scores into a headline
Skill Score. Pipeline (PRD section 5): normalize each dimension to [0, 1],
apply the safety gate (a veto multiplier, not a weighted term), take the
weighted sum, scale to 0-100, then map to a letter grade and a verdict.

Weights mirror ``references/scoring-rubric.md``. Dimensions absent from
``dims`` (e.g. behavioral dims in the M0 structural-only path) are excluded and
the remaining weights are renormalized, so a partial run still yields a
meaningful composite over what was actually measured.
"""

from __future__ import annotations

# D1 Structural, D2 Effectiveness, D3 Reliability, D4 Artifact, D5 Triggering.
# D6 Safety is a gate (0/1 multiplier), not a weighted term.
DEFAULT_WEIGHTS = {"D2": 0.30, "D3": 0.20, "D4": 0.20, "D5": 0.15, "D1": 0.15}

# (threshold, letter) in descending order.
_BANDS = [(90, "A"), (80, "B"), (70, "C"), (50, "D"), (0, "F")]


def composite(dims: dict, safety_pass: bool, weights: dict | None = None) -> int:
    """Gated, normalized, weighted composite in [0, 100]. 0 if safety fails.

    Dimension values are clamped to [0, 1] so a stray out-of-range input can't
    push the score outside [0, 100]; a present-weight sum of 0 (possible with a
    calibrated weight vector) returns 0 rather than dividing by zero.
    """
    if not safety_pass:
        return 0
    weights = weights or DEFAULT_WEIGHTS
    present = {d: min(1.0, max(0.0, v)) for d, v in dims.items() if d in weights}
    total_w = sum(weights[d] for d in present)
    if not present or total_w <= 0:
        return 0
    raw = sum(weights[d] * present[d] for d in present) / total_w
    return round(100 * raw)


def grade(score: int) -> str:
    for threshold, letter in _BANDS:
        if score >= threshold:
            return letter
    return "F"


def verdict(score: int, safety_pass: bool) -> str:
    if not safety_pass:
        return "Reject"
    if score >= 80:
        return "Ship"
    if score >= 50:
        return "Revise"
    return "Reject"


def score_skill(dims: dict, safety_pass: bool, weights: dict | None = None) -> dict:
    """Bundle the composite, grade, verdict, and the weights actually used."""
    weights = weights or DEFAULT_WEIGHTS
    score = composite(dims, safety_pass, weights)
    return {
        "score": score,
        "grade": grade(score),
        "verdict": verdict(score, safety_pass),
        "weights_used": {d: weights[d] for d in dims if d in weights},
        "dims": dims,
        "safety_pass": safety_pass,
    }
