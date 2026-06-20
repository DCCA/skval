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
