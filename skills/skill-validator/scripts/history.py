"""Track a skill's scores over time and flag regressions.

Appends a compact summary of each scorecard to a ``history.json`` and compares the
latest run to the best previous run, so an edit that lowers the score (overall or on
any dimension) is caught.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _summary(sc: dict) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "score": sc["score"],
        "grade": sc["grade"],
        "verdict": sc["verdict"],
        "dims": {d: e.get("score") for d, e in sc.get("dimensions", {}).items()},
    }


def append_run(history_path: Path, scorecard: dict) -> dict:
    p = Path(history_path)
    if p.exists():
        h = json.loads(p.read_text())
    else:
        h = {"skill_name": scorecard.get("metadata", {}).get("skill_name"), "entries": []}
    h["entries"].append(_summary(scorecard))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(h, indent=2))
    return h


def detect_regression(history: dict) -> dict | None:
    entries = history.get("entries", [])
    if len(entries) < 2:
        return None
    current = entries[-1]
    best_prior = max(entries[:-1], key=lambda e: e["score"])
    delta = current["score"] - best_prior["score"]
    regressed_dims = [
        d
        for d, v in current["dims"].items()
        if best_prior["dims"].get(d) is not None and v is not None and v < best_prior["dims"][d]
    ]
    return {
        "regressed": bool(delta < 0),
        "delta": delta,
        "current": current,
        "prev_best": best_prior,
        "regressed_dims": regressed_dims,
    }
