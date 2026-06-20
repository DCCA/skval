"""M0 entry point: the structural-only validation path (no model calls).

resolve -> D1 static checks -> D6 safety gate -> score (D1 only) -> scorecard.
This is the deterministic floor of skval; M1 adds behavioral (D2), artifact
judging (D4), reliability (D3), and triggering (D5) on top of the same engine.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import classify
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


def validate_structural(source: str, out_dir: Path, type_override: str | None = None) -> dict:
    out_dir = Path(out_dir)
    resolved = resolve_skill.resolve(source, out_dir / "resolved")
    skill_dir = resolved["skill_dir"]

    checks = static_checks.run_checks(skill_dir)
    d1 = static_checks.d1_score(checks)
    safety = safety_scan.scan(skill_dir)

    scoring_result = scoring.score_skill({"D1": d1}, safety["safety_pass"])

    sc = scorecard.build_scorecard(
        provenance=resolved["provenance"],
        scoring_result=scoring_result,
        d1_checks=checks,
        safety=safety,
        metadata={
            "mode": "structural-only",
            "skill_name": static_checks.skill_name(resolved["skill_md"]),
            "classification": _classify(resolved["skill_md"], skill_dir, type_override),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )
    scorecard.write_scorecard(sc, out_dir)
    return sc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="skval structural-only validation (M0): score a skill's structure and safety."
    )
    parser.add_argument("source", help="skill directory, SKILL.md file, or .skill/.zip archive")
    parser.add_argument(
        "--out", default="skval-runs/latest", help="output directory for the scorecard"
    )
    parser.add_argument(
        "--type",
        choices=classify.TYPES,
        default=None,
        help="force the skill type (overrides auto-classification)",
    )
    args = parser.parse_args(argv)

    try:
        sc = validate_structural(args.source, Path(args.out), type_override=args.type)
    except (FileNotFoundError, ValueError, NotImplementedError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(scorecard.render_markdown(sc))
    return 1 if sc["verdict"] == "Reject" else 0


if __name__ == "__main__":
    sys.exit(main())
