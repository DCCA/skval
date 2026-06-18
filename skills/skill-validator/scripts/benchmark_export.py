"""Export a skval workspace to a skill-creator-compatible ``benchmark.json``.

This lets the existing skill-creator ``eval-viewer`` render skval behavioral runs
for free. The schema (configuration ∈ {with_skill, without_skill}, nested ``result``,
``run_summary`` with mean/stddev + ``delta``) matches that project's references.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import stats


def _load(bench_dir: Path) -> dict[str, list[dict]]:
    bench_dir = Path(bench_dir)
    out: dict[str, list[dict]] = {}
    for eval_dir in sorted(bench_dir.glob("eval-*")):
        try:
            eval_id = int(eval_dir.name.split("-", 1)[1])
        except (ValueError, IndexError):
            eval_id = eval_dir.name
        for cfg_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir()):
            for run_dir in sorted(cfg_dir.glob("run-*")):
                gf = run_dir / "grading.json"
                if not gf.exists():
                    continue
                try:
                    s = json.loads(gf.read_text()).get("summary", {})
                except json.JSONDecodeError:
                    continue
                try:
                    run_number = int(run_dir.name.split("-", 1)[1])
                except (ValueError, IndexError):
                    run_number = 0
                out.setdefault(cfg_dir.name, []).append(
                    {
                        "eval_id": eval_id,
                        "run_number": run_number,
                        "pass_rate": s.get("pass_rate", 0.0),
                        "passed": s.get("passed", 0),
                        "failed": s.get("failed", 0),
                        "total": s.get("total", 0),
                    }
                )
    return out


def export_benchmark(bench_dir: Path, skill_name: str = "", executor_model: str = "") -> dict:
    loaded = _load(bench_dir)

    runs = []
    run_summary: dict[str, dict] = {}
    eval_ids = set()
    for cfg, rlist in loaded.items():
        for r in rlist:
            eval_ids.add(r["eval_id"])
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
                        "time_seconds": 0.0,
                        "tokens": 0,
                        "tool_calls": 0,
                        "errors": 0,
                    },
                    "expectations": [],
                    "notes": [],
                }
            )
        s = stats.summarize([r["pass_rate"] for r in rlist])
        zero = {"mean": 0, "stddev": 0, "min": 0, "max": 0}
        run_summary[cfg] = {
            "pass_rate": {"mean": s["mean"], "stddev": s["stddev"], "min": s["min"], "max": s["max"]},
            "time_seconds": dict(zero),
            "tokens": dict(zero),
        }

    if "with_skill" in run_summary and "without_skill" in run_summary:
        d = run_summary["with_skill"]["pass_rate"]["mean"] - run_summary["without_skill"]["pass_rate"]["mean"]
        run_summary["delta"] = {"pass_rate": f"{d:+.2f}", "time_seconds": "+0.0", "tokens": "+0"}

    return {
        "metadata": {
            "skill_name": skill_name or "<skill-name>",
            "executor_model": executor_model or "<model>",
            "analyzer_model": "<model>",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": sorted(eval_ids, key=str),
            "runs_per_configuration": max((len(v) for v in loaded.values()), default=0)
            // max(len(eval_ids), 1),
        },
        "runs": runs,
        "run_summary": run_summary,
        "notes": [],
    }


def write_benchmark(bench_dir: Path, out_path: Path, skill_name: str = "", executor_model: str = "") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(export_benchmark(bench_dir, skill_name, executor_model), indent=2))
    return out_path


if __name__ == "__main__":
    import sys

    p = write_benchmark(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "")
    print(f"wrote {p}")
