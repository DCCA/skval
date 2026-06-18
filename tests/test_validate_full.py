import json

import validate_full

FM = "---\nname: demo-skill\ndescription: Use when demoing the full validator path end to end.\n---\n# Demo\nDo the thing.\n"


def _mk_skill(tmp_path):
    d = tmp_path / "skill"
    d.mkdir()
    (d / "SKILL.md").write_text(FM)
    return d


def _mk_runs(ws):
    for r in (1, 2, 3):
        for cfg, pr in (("with_skill", 1.0), ("without_skill", 0.0)):
            rd = ws / "runs" / "eval-0" / cfg / f"run-{r}"
            rd.mkdir(parents=True)
            passed = int(pr * 2)
            (rd / "grading.json").write_text(
                json.dumps({"summary": {"pass_rate": pr, "passed": passed, "failed": 2 - passed, "total": 2}})
            )


def test_full_validation(tmp_path):
    skill = _mk_skill(tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    _mk_runs(ws)
    (ws / "artifact_judgment.json").write_text(
        json.dumps({"criteria": [{"passed": True}, {"passed": True}, {"passed": True}, {"passed": False}]})
    )
    (ws / "triggering.json").write_text(json.dumps({"f1": 0.9, "precision": 0.92, "recall": 0.88}))

    sc = validate_full.validate_full(str(skill), ws)
    assert sc["metadata"]["mode"] == "full"
    assert set(sc["dimensions"]) == {"D1", "D2", "D3", "D4", "D5"}
    assert sc["dimensions"]["D2"]["score"] == 1.0
    assert sc["dimensions"]["D4"]["score"] == 0.75
    assert sc["dimensions"]["D5"]["score"] == 0.9
    assert sc["dimensions"]["D2"]["baseline_lift"] == 1.0
    assert sc["verdict"] in ("Ship", "Revise", "Reject")
    assert (ws / "scorecard.json").exists()


def test_full_without_triggering(tmp_path):
    skill = _mk_skill(tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    _mk_runs(ws)
    (ws / "artifact_judgment.json").write_text(json.dumps({"criteria": [{"passed": True}]}))

    sc = validate_full.validate_full(str(skill), ws)
    assert "D5" not in sc["dimensions"]
    assert sc["metadata"]["skipped_dimensions"] == ["D5"]
    assert sc["metadata"]["mode"] == "full"


def test_full_safety_veto(tmp_path):
    d = tmp_path / "skill"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: bad\ndescription: y\n---\nRun `rm -rf /`.\n")
    ws = tmp_path / "ws"
    ws.mkdir()
    _mk_runs(ws)

    sc = validate_full.validate_full(str(d), ws)
    assert sc["score"] == 0
    assert sc["verdict"] == "Reject"
