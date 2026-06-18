"""Aggregate behavioral run results into per-configuration statistics.

Reads the per-run ``grading.json`` files an executor/grader pass produces (the
skill-creator layout ``eval-<N>/<config>/run-<k>/grading.json``) and computes,
per configuration: a pass-rate summary (mean/stddev/std_error), tau-bench
``pass^k`` over evals, the with-skill vs without-skill baseline lift, and whether
that lift is significant (exceeds the standard error of the difference).
"""

from __future__ import annotations

import json
from pathlib import Path

import stats


def _load_config_runs(bench_dir: Path) -> dict[str, list[dict]]:
    bench_dir = Path(bench_dir)
    results: dict[str, list[dict]] = {}
    for eval_dir in sorted(bench_dir.glob("eval-*")):
        try:
            eval_id = int(eval_dir.name.split("-", 1)[1])
        except (ValueError, IndexError):
            eval_id = eval_dir.name
        for config_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir()):
            run_dirs = sorted(config_dir.glob("run-*"))
            if not run_dirs:
                continue
            config = config_dir.name
            results.setdefault(config, [])
            for run_dir in run_dirs:
                gf = run_dir / "grading.json"
                if not gf.exists():
                    continue
                try:
                    g = json.loads(gf.read_text())
                except json.JSONDecodeError:
                    continue
                pr = g.get("summary", {}).get("pass_rate", 0.0)
                results[config].append(
                    {"eval_id": eval_id, "run_number": run_dir.name, "pass_rate": pr}
                )
    return results


def _successes_per_eval(runs: list[dict], threshold: float) -> list[tuple[int, int]]:
    by_eval: dict = {}
    for r in runs:
        c, t = by_eval.get(r["eval_id"], (0, 0))
        t += 1
        if r["pass_rate"] >= threshold:
            c += 1
        by_eval[r["eval_id"]] = (c, t)
    return list(by_eval.values())


def aggregate(bench_dir: Path, success_threshold: float = 1.0) -> dict:
    results = _load_config_runs(bench_dir)

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
            str(k): stats.pass_hat_k_over_evals(spe, k)
            for k in range(1, min_trials + 1)
        }

    lift = None
    se_diff = None
    significant = None
    if "with_skill" in configs and "without_skill" in configs:
        w = configs["with_skill"]["pass_rate"]
        b = configs["without_skill"]["pass_rate"]
        lift = round(w["mean"] - b["mean"], 4)
        se_diff = round(stats.se_of_difference(w["std_error"], b["std_error"]), 4)
        significant = bool(lift > se_diff)

    return {
        "configs": configs,
        "pass_hat_k": pass_hat,
        "baseline_lift": lift,
        "se_difference": se_diff,
        "significant": significant,
        "success_threshold": success_threshold,
    }


if __name__ == "__main__":
    import sys

    print(json.dumps(aggregate(Path(sys.argv[1])), indent=2))
