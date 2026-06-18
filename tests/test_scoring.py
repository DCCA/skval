import pytest

import scoring


def test_default_weights_sum_to_one():
    assert sum(scoring.DEFAULT_WEIGHTS.values()) == pytest.approx(1.0)


def test_composite_matches_prd_example():
    # PRD scorecard example must reproduce 78.
    dims = {"D2": 0.84, "D3": 0.62, "D4": 0.80, "D5": 0.90, "D1": 0.75}
    assert scoring.composite(dims, safety_pass=True) == 78


def test_safety_gate_zeroes_score():
    dims = {"D1": 1.0, "D2": 1.0, "D3": 1.0, "D4": 1.0, "D5": 1.0}
    assert scoring.composite(dims, safety_pass=False) == 0


def test_missing_dims_renormalize():
    # Only D1 present -> its weight renormalizes to 1.0 -> round(100 * 0.5) = 50.
    assert scoring.composite({"D1": 0.5}, safety_pass=True) == 50


def test_grade_bands():
    assert [scoring.grade(s) for s in (95, 85, 75, 55, 40)] == ["A", "B", "C", "D", "F"]


def test_verdict():
    assert scoring.verdict(85, True) == "Ship"
    assert scoring.verdict(72, True) == "Revise"
    assert scoring.verdict(40, True) == "Reject"
    assert scoring.verdict(99, False) == "Reject"  # safety veto overrides score


def test_score_skill_bundle():
    out = scoring.score_skill(
        {"D1": 0.75, "D2": 0.84, "D3": 0.62, "D4": 0.80, "D5": 0.90}, True
    )
    assert out["score"] == 78
    assert out["grade"] == "C"
    assert out["verdict"] == "Revise"
    assert "weights_used" in out
