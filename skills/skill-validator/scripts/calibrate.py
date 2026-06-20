"""Calibrate dimension weights against a labeled corpus.

Given examples of ``{dims, human_score}``, measure how well a weight vector's
composite agrees with human judgment (Spearman rank correlation) and search for a
weighting that agrees better. Use this to tune ``scoring.DEFAULT_WEIGHTS`` so the
headline score tracks what humans consider a good skill (PRD section 12).
"""

from __future__ import annotations

import random

import scoring

DIMS = ["D1", "D2", "D3", "D4", "D5"]


def _ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1  # 1-based average rank for ties
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs, ys) -> float:
    xs, ys = list(xs), list(ys)
    n = len(xs)
    if n < 2:
        return 0.0
    rx, ry = _ranks(xs), _ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        return 0.0
    return round(cov / ((vx * vy) ** 0.5), 6)


def evaluate_weights(examples: list[dict], weights: dict) -> float:
    comps = [scoring.composite(e["dims"], True, weights) for e in examples]
    humans = [e["human_score"] for e in examples]
    return spearman(comps, humans)


def _normalize(w: dict) -> dict:
    s = sum(w.values())
    return {k: v / s for k, v in w.items()} if s > 0 else w


def suggest_weights(examples: list[dict], samples: int = 300, seed: int = 0) -> dict:
    """Random search over the weight simplex; never worse than DEFAULT_WEIGHTS."""
    rng = random.Random(seed)
    best_w = dict(scoring.DEFAULT_WEIGHTS)
    best = evaluate_weights(examples, best_w)
    for _ in range(samples):
        w = _normalize({d: rng.random() for d in DIMS})
        s = evaluate_weights(examples, w)
        if s > best:
            best, best_w = s, w
    return {"weights": {d: round(best_w.get(d, 0.0), 4) for d in DIMS}, "score": best}


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Calibrate skval dimension weights against a labeled corpus (library helper)."
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=300,
        help="random-search samples for callers using suggest_weights",
    )
    parser.add_argument(
        "--seed", type=int, default=0, help="random seed for callers using suggest_weights"
    )
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
