import json

import pytest

import aggregate


def _grading(pass_rate, total=2):
    passed = round(pass_rate * total)
    return {
        "summary": {
            "pass_rate": pass_rate,
            "passed": passed,
            "failed": total - passed,
            "total": total,
        }
    }


def _mk_run(base, eval_id, config, run, grading):
    d = base / f"eval-{eval_id}" / config / f"run-{run}"
    d.mkdir(parents=True)
    (d / "grading.json").write_text(json.dumps(grading))


def test_aggregate_basic(tmp_path):
    for r in (1, 2, 3):
        _mk_run(tmp_path, 0, "with_skill", r, _grading(1.0))
        _mk_run(tmp_path, 0, "without_skill", r, _grading(0.0))
    agg = aggregate.aggregate(tmp_path)
    assert agg["configs"]["with_skill"]["pass_rate"]["mean"] == 1.0
    assert agg["configs"]["without_skill"]["pass_rate"]["mean"] == 0.0
    assert agg["baseline_lift"] == 1.0
    assert agg["significant"] is True
    assert agg["pass_hat_k"]["with_skill"]["1"] == 1.0
    assert agg["pass_hat_k"]["with_skill"]["3"] == 1.0


def test_aggregate_mixed_reliability(tmp_path):
    _mk_run(tmp_path, 0, "with_skill", 1, _grading(1.0))
    _mk_run(tmp_path, 0, "with_skill", 2, _grading(1.0))
    _mk_run(tmp_path, 0, "with_skill", 3, _grading(0.5))  # not a full success
    for r in (1, 2, 3):
        _mk_run(tmp_path, 0, "without_skill", r, _grading(0.0))
    agg = aggregate.aggregate(tmp_path)
    # 2/3 full successes -> pass^1 = 2/3, pass^2 = C(2,2)/C(3,2) = 1/3
    assert agg["pass_hat_k"]["with_skill"]["1"] == pytest.approx(2 / 3)
    assert agg["pass_hat_k"]["with_skill"]["2"] == pytest.approx(1 / 3)


def test_aggregate_insignificant_when_noisy(tmp_path):
    # tiny, noisy lift that should not clear the standard error of the difference
    for r, pr in enumerate([1.0, 0.0, 1.0], start=1):
        _mk_run(tmp_path, 0, "with_skill", r, _grading(pr))
    for r, pr in enumerate([1.0, 0.0, 0.5], start=1):
        _mk_run(tmp_path, 0, "without_skill", r, _grading(pr))
    agg = aggregate.aggregate(tmp_path)
    assert agg["significant"] is False


def test_aggregate_no_baseline(tmp_path):
    for r in (1, 2):
        _mk_run(tmp_path, 0, "with_skill", r, _grading(1.0))
    agg = aggregate.aggregate(tmp_path)
    assert agg["baseline_lift"] is None
    assert agg["significant"] is None
