"""Stage eval input fixtures into executor run directories.

File-transform skills (pdf, xlsx, docx, ...) only show their effect on a real input
file. The eval-generator writes fixtures under ``workspace/fixtures/`` and lists them
(workspace-relative) in each eval's ``files``; before running the task the executor
stages them into ``run_dir/inputs/`` so the deliverable has something to act on.

- ``missing_fixtures`` — pre-flight: which referenced fixtures don't exist.
- ``stage`` — copy an eval's fixtures into a run's ``inputs/`` dir.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def eval_files(eval_obj: dict) -> list[str]:
    """The non-blank file references declared by an eval."""
    return [f for f in (eval_obj.get("files") or []) if isinstance(f, str) and f.strip()]


def missing_fixtures(evals: list[dict], workspace) -> list[tuple]:
    """Return (eval_id, path) for every referenced fixture missing under ``workspace``."""
    ws = Path(workspace)
    missing = []
    for ev in evals:
        for f in eval_files(ev):
            if not (ws / f).exists():
                missing.append((ev.get("id"), f))
    return missing


def stage(eval_obj: dict, workspace, run_dir) -> list[str]:
    """Copy an eval's fixtures into ``run_dir/inputs/``; return staged basenames.

    Missing sources are skipped — run ``missing_fixtures`` first for a hard pre-flight.
    """
    ws = Path(workspace)
    inputs = Path(run_dir) / "inputs"
    staged = []
    for f in eval_files(eval_obj):
        src = ws / f
        if not src.exists():
            continue
        inputs.mkdir(parents=True, exist_ok=True)
        dest = inputs / src.name
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)
        staged.append(src.name)
    return staged


if __name__ == "__main__":  # pre-flight: python eval_fixtures.py check <workspace>
    import jsonutil

    if len(sys.argv) >= 3 and sys.argv[1] == "check":
        ws = Path(sys.argv[2])
        data = jsonutil.read_or(ws / "evals.json", {}) or {}
        miss = missing_fixtures(data.get("evals", []), ws)
        if miss:
            print("MISSING fixtures:")
            for eid, f in miss:
                print(f"  eval {eid}: {f}")
            sys.exit(1)
        print("all referenced fixtures present")
