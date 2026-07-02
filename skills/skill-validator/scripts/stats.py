"""Pure statistics helpers for skval scoring.

No third-party dependencies. Covers the variance/reliability machinery the
scorecard needs: sample mean/stddev/standard-error, a compact summary, the
tau-bench ``pass^k`` reliability metric, the standard error of a difference and
the ``paired_diff`` (Miller 2024) used to decide whether a with-skill vs no-skill
delta is real, and the Hake ``normalized_gain`` that corrects lift for headroom.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from math import comb


def mean(xs: Iterable[float]) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def stddev(xs: Iterable[float]) -> float:
    """Sample standard deviation (n-1). 0.0 for fewer than two values."""
    xs = list(xs)
    n = len(xs)
    if n < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def std_error(xs: Iterable[float]) -> float:
    """Standard error of the mean = stddev / sqrt(n)."""
    xs = list(xs)
    n = len(xs)
    return stddev(xs) / math.sqrt(n) if n >= 2 else 0.0


def summarize(xs: Iterable[float]) -> dict:
    xs = list(xs)
    return {
        "mean": round(mean(xs), 4),
        "stddev": round(stddev(xs), 4),
        "std_error": round(std_error(xs), 4),
        "min": round(min(xs), 4) if xs else 0.0,
        "max": round(max(xs), 4) if xs else 0.0,
        "n": len(xs),
    }


def pass_hat_k(successes: int, trials: int, k: int) -> float:
    """tau-bench pass^k for a single eval.

    Probability that all k of a randomly chosen k-subset of the ``trials``
    runs succeeded: C(successes, k) / C(trials, k). pass^1 is the ordinary
    success rate; it decays fast when the skill is inconsistent.
    """
    if trials < 1:
        raise ValueError("trials must be >= 1")
    if k < 1 or k > trials:
        raise ValueError("k must be in [1, trials]")
    if successes < k:
        return 0.0
    return comb(successes, k) / comb(trials, k)


def pass_hat_k_over_evals(per_eval: Iterable[tuple[int, int]], k: int) -> float:
    """Mean pass^k across evals. ``per_eval`` is a list of (successes, trials)."""
    vals = [pass_hat_k(c, n, k) for (c, n) in per_eval]
    return mean(vals)


def se_of_difference(se_a: float, se_b: float) -> float:
    """Standard error of a difference of two independent means: sqrt(se_a^2+se_b^2)."""
    return math.sqrt(se_a**2 + se_b**2)


def normalized_gain(pass_skill: float, pass_baseline: float) -> float | None:
    """Hake normalized gain g = (skill - baseline) / (1 - baseline), in (-inf, 1].

    Corrects the raw lift for baseline headroom: a +0.05 lift closes half the
    remaining gap on a 0.9 baseline (g=0.5) but only a twelfth on a 0.4 baseline
    (g≈0.083). ``None`` when the baseline is already 1.0 (no headroom, undefined).
    """
    headroom = 1.0 - pass_baseline
    if headroom <= 0:
        return None
    return (pass_skill - pass_baseline) / headroom


def paired_diff(pairs: Iterable[tuple[float, float]]) -> tuple[float, float, int]:
    """Paired mean difference, its standard error, and the item count.

    ``pairs`` are (with_skill, without_skill) per matched item (eval). Inference
    on the per-item differences rather than the two group means (Miller 2024)
    cancels the shared per-item level, so when the two conditions are positively
    correlated across items the SE is smaller than an unpaired ``se_of_difference``
    — more power to detect a real lift. SE is 0 for a single pair (no spread).
    """
    diffs = [a - b for a, b in pairs]
    return mean(diffs), std_error(diffs), len(diffs)
