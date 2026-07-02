import json

import pytest

import aggregate
import stats


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
    assert agg["normalized_gain"] is None
    assert agg["paired_lift"] is None


def test_aggregate_normalized_gain(tmp_path):
    # with-skill mean 0.8, baseline mean 0.6 -> gain (0.8-0.6)/(1-0.6) = 0.5
    for r in (1, 2):
        _mk_run(tmp_path, 0, "with_skill", r, _grading(0.8))
        _mk_run(tmp_path, 0, "without_skill", r, _grading(0.6))
    agg = aggregate.aggregate(tmp_path)
    assert agg["baseline_lift"] == pytest.approx(0.2)
    assert agg["normalized_gain"] == pytest.approx(0.5)


def test_aggregate_paired_significance_beats_unpaired(tmp_path):
    # Two evals of very different difficulty; the skill adds a steady ~0.19 on
    # each. The between-eval difficulty swamps an unpaired SE (verdict n.s.),
    # but cancels in the paired difference (Miller 2024) -> significant.
    for r in (1, 2):
        _mk_run(tmp_path, 0, "with_skill", r, _grading(0.4))  # hard eval
        _mk_run(tmp_path, 0, "without_skill", r, _grading(0.2))
        _mk_run(tmp_path, 1, "with_skill", r, _grading(0.9))  # easy eval
        _mk_run(tmp_path, 1, "without_skill", r, _grading(0.72))
    agg = aggregate.aggregate(tmp_path)
    # unpaired SE of the difference would not clear the lift...
    unpaired = stats.se_of_difference(
        stats.std_error([0.4, 0.4, 0.9, 0.9]), stats.std_error([0.2, 0.2, 0.72, 0.72])
    )
    assert agg["baseline_lift"] <= unpaired  # unpaired alone would be n.s.
    # ...but the paired inference exploits the correlation and clears it.
    assert agg["paired_lift"] == pytest.approx(0.19)
    assert agg["significant"] is True


def test_aggregate_paired_none_with_single_eval(tmp_path):
    # One eval -> no between-eval variance to exploit; paired fields stay None
    # and significance falls back to the unpaired within-eval SE.
    for r in (1, 2, 3):
        _mk_run(tmp_path, 0, "with_skill", r, _grading(1.0))
        _mk_run(tmp_path, 0, "without_skill", r, _grading(0.0))
    agg = aggregate.aggregate(tmp_path)
    assert agg["paired_lift"] is None
    assert agg["paired_se"] is None
    assert agg["significant"] is True  # unpaired fallback still fires
