"""Assemble and render the skval Scorecard.

Turns the outputs of the scoring engine, D1 checks, and the D6 safety scan
(plus optional behavioral/judge detail from M1+) into a single ``scorecard.json``
and a human-readable ``scorecard.md`` (the PRD section 8 layout). Findings are
ranked by estimated score impact so the most valuable fix is on top.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path

_SEVERITY_IMPACT = {"critical": 3, "major": 2, "minor": 1}
_ALL_DIMS = ["D1", "D2", "D3", "D4", "D5"]


def _check_to_dict(c) -> dict:
    if is_dataclass(c):
        return asdict(c)
    if isinstance(c, dict):
        return c
    return {
        "id": getattr(c, "id", ""),
        "passed": getattr(c, "passed", None),
        "severity": getattr(c, "severity", ""),
        "detail": getattr(c, "detail", ""),
    }


def derive_findings(d1_checks, safety, dimensions_detail) -> list[dict]:
    """Build a list of {dimension, impact_estimate, message}, highest impact first."""
    findings: list[dict] = []

    for f in (safety or {}).get("findings", []):
        if f.get("severity") == "critical":
            findings.append(
                {
                    "dimension": "D6",
                    "impact_estimate": 100,
                    "message": f"Safety: {f['pattern']} in {f['file']}:{f['line']}",
                }
            )

    for c in d1_checks or []:
        cd = _check_to_dict(c)
        if not cd.get("passed"):
            findings.append(
                {
                    "dimension": "D1",
                    "impact_estimate": _SEVERITY_IMPACT.get(cd.get("severity"), 1),
                    "message": cd.get("detail") or cd.get("id"),
                }
            )

    for dim, detail in (dimensions_detail or {}).items():
        for msg in detail.get("findings", []):
            findings.append({"dimension": dim, "impact_estimate": 2, "message": msg})

    findings.sort(key=lambda x: x["impact_estimate"], reverse=True)
    return findings


def build_scorecard(
    *,
    provenance: dict,
    scoring_result: dict,
    d1_checks,
    safety: dict,
    dimensions_detail: dict | None = None,
    findings: list[dict] | None = None,
    metadata: dict | None = None,
) -> dict:
    dims = scoring_result.get("dims", {})
    weights = scoring_result.get("weights_used", {})

    dimensions: dict[str, dict] = {}
    for dim, val in dims.items():
        entry = {"score": val, "weight": weights.get(dim)}
        if dim == "D1":
            entry["checks"] = [_check_to_dict(c) for c in (d1_checks or [])]
        if dimensions_detail and dim in dimensions_detail:
            entry.update(dimensions_detail[dim])
        dimensions[dim] = entry

    metadata = dict(metadata or {})
    metadata.setdefault("skipped_dimensions", [d for d in _ALL_DIMS if d not in dims])

    fnd = findings if findings is not None else derive_findings(d1_checks, safety, dimensions_detail)
    cls = metadata.get("classification")
    if cls and cls.get("confidence") == "low":  # genuine type ambiguity — advisory, zero score impact
        also = f" vs {', '.join(cls.get('also', []))}" if cls.get("also") else ""
        fnd = list(fnd) + [{
            "dimension": "info",
            "impact_estimate": 0,
            "message": f"Ambiguous skill type ({cls.get('type')}{also}) — confirm before choosing the eval strategy",
        }]
        fnd.sort(key=lambda x: x["impact_estimate"], reverse=True)

    return {
        "score": scoring_result["score"],
        "grade": scoring_result["grade"],
        "verdict": scoring_result["verdict"],
        "safety_pass": scoring_result.get("safety_pass", safety.get("safety_pass", True)),
        "dimensions": dimensions,
        "safety": safety,
        "findings": fnd,
        "provenance": provenance,
        "metadata": metadata,
    }


def _bar(score: int, width: int = 14) -> str:
    filled = round(width * score / 100)
    return "█" * filled + "░" * (width - filled)


_DIM_NAMES = {
    "D1": "Structural",
    "D2": "Effectiveness",
    "D3": "Reliability",
    "D4": "Artifact quality",
    "D5": "Triggering",
}


def _dim_detail(dim: str, e: dict) -> str:
    if dim == "D1":
        checks = e.get("checks", [])
        failed = [c for c in checks if not c.get("passed")]
        if not checks:
            return ""
        return "all checks pass" if not failed else f"{len(failed)}/{len(checks)} checks failed"
    if dim == "D2":
        pr = e.get("pass_rate", {})
        s = f"pass {pr.get('mean', 0) * 100:.0f}% ± {pr.get('stddev', 0) * 100:.0f}%"
        lift = e.get("baseline_lift")
        if lift is not None:
            s += f", lift {lift * 100:+.0f}% ({'significant' if e.get('significant') else 'n.s.'})"
        return s
    if dim == "D3":
        ph = e.get("pass_hat_k", {})
        if not ph:
            return ""
        ks = sorted(ph, key=int)
        picks = (ks[0], ks[-1]) if len(ks) > 1 else (ks[0],)
        return "  ".join(f"pass^{k}={ph[k]:.2f}" for k in picks)
    if dim == "D4":
        crit = e.get("criteria", [])
        if not crit:
            return ""
        passed = sum(1 for c in crit if c.get("passed"))
        return f"{passed}/{len(crit)} rubric criteria"
    if dim == "D5":
        bits = [f"{label} {e[k]:.2f}" for k, label in (("f1", "F1"), ("precision", "P"), ("recall", "R")) if k in e]
        return ", ".join(bits)
    return ""


def render_markdown(sc: dict) -> str:
    name = sc["metadata"].get("skill_name") or Path(sc["provenance"].get("source", "skill")).name
    mode = sc["metadata"].get("mode", "full")
    lines = [
        f"# Skill Scorecard — `{name}`",
        f"Source: {sc['provenance'].get('source')} · mode: {mode}",
    ]
    cls = sc["metadata"].get("classification")
    if cls:
        tline = f"Type: {cls.get('type')} (confidence: {cls.get('confidence', '?')})"
        if cls.get("also"):
            tline += f" · also: {', '.join(cls['also'])}"
        if cls.get("confidence") == "low":
            tline += "  ⚠ confirm the type before choosing the eval strategy"
        lines.append(tline)
    lines += [
        "",
        f"## {_bar(sc['score'])}  {sc['score']} / 100   Grade: {sc['grade']}   Verdict: {sc['verdict']}",
        "",
        "| Dimension | Score | Weight | Detail |",
        "|-----------|-------|--------|--------|",
    ]
    for dim, entry in sc["dimensions"].items():
        w = entry.get("weight")
        wtxt = f"{w:.2f}" if isinstance(w, (int, float)) else "gate"
        name = _DIM_NAMES.get(dim, dim)
        lines.append(f"| {dim} {name} | {entry['score']:.2f} | {wtxt} | {_dim_detail(dim, entry)} |")

    safe = sc["safety"].get("safety_pass", True)
    lines += ["", f"Safety gate: {'PASS' if safe else 'FAIL (Reject)'}"]

    skipped = sc["metadata"].get("skipped_dimensions") or []
    if skipped:
        lines.append(f"Skipped dimensions ({mode}): {', '.join(skipped)}")

    if sc["findings"]:
        lines += ["", "## Top findings (ranked by score impact)"]
        for i, f in enumerate(sc["findings"], start=1):
            lines.append(f"{i}. [{f['dimension']}] {f['message']}")
    else:
        lines += ["", "No findings — clean."]

    return "\n".join(lines) + "\n"


def write_scorecard(sc: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "scorecard.json"
    md_path = out_dir / "scorecard.md"
    json_path.write_text(json.dumps(sc, indent=2, default=str))
    md_path.write_text(render_markdown(sc))
    return json_path, md_path
