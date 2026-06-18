import pytest

import dimensions as dim


def test_d2_effectiveness():
    agg = {"configs": {"with_skill": {"pass_rate": {"mean": 0.86}}}}
    assert dim.d2_effectiveness(agg) == 0.86


def test_d3_reliability_default_k():
    # n=5 trials -> default k_rel = max(2, (5+1)//2) = 3
    agg = {"pass_hat_k": {"with_skill": {"1": 0.9, "2": 0.8, "3": 0.7, "4": 0.6, "5": 0.5}}}
    assert dim.d3_reliability(agg) == 0.7


def test_d3_reliability_clamped_to_available():
    agg = {"pass_hat_k": {"with_skill": {"1": 0.9}}}
    assert dim.d3_reliability(agg) == 0.9


def test_d4_artifact_fraction():
    j = {"criteria": [{"passed": True}, {"passed": True}, {"passed": False}, {"passed": True}]}
    assert dim.d4_artifact(j) == 0.75


def test_d4_artifact_empty():
    assert dim.d4_artifact({"criteria": []}) == 0.0


def test_d5_triggering_from_counts():
    trig = {"tp": 8, "fp": 1, "fn": 2, "tn": 9}
    p, r = 8 / 9, 8 / 10
    assert dim.d5_triggering(trig) == pytest.approx(2 * p * r / (p + r))


def test_d5_triggering_from_f1():
    assert dim.d5_triggering({"f1": 0.9}) == 0.9


def test_d5_triggering_zero():
    assert dim.d5_triggering({"tp": 0, "fp": 0, "fn": 0}) == 0.0


def test_behavioral_dims_assembles_present_signals():
    agg = {
        "configs": {"with_skill": {"pass_rate": {"mean": 0.8}}},
        "pass_hat_k": {"with_skill": {"1": 0.8, "2": 0.6}},
        "baseline_lift": 0.4,
        "significant": True,
    }
    artifact = {"criteria": [{"passed": True}, {"passed": False}]}
    triggering = {"f1": 0.9}
    dims, detail = dim.behavioral_dims(agg, artifact, triggering)
    assert set(dims) == {"D2", "D3", "D4", "D5"}
    assert dims["D2"] == 0.8 and dims["D4"] == 0.5 and dims["D5"] == 0.9
    assert detail["D2"]["baseline_lift"] == 0.4
