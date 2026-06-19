"""Export a skval workspace to a skill-creator-compatible ``benchmark.json``.

Lets the existing skill-creator ``eval-viewer`` render skval behavioral runs. The
schema (configuration ∈ {with_skill, without_skill}, nested ``result``,
``run_summary`` with mean/stddev + ``delta``) matches that project's references.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import runs_io
import stats


def _summ(values):
    s = stats.summarize(values)
    return {"mean": s["mean"], "stddev": s["stddev"], "min": s["min"], "max": s["max"]}


def export_benchmark(bench_dir, skill_name: str = "", executor_model: str = "") -> dict:
    loaded = runs_io.load_runs(bench_dir)

    runs = []
    run_summary: dict[str, dict] = {}
    eval_ids = set()
    runs_per_config = 0  # max runs in any single (config, eval) bucket — i.e. N

    for cfg, rlist in loaded.items():
        per_eval: dict = {}
        for r in rlist:
            eval_ids.add(r["eval_id"])
            per_eval[r["eval_id"]] = per_eval.get(r["eval_id"], 0) + 1
            runs.append(
                {
                    "eval_id": r["eval_id"],
                    "configuration": cfg,
                    "run_number": r["run_number"],
                    "result": {
                        "pass_rate": r["pass_rate"],
                        "passed": r["passed"],
                        "failed": r["failed"],
                        "total": r["total"],
                        "time_seconds": r["time_seconds"],
                        "tokens": r["tokens"],
                        "tool_calls": r["tool_calls"],
                        "errors": r["errors"],
                    },
                    "expectations": [],
                    "notes": [],
                }
            )
        if per_eval:
            runs_per_config = max(runs_per_config, max(per_eval.values()))
        run_summary[cfg] = {
            "pass_rate": _summ([r["pass_rate"] for r in rlist]),
            "time_seconds": _summ([r["time_seconds"] for r in rlist]),
            "tokens": _summ([r["tokens"] for r in rlist]),
        }

    if "with_skill" in run_summary and "without_skill" in run_summary:
        w, b = run_summary["with_skill"], run_summary["without_skill"]
        run_summary["delta"] = {
            "pass_rate": f"{w['pass_rate']['mean'] - b['pass_rate']['mean']:+.2f}",
            "time_seconds": f"{w['time_seconds']['mean'] - b['time_seconds']['mean']:+.1f}",
            "tokens": f"{w['tokens']['mean'] - b['tokens']['mean']:+.0f}",
        }

    return {
        "metadata": {
            "skill_name": skill_name or "<skill-name>",
            "executor_model": executor_model or "<model>",
            "analyzer_model": "<model>",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": sorted(eval_ids, key=str),
            "runs_per_configuration": runs_per_config,
        },
        "runs": runs,
        "run_summary": run_summary,
        "notes": [],
    }


def write_benchmark(bench_dir, out_path, skill_name: str = "", executor_model: str = "") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(export_benchmark(bench_dir, skill_name, executor_model), indent=2))
    return out_path


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Export a skval runs directory to skill-creator eval-viewer benchmark.json format."
    )
    parser.add_argument("runs_dir", help="workspace runs/ directory")
    parser.add_argument("out_path", help="output benchmark.json path")
    parser.add_argument("--skill-name", default="", help="skill name to store in benchmark metadata")
    parser.add_argument("--executor-model", default="", help="executor model to store in benchmark metadata")
    args = parser.parse_args(argv)

    p = write_benchmark(args.runs_dir, args.out_path, args.skill_name, args.executor_model)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
