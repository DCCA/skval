"""Shared loader for behavioral run directories.

One place that knows the on-disk layout ``eval-<id>/<config>/run-<k>/`` so
``aggregate`` and ``benchmark_export`` can't drift. Reads each run's
``grading.json`` summary and, when present, the executor's optional
``outputs/metrics.json`` and ``timing.json`` so tool/latency/token data flows
through to the benchmark export instead of being silently dropped.
"""

from __future__ import annotations

from pathlib import Path

import jsonutil


def load_runs(bench_dir: Path) -> dict[str, list[dict]]:
    """Return {config: [run, ...]}. Each run carries eval_id, run_number, the
    grading summary (pass_rate/passed/failed/total), and time/tokens/tool_calls/
    errors (0 when the optional metrics/timing files are absent)."""
    bench_dir = Path(bench_dir)
    out: dict[str, list[dict]] = {}
    for eval_dir in sorted(bench_dir.glob("eval-*")):
        try:
            eval_id: object = int(eval_dir.name.split("-", 1)[1])
        except (ValueError, IndexError):
            eval_id = eval_dir.name
        for cfg_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir()):
            for run_dir in sorted(cfg_dir.glob("run-*")):
                gf = run_dir / "grading.json"
                if not gf.exists():
                    continue
                data = jsonutil.read_or(gf)
                if data is None:
                    continue
                summary = data.get("summary", {})
                try:
                    run_number = int(run_dir.name.split("-", 1)[1])
                except (ValueError, IndexError):
                    run_number = 0
                run = {
                    "eval_id": eval_id,
                    "run_number": run_number,
                    "pass_rate": summary.get("pass_rate", 0.0),
                    "passed": summary.get("passed", 0),
                    "failed": summary.get("failed", 0),
                    "total": summary.get("total", 0),
                    "time_seconds": 0.0,
                    "tokens": 0,
                    "tool_calls": 0,
                    "errors": 0,
                }
                _merge_optional(run, run_dir / "outputs" / "metrics.json", {"total_tool_calls": "tool_calls", "errors_encountered": "errors"})
                _merge_optional(run, run_dir / "timing.json", {"total_duration_seconds": "time_seconds", "total_tokens": "tokens"})
                out.setdefault(cfg_dir.name, []).append(run)
    return out


def _merge_optional(run: dict, path: Path, mapping: dict[str, str]) -> None:
    data = jsonutil.read_or(path)
    if not isinstance(data, dict):
        return
    for src, dst in mapping.items():
        if src in data:
            run[dst] = data[src]
