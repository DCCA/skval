"""Aggregate behavioral run results into per-configuration statistics.

Reads runs via the shared ``runs_io`` loader and computes, per configuration: a
pass-rate summary (mean/stddev/std_error), tau-bench ``pass^k`` over evals, the
with-skill vs without-skill baseline lift, its Hake normalized gain (headroom-
corrected), and whether that lift is significant.

Significance is one-sided (did the skill help beyond noise) and is computed at
full precision so display rounding can't flip the verdict. It uses a *paired*
per-eval difference (Miller 2024) when >=2 evals appear in both configs — shared
per-eval difficulty cancels, lowering the SE — and falls back to the unpaired
``se_of_difference`` for a single eval. (``compare.compare_scorecards`` uses a
two-sided test for per-dimension change, a different question — a regression
there is still a "significant" change.)
"""

from __future__ import annotations

import json

import runs_io
import stats


def _successes_per_eval(runs: list[dict], threshold: float) -> list[tuple[int, int]]:
    by_eval: dict = {}
    for r in runs:
        c, t = by_eval.get(r["eval_id"], (0, 0))
        t += 1
        if r["pass_rate"] >= threshold:
            c += 1
        by_eval[r["eval_id"]] = (c, t)
    return list(by_eval.values())


def _mean_pass_by_eval(runs: list[dict]) -> dict:
    sums: dict = {}
    counts: dict = {}
    for r in runs:
        sums[r["eval_id"]] = sums.get(r["eval_id"], 0.0) + r["pass_rate"]
        counts[r["eval_id"]] = counts.get(r["eval_id"], 0) + 1
    return {e: sums[e] / counts[e] for e in sums}


def aggregate(bench_dir, success_threshold: float = 1.0) -> dict:
    results = runs_io.load_runs(bench_dir)

    configs: dict[str, dict] = {}
    pass_hat: dict[str, dict] = {}
    for config, runs in results.items():
        configs[config] = {
            "pass_rate": stats.summarize([r["pass_rate"] for r in runs]),
            "n_runs": len(runs),
        }
        spe = _successes_per_eval(runs, success_threshold)
        min_trials = min((t for _, t in spe), default=0)
        pass_hat[config] = {
            str(k): stats.pass_hat_k_over_evals(spe, k) for k in range(1, min_trials + 1)
        }

    lift = se_diff = significant = None
    norm_gain = paired_lift = paired_se = None
    if "with_skill" in results and "without_skill" in results:
        w = [r["pass_rate"] for r in results["with_skill"]]
        b = [r["pass_rate"] for r in results["without_skill"]]
        raw_lift = stats.mean(w) - stats.mean(b)
        raw_se = stats.se_of_difference(stats.std_error(w), stats.std_error(b))
        lift = round(raw_lift, 4)
        se_diff = round(raw_se, 4)

        gain = stats.normalized_gain(stats.mean(w), stats.mean(b))
        norm_gain = round(gain, 4) if gain is not None else None

        # Paired inference (Miller 2024): pair the per-eval means so shared
        # per-eval difficulty cancels. Needs >=2 evals present in both configs
        # for a between-eval SE; otherwise fall back to the unpaired within-eval
        # SE (a single eval has no between-eval variance to exploit).
        ew = _mean_pass_by_eval(results["with_skill"])
        eb = _mean_pass_by_eval(results["without_skill"])
        shared = sorted(ew.keys() & eb.keys())
        if len(shared) >= 2:
            p_mean, p_se, _ = stats.paired_diff([(ew[e], eb[e]) for e in shared])
            paired_lift = round(p_mean, 4)
            paired_se = round(p_se, 4)
            significant = bool(p_mean > p_se)  # decided at full precision
        else:
            significant = bool(raw_lift > raw_se)

    return {
        "configs": configs,
        "pass_hat_k": pass_hat,
        "baseline_lift": lift,
        "se_difference": se_diff,
        "normalized_gain": norm_gain,
        "paired_lift": paired_lift,
        "paired_se": paired_se,
        "significant": significant,
        "success_threshold": success_threshold,
    }


if __name__ == "__main__":
    import sys

    print(json.dumps(aggregate(sys.argv[1]), indent=2))
