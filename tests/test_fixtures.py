import json
import subprocess
import sys
from pathlib import Path

import eval_fixtures as fixtures

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "skill-validator" / "scripts"


def test_eval_files_filters_blanks():
    assert fixtures.eval_files({"files": ["a.csv", "", "  ", None, "b.pdf"]}) == ["a.csv", "b.pdf"]
    assert fixtures.eval_files({}) == []


def test_missing_fixtures(tmp_path):
    (tmp_path / "fixtures" / "eval-0").mkdir(parents=True)
    (tmp_path / "fixtures" / "eval-0" / "in.csv").write_text("x\n")
    evals = [
        {"id": 0, "files": ["fixtures/eval-0/in.csv"]},
        {"id": 1, "files": ["fixtures/eval-1/missing.xlsx"]},
    ]
    assert fixtures.missing_fixtures(evals, tmp_path) == [(1, "fixtures/eval-1/missing.xlsx")]


def test_stage_copies_into_run_dir(tmp_path):
    ws = tmp_path / "ws"
    (ws / "fixtures" / "eval-0").mkdir(parents=True)
    (ws / "fixtures" / "eval-0" / "report.csv").write_text("a,b\n1,2\n")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    staged = fixtures.stage({"id": 0, "files": ["fixtures/eval-0/report.csv"]}, ws, run_dir)
    assert staged == ["report.csv"]
    assert (run_dir / "inputs" / "report.csv").read_text() == "a,b\n1,2\n"


def test_stage_copies_directory_and_skips_missing(tmp_path):
    ws = tmp_path / "ws"
    d = ws / "fixtures" / "eval-0" / "assets"
    d.mkdir(parents=True)
    (d / "logo.txt").write_text("logo")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    staged = fixtures.stage(
        {"id": 0, "files": ["fixtures/eval-0/assets", "fixtures/eval-0/gone.bin"]}, ws, run_dir
    )
    assert staged == ["assets"]
    assert (run_dir / "inputs" / "assets" / "logo.txt").read_text() == "logo"


def test_stage_empty_is_noop(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    assert fixtures.stage({"id": 0, "files": []}, tmp_path, run_dir) == []
    assert not (run_dir / "inputs").exists()


def _run_check(workspace):
    return subprocess.run(
        [sys.executable, str(SCRIPT / "eval_fixtures.py"), "check", str(workspace)],
        text=True,
        capture_output=True,
    )


def test_check_cli_flags_missing_fixture(tmp_path):
    (tmp_path / "evals.json").write_text(
        json.dumps({"evals": [{"id": 0, "files": ["fixtures/eval-0/in.csv"]}]})
    )

    result = _run_check(tmp_path)

    assert result.returncode == 1
    assert "MISSING fixtures:" in result.stdout
    assert "eval 0: fixtures/eval-0/in.csv" in result.stdout


def test_check_cli_passes_when_all_present(tmp_path):
    (tmp_path / "fixtures" / "eval-0").mkdir(parents=True)
    (tmp_path / "fixtures" / "eval-0" / "in.csv").write_text("x\n")
    (tmp_path / "evals.json").write_text(
        json.dumps({"evals": [{"id": 0, "files": ["fixtures/eval-0/in.csv"]}]})
    )

    result = _run_check(tmp_path)

    assert result.returncode == 0
    assert "all referenced fixtures present" in result.stdout


def test_check_cli_passes_with_no_evals_file(tmp_path):
    # missing evals.json is read leniently as {} -> nothing referenced, nothing missing
    result = _run_check(tmp_path)

    assert result.returncode == 0
    assert "all referenced fixtures present" in result.stdout
