"""Compare two skill versions (A = old/baseline, B = new/candidate).

Two complementary tools:
- ``compare_scorecards`` — diff two scorecards dimension-by-dimension, marking a
  per-dimension change significant only when it clears the standard error of the
  difference (Miller 2024), plus the overall score and verdict change.
- ``decide_pairwise`` / ``position_bias_detected`` — neutralize position bias in an
  LLM pairwise judgment by requiring agreement across both presentation orders
  (Zheng et al. 2023). The comparator agent runs the judge twice (A-first, B-first)
  and reports each winner as an original label; this collapses them to a verdict.
"""

from __future__ import annotations

import stats


def decide_pairwise(winner_ab: str, winner_ba: str) -> str:
    """Return the consistent winner ("A"/"B") across both orders, else "tie".

    ``winner_ab`` is the winner when shown order [A, B]; ``winner_ba`` when shown
    [B, A]. Both are expressed as the original label ("A", "B", or "tie"). If they
    disagree (the classic symptom of position bias), the result is a tie.
    """
    if winner_ab == winner_ba and winner_ab in ("A", "B"):
        return winner_ab
    return "tie"


def position_bias_detected(winner_ab: str, winner_ba: str) -> bool:
    """True when the judge favored the first-shown answer in both orders."""
    return (winner_ab, winner_ba) in {("A", "B"), ("B", "A")}


def _se(entry: dict) -> float | None:
    pr = entry.get("pass_rate")
    if isinstance(pr, dict) and "std_error" in pr:
        return pr["std_error"]
    return None


def compare_scorecards(a: dict, b: dict) -> dict:
    """Diff scorecard B against A. Positive deltas mean B improved over A."""
    dims_a = a.get("dimensions", {})
    dims_b = b.get("dimensions", {})
    out_dims: dict[str, dict] = {}
    for dim in sorted(set(dims_a) | set(dims_b)):
        ea, eb = dims_a.get(dim, {}), dims_b.get(dim, {})
        sa, sb = ea.get("score"), eb.get("score")
        entry: dict = {"a": sa, "b": sb}
        if sa is not None and sb is not None:
            entry["delta"] = round(sb - sa, 4)
            se_a, se_b = _se(ea), _se(eb)
            if se_a is not None and se_b is not None:
                se_diff = stats.se_of_difference(se_a, se_b)
                entry["se_difference"] = round(se_diff, 4)
                entry["significant"] = bool(abs(entry["delta"]) > se_diff)
        out_dims[dim] = entry

    va, vb = a.get("verdict"), b.get("verdict")
    return {
        "overall_delta": b.get("score", 0) - a.get("score", 0),
        "dimensions": out_dims,
        "verdict_change": f"{va} -> {vb}" if va != vb else va,
    }
