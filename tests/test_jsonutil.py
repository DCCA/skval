"""Lenient JSON loading + the fenced-artifact gap found by real-skill dogfooding."""

import json

import jsonutil
import runs_io


def test_loads_plain():
    assert jsonutil.loads_lenient('{"a": 1}') == {"a": 1}
    assert jsonutil.loads_lenient("[1, 2, 3]") == [1, 2, 3]


def test_loads_code_fence():
    assert jsonutil.loads_lenient('```json\n{"a": 1}\n```') == {"a": 1}
    assert jsonutil.loads_lenient('```\n{"a": 1}\n```') == {"a": 1}


def test_loads_prose_then_fence():
    raw = 'Here is the grading result:\n\n```json\n{"summary": {"pass_rate": 1.0}}\n```'
    assert jsonutil.loads_lenient(raw) == {"summary": {"pass_rate": 1.0}}


def test_loads_prose_then_bare_object():
    raw = (
        'I need write permission. Here it is directly:\n{"criteria": [{"id": "x", "passed": true}]}'
    )
    assert jsonutil.loads_lenient(raw)["criteria"][0]["passed"] is True


def test_loads_raises_on_garbage():
    for bad in ("", "no json here", "   "):
        try:
            jsonutil.loads_lenient(bad)
            assert False, bad
        except ValueError:
            pass


def test_read_or_missing_and_fenced(tmp_path):
    assert jsonutil.read_or(tmp_path / "nope.json", {"d": 1}) == {"d": 1}
    p = tmp_path / "a.json"
    p.write_text('```json\n{"ok": true}\n```')
    assert jsonutil.read_or(p) == {"ok": True}


def test_runs_io_tolerates_fenced_grading(tmp_path):
    # The exact failure mode: a subagent wrote fenced JSON -> run was silently dropped.
    d = tmp_path / "eval-0" / "with_skill" / "run-1"
    d.mkdir(parents=True)
    (d / "grading.json").write_text(
        "```json\n"
        + json.dumps({"summary": {"pass_rate": 1.0, "passed": 3, "failed": 0, "total": 3}})
        + "\n```"
    )
    runs = runs_io.load_runs(tmp_path)
    assert "with_skill" in runs
    assert runs["with_skill"][0]["pass_rate"] == 1.0
