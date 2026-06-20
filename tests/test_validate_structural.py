from pathlib import Path

import validate_structural as v

FX = Path(__file__).parent / "fixtures"


def test_good_skill_scores_well(tmp_path):
    sc = v.validate_structural(str(FX / "good-skill"), tmp_path)
    assert sc["dimensions"]["D1"]["score"] > 0.9
    assert sc["metadata"]["mode"] == "structural-only"
    assert sc["verdict"] != "Reject"
    assert (tmp_path / "scorecard.json").exists()
    assert (tmp_path / "scorecard.md").exists()


def test_bad_skill_flags_findings(tmp_path):
    sc = v.validate_structural(str(FX / "bad-skill"), tmp_path)
    assert sc["dimensions"]["D1"]["score"] < 0.9
    assert len(sc["findings"]) >= 2


def test_unsafe_skill_is_rejected(tmp_path):
    sc = v.validate_structural(str(FX / "unsafe-skill"), tmp_path)
    assert sc["verdict"] == "Reject"
    assert sc["score"] == 0


def test_skill_name_recorded(tmp_path):
    sc = v.validate_structural(str(FX / "good-skill"), tmp_path)
    assert sc["metadata"]["skill_name"] == "good-skill"


def test_classification_recorded(tmp_path):
    sc = v.validate_structural(str(FX / "good-skill"), tmp_path)
    assert sc["metadata"]["classification"]["type"] in (
        "task",
        "file_transform",
        "interactive",
        "discipline",
        "reference",
    )


def test_type_override(tmp_path):
    sc = v.validate_structural(str(FX / "good-skill"), tmp_path, type_override="interactive")
    assert sc["metadata"]["classification"] == {
        "type": "interactive",
        "confidence": "forced",
        "also": [],
    }
    assert "Type: interactive (confidence: forced)" in __import__("scorecard").render_markdown(sc)
