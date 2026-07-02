import math

import pytest

import stats


def test_mean_and_stddev():
    assert stats.mean([2, 4, 6]) == 4.0
    assert stats.stddev([2, 4, 6]) == pytest.approx(2.0)  # sample stddev (n-1)
    assert stats.stddev([5]) == 0.0
    assert stats.mean([]) == 0.0


def test_std_error():
    assert stats.std_error([2, 4, 6]) == pytest.approx(2.0 / math.sqrt(3))
    assert stats.std_error([5]) == 0.0


def test_summarize_shape():
    s = stats.summarize([0.8, 0.9, 1.0])
    assert set(s) == {"mean", "stddev", "std_error", "min", "max", "n"}
    assert s["n"] == 3 and s["min"] == 0.8 and s["max"] == 1.0


def test_pass_hat_k():
    # 3/3 successes => pass^k = 1 for all k <= 3
    assert stats.pass_hat_k(3, 3, 1) == 1.0
    assert stats.pass_hat_k(3, 3, 3) == 1.0
    # 2/3 successes: pass^1 = 2/3 ; pass^2 = C(2,2)/C(3,2) = 1/3
    assert stats.pass_hat_k(2, 3, 1) == pytest.approx(2 / 3)
    assert stats.pass_hat_k(2, 3, 2) == pytest.approx(1 / 3)
    # k greater than successes => 0
    assert stats.pass_hat_k(1, 3, 2) == 0.0


def test_pass_hat_k_validation():
    with pytest.raises(ValueError):
        stats.pass_hat_k(1, 3, 4)  # k > trials
    with pytest.raises(ValueError):
        stats.pass_hat_k(0, 0, 1)  # trials < 1


def test_pass_hat_k_over_evals():
    # eval A 3/3 -> 1.0 ; eval B 2/3 -> 1/3 ; mean of the two
    assert stats.pass_hat_k_over_evals([(3, 3), (2, 3)], 2) == pytest.approx((1.0 + 1 / 3) / 2)


def test_se_of_difference():
    assert stats.se_of_difference(0.3, 0.4) == pytest.approx(0.5)


def test_normalized_gain():
    # Hake gain: same +0.05 absolute lift, but far more of the headroom closed
    # on a high baseline -> higher normalized gain.
    assert stats.normalized_gain(0.8, 0.6) == pytest.approx(0.5)  # 0.2 / 0.4
    assert stats.normalized_gain(0.95, 0.9) == pytest.approx(0.5)  # 0.05 / 0.1
    # a regression gives a negative gain
    assert stats.normalized_gain(0.3, 0.5) == pytest.approx(-0.4)  # -0.2 / 0.5
    # no headroom (baseline already maxed) -> undefined
    assert stats.normalized_gain(0.5, 1.0) is None


def test_paired_diff():
    m, se, n = stats.paired_diff([(0.8, 0.5), (0.6, 0.4), (1.0, 0.9)])
    assert (m, n) == (pytest.approx(0.2), 3)  # diffs 0.3, 0.2, 0.1
    assert se == pytest.approx(0.1 / math.sqrt(3))  # stddev 0.1 over sqrt(3)
    # a single pair has no between-item variance -> se 0
    assert stats.paired_diff([(1.0, 0.0)]) == (pytest.approx(1.0), 0.0, 1)
