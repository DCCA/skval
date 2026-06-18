import history


def _sc(score, grade, verdict, d2=0.8):
    return {"score": score, "grade": grade, "verdict": verdict,
            "metadata": {"skill_name": "demo"},
            "dimensions": {"D1": {"score": 1.0}, "D2": {"score": d2}}}


def test_append_run(tmp_path):
    p = tmp_path / "history.json"
    h = history.append_run(p, _sc(90, "A", "Ship"))
    h = history.append_run(p, _sc(80, "B", "Ship"))
    assert len(h["entries"]) == 2
    assert h["entries"][-1]["score"] == 80
    assert p.exists()


def test_detect_regression(tmp_path):
    p = tmp_path / "history.json"
    history.append_run(p, _sc(90, "A", "Ship", d2=0.9))
    h = history.append_run(p, _sc(80, "B", "Ship", d2=0.6))
    reg = history.detect_regression(h)
    assert reg["regressed"] is True
    assert reg["delta"] == -10
    assert "D2" in reg["regressed_dims"]


def test_no_regression_on_improvement(tmp_path):
    p = tmp_path / "history.json"
    history.append_run(p, _sc(80, "B", "Ship"))
    h = history.append_run(p, _sc(92, "A", "Ship"))
    reg = history.detect_regression(h)
    assert reg["regressed"] is False


def test_regression_none_for_single_entry(tmp_path):
    p = tmp_path / "history.json"
    h = history.append_run(p, _sc(80, "B", "Ship"))
    assert history.detect_regression(h) is None
