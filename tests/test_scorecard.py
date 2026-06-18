import json
from pathlib import Path

import scorecard
from static_checks import Check


def _scoring_result():
    return {
        "score": 78,
        "grade": "C",
        "verdict": "Revise",
        "dims": {"D1": 0.75},
        "weights_used": {"D1": 0.15},
        "safety_pass": True,
    }


def test_build_and_render(tmp_path):
    sc = scorecard.build_scorecard(
        provenance={"source": "x", "kind": "dir"},
        scoring_result=_scoring_result(),
        d1_checks=[],
        safety={"safety_pass": True, "findings": []},
    )
    assert sc["score"] == 78
    assert sc["grade"] == "C"
    assert sc["verdict"] == "Revise"
    assert "D1" in sc["dimensions"]

    md = scorecard.render_markdown(sc)
    assert "78" in md and "Revise" in md

    j, m = scorecard.write_scorecard(sc, tmp_path)
    assert json.loads(Path(j).read_text())["grade"] == "C"
    assert Path(m).exists()


def test_render_shows_classification():
    sc = scorecard.build_scorecard(
        provenance={"source": "x", "kind": "dir"},
        scoring_result=_scoring_result(),
        d1_checks=[],
        safety={"safety_pass": True, "findings": []},
        metadata={"classification": {"type": "interactive", "confidence": "high", "also": ["file_transform"]}},
    )
    md = scorecard.render_markdown(sc)
    assert "Type: interactive (confidence: high)" in md
    assert "also: file_transform" in md


def test_render_flags_low_confidence():
    sc = scorecard.build_scorecard(
        provenance={"source": "x", "kind": "dir"},
        scoring_result=_scoring_result(),
        d1_checks=[],
        safety={"safety_pass": True, "findings": []},
        metadata={"classification": {"type": "task", "confidence": "low", "also": []}},
    )
    assert "⚠ confirm the type" in scorecard.render_markdown(sc)


def test_findings_from_failed_checks():
    checks = [
        Check("name_kebab_case", False, "major", "name 'Bad_Name' must be kebab-case"),
        Check("frontmatter_present", True, "critical", ""),
    ]
    findings = scorecard.derive_findings(checks, {"safety_pass": True, "findings": []}, None)
    assert len(findings) == 1
    assert findings[0]["dimension"] == "D1"


def test_safety_finding_ranks_first():
    safety = {
        "safety_pass": False,
        "findings": [{"pattern": "fork bomb", "severity": "critical", "file": "SKILL.md", "line": 9, "excerpt": ":(){...}"}],
    }
    checks = [Check("token_budget", False, "minor", "too big")]
    findings = scorecard.derive_findings(checks, safety, None)
    assert findings[0]["dimension"] == "D6"  # safety veto ranks above a minor D1 nit
