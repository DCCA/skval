"""Map raw behavioral artifacts to normalized dimension scores (D2-D5), each [0, 1].

- D2 Effectiveness: with-skill eval pass rate (baseline lift reported as detail).
- D3 Reliability: tau-bench pass^k at a moderate k (default ~N/2) for with-skill.
- D4 Artifact quality: fraction of the LLM judge's binary rubric criteria passed.
- D5 Triggering: F1 over should-trigger / should-not-trigger activation.
"""

from __future__ import annotations


def d2_effectiveness(agg: dict) -> float:
    return agg["configs"]["with_skill"]["pass_rate"]["mean"]


def d3_reliability(agg: dict, k_rel: int | None = None) -> float:
    ph = agg["pass_hat_k"]["with_skill"]
    if not ph:
        return 0.0
    n = max(int(k) for k in ph)
    if k_rel is None:
        k_rel = max(2, (n + 1) // 2)
    k_rel = min(k_rel, n)
    return ph[str(k_rel)]


def d4_artifact(judgment: dict) -> float:
    criteria = judgment.get("criteria", [])
    if not criteria:
        return 0.0
    passed = sum(1 for c in criteria if c.get("passed"))
    return passed / len(criteria)


def d5_triggering(trig: dict) -> float:
    if "f1" in trig:
        return trig["f1"]
    tp = trig.get("tp", 0)
    fp = trig.get("fp", 0)
    fn = trig.get("fn", 0)
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def behavioral_dims(
    agg: dict | None = None,
    artifact: dict | None = None,
    triggering: dict | None = None,
    k_rel: int | None = None,
) -> tuple[dict, dict]:
    """Assemble {D2..D5} scores + detail from whatever signals are present."""
    dims: dict[str, float] = {}
    detail: dict[str, dict] = {}

    if agg and agg.get("configs", {}).get("with_skill"):
        dims["D2"] = d2_effectiveness(agg)
        detail["D2"] = {
            "pass_rate": agg["configs"]["with_skill"]["pass_rate"],
            "baseline_lift": agg.get("baseline_lift"),
            "significant": agg.get("significant"),
        }
        if agg.get("pass_hat_k", {}).get("with_skill"):
            dims["D3"] = d3_reliability(agg, k_rel)
            detail["D3"] = {"pass_hat_k": agg["pass_hat_k"]["with_skill"]}

    if artifact and artifact.get("criteria"):
        dims["D4"] = d4_artifact(artifact)
        detail["D4"] = {"criteria": artifact["criteria"]}

    if triggering:
        dims["D5"] = d5_triggering(triggering)
        detail["D5"] = {
            k: triggering[k]
            for k in ("precision", "recall", "f1", "tp", "fp", "fn", "tn")
            if k in triggering
        }

    return dims, detail
