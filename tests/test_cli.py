import json
from pathlib import Path

import pytest

import skval_cli


FX = Path(__file__).parent / "fixtures"


def test_structural_command_scores_good_skill(tmp_path, capsys):
    rc = skval_cli.main(["structural", str(FX / "good-skill"), "--out", str(tmp_path / "out")])

    captured = capsys.readouterr()
    assert rc == 0
    assert "100 / 100" in captured.out
    assert json.loads((tmp_path / "out" / "scorecard.json").read_text())["verdict"] == "Ship"


def test_structural_command_reject_exits_1(tmp_path, capsys):
    rc = skval_cli.main(["structural", str(FX / "unsafe-skill"), "--out", str(tmp_path / "out")])

    captured = capsys.readouterr()
    assert rc == 1
    assert "Reject" in captured.out
    assert json.loads((tmp_path / "out" / "scorecard.json").read_text())["verdict"] == "Reject"


def test_structural_command_prints_friendly_missing_source_error(tmp_path, capsys):
    rc = skval_cli.main(["structural", str(tmp_path / "missing"), "--out", str(tmp_path / "out")])

    captured = capsys.readouterr()
    assert rc == 2
    assert "ERROR: skill source not found" in captured.err
    assert "Traceback" not in captured.err


def test_structural_command_prints_friendly_unsupported_remote_error(tmp_path, capsys):
    rc = skval_cli.main(
        ["structural", "https://github.com/example/skill.git", "--out", str(tmp_path / "out")]
    )

    captured = capsys.readouterr()
    assert rc == 2
    assert "ERROR:" in captured.err
    assert "remote" in captured.err.lower() or "git" in captured.err.lower()
    assert "Traceback" not in captured.err


def _mk_behavioral_workspace(tmp_path):
    """Workspace with runs/ + artifact_judgment.json + triggering.json for `full`."""
    ws = tmp_path / "ws"
    for r in (1, 2, 3):
        for cfg, pr in (("with_skill", 1.0), ("without_skill", 0.0)):
            rd = ws / "runs" / "eval-0" / cfg / f"run-{r}"
            rd.mkdir(parents=True)
            passed = int(pr * 2)
            (rd / "grading.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "pass_rate": pr,
                            "passed": passed,
                            "failed": 2 - passed,
                            "total": 2,
                        }
                    }
                )
            )
    (ws / "artifact_judgment.json").write_text(
        json.dumps({"criteria": [{"passed": True}, {"passed": True}]})
    )
    (ws / "triggering.json").write_text(json.dumps({"f1": 0.9, "precision": 0.92, "recall": 0.88}))
    return ws


def test_full_command_assembles_scorecard(tmp_path, capsys):
    ws = _mk_behavioral_workspace(tmp_path)
    out = tmp_path / "out"

    rc = skval_cli.main(["full", str(FX / "good-skill"), str(ws), "--out", str(out)])

    captured = capsys.readouterr()
    assert rc == 0
    assert "/ 100" in captured.out
    sc = json.loads((out / "scorecard.json").read_text())
    assert sc["metadata"]["mode"] == "full"
    assert set(sc["dimensions"]) == {"D1", "D2", "D3", "D4", "D5"}
    assert sc["verdict"] in ("Ship", "Revise")


def test_full_command_defaults_out_to_workspace(tmp_path, capsys):
    ws = _mk_behavioral_workspace(tmp_path)

    rc = skval_cli.main(["full", str(FX / "good-skill"), str(ws)])

    capsys.readouterr()
    assert rc == 0
    assert (ws / "scorecard.json").exists()


def test_full_command_prints_friendly_missing_source_error(tmp_path, capsys):
    ws = tmp_path / "ws"
    ws.mkdir()

    rc = skval_cli.main(["full", str(tmp_path / "missing"), str(ws)])

    captured = capsys.readouterr()
    assert rc == 2
    assert "ERROR:" in captured.err
    assert "Traceback" not in captured.err


def test_estimate_command_previews_without_writing(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)  # so a buggy write would land somewhere observable

    rc = skval_cli.main(["estimate", str(FX / "good-skill")])

    captured = capsys.readouterr()
    assert rc == 0
    assert "Cost estimate" in captured.out
    assert "$" in captured.out
    assert not (tmp_path / "skval-runs").exists()  # preview mode leaves no files behind


def test_estimate_command_write_produces_estimate_json(tmp_path, capsys):
    out = tmp_path / "est"

    rc = skval_cli.main(
        [
            "estimate",
            str(FX / "good-skill"),
            "--write",
            "--out",
            str(out),
            "--evals",
            "2",
            "--trials",
            "2",
        ]
    )

    captured = capsys.readouterr()
    assert rc == 0
    assert "wrote" in captured.err
    est = json.loads((out / "estimate.json").read_text())
    assert est["plan"]["evals"] == 2
    assert est["plan"]["trials"] == 2
    assert est["totals"]["tokens"]["expected"] > 0
    assert est["totals"]["cost_usd"]["expected"] > 0


def test_estimate_command_prints_friendly_missing_source_error(tmp_path, capsys):
    rc = skval_cli.main(["estimate", str(tmp_path / "missing")])

    captured = capsys.readouterr()
    assert rc == 2
    assert "ERROR:" in captured.err
    assert "Traceback" not in captured.err


def test_benchmark_export_help_and_command(tmp_path, capsys):
    runs = tmp_path / "runs" / "eval-0" / "with_skill" / "run-1"
    runs.mkdir(parents=True)
    (runs / "grading.json").write_text(
        json.dumps({"summary": {"pass_rate": 1.0, "passed": 1, "failed": 0, "total": 1}})
    )
    out = tmp_path / "benchmark.json"

    with pytest.raises(SystemExit) as exc:
        skval_cli.main(["benchmark-export", "--help"])
    assert exc.value.code == 0
    assert "usage:" in capsys.readouterr().out

    rc = skval_cli.main(
        ["benchmark-export", str(tmp_path / "runs"), str(out), "--skill-name", "demo"]
    )
    captured = capsys.readouterr()
    assert rc == 0
    assert "wrote" in captured.out
    assert json.loads(out.read_text())["metadata"]["skill_name"] == "demo"


def test_batch_command_ranks_scorecards(tmp_path, capsys):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(
        json.dumps(
            {"score": 70, "grade": "C", "verdict": "Revise", "metadata": {"skill_name": "alpha"}}
        )
    )
    b.write_text(
        json.dumps(
            {"score": 95, "grade": "A", "verdict": "Ship", "metadata": {"skill_name": "beta"}}
        )
    )

    rc = skval_cli.main(["batch", str(a), str(b)])

    captured = capsys.readouterr()
    assert rc == 0
    assert "| 1 | beta | 95 | A | Ship |" in captured.out


def test_compare_command_diffs_scorecards(tmp_path, capsys):
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text(
        json.dumps(
            {"score": 70, "grade": "C", "verdict": "Revise", "dimensions": {"D1": {"score": 0.7}}}
        )
    )
    new.write_text(
        json.dumps(
            {"score": 90, "grade": "A", "verdict": "Ship", "dimensions": {"D1": {"score": 1.0}}}
        )
    )

    rc = skval_cli.main(["compare", str(old), str(new)])

    captured = capsys.readouterr()
    assert rc == 0
    assert '"overall_delta": 20' in captured.out
    assert '"D1"' in captured.out
