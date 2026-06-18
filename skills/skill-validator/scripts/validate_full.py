"""Full validation assembler: combine deterministic + behavioral signals into the scorecard.

The invoking agent (following SKILL.md) collects artifacts into a workspace —
``runs/`` with per-run grading.json (with_skill vs without_skill), plus optional
``artifact_judgment.json`` (D4) and ``triggering.json`` (D5). This module does the
deterministic final assembly: D1 static checks + D6 safety gate (computed here),
D2/D3 from aggregating the runs, D4/D5 from the judge artifacts, then score and
write the scorecard. Spawning subagents / running ``claude -p`` is the agent's job;
turning their outputs into a defensible number is this module's job.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import aggregate
import classify
import dimensions
import jsonutil
import resolve_skill
import safety_scan
import scorecard
import scoring
import static_checks


def _classify(skill_md, skill_dir, override=None) -> dict | None:
    """Compact skill-type classification for the scorecard (None if unreadable).

    ``override`` forces a type (confidence ``forced``) so the agent can pin the strategy.
    """
    if override:
        return {"type": override, "confidence": "forced", "also": []}
    try:
        r = classify.classify_skill(Path(skill_md).read_text(), skill_dir)
    except OSError:
        return None
    return {"type": r["type"], "confidence": r["confidence"], "also": r["also"]}


def _read_json(path: Path):
    # Lenient: agent-written artifacts often arrive fenced or prose-wrapped.
    return jsonutil.read_or(path, None)


def validate_full(skill_source: str, workspace: Path, out_dir: Path | None = None,
                  type_override: str | None = None) -> dict:
    workspace = Path(workspace)
    out_dir = Path(out_dir) if out_dir else workspace

    resolved = resolve_skill.resolve(skill_source, workspace / "resolved")
    skill_dir = resolved["skill_dir"]

    checks = static_checks.run_checks(skill_dir)
    safety = safety_scan.scan(skill_dir)
    dims: dict[str, float] = {"D1": static_checks.d1_score(checks)}
    detail: dict[str, dict] = {}

    bench_dir = workspace / "runs"
    agg = aggregate.aggregate(bench_dir) if bench_dir.exists() else None
    artifact = _read_json(workspace / "artifact_judgment.json")
    triggering = _read_json(workspace / "triggering.json")

    bdims, bdetail = dimensions.behavioral_dims(agg, artifact, triggering)
    dims.update(bdims)
    detail.update(bdetail)

    scoring_result = scoring.score_skill(dims, safety["safety_pass"])
    mode = "full" if bdims else "structural-only"

    sc = scorecard.build_scorecard(
        provenance=resolved["provenance"],
        scoring_result=scoring_result,
        d1_checks=checks,
        safety=safety,
        dimensions_detail=detail,
        metadata={
            "mode": mode,
            "skill_name": static_checks.skill_name(resolved["skill_md"]),
            "classification": _classify(resolved["skill_md"], skill_dir, type_override),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )
    scorecard.write_scorecard(sc, out_dir)
    return sc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="skval full validation: assemble D1-D6 into a scorecard from collected artifacts."
    )
    parser.add_argument("skill_source", help="skill directory, SKILL.md, or .skill/.zip")
    parser.add_argument("workspace", help="workspace dir with runs/ + artifact_judgment.json + triggering.json")
    parser.add_argument("--out", default=None, help="output dir (default: workspace)")
    parser.add_argument("--type", choices=classify.TYPES, default=None,
                        help="force the skill type (overrides auto-classification)")
    args = parser.parse_args(argv)

    sc = validate_full(args.skill_source, Path(args.workspace), Path(args.out) if args.out else None,
                       type_override=args.type)
    print(scorecard.render_markdown(sc))
    return 1 if sc["verdict"] == "Reject" else 0


if __name__ == "__main__":
    sys.exit(main())
