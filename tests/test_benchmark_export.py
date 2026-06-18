import json

import benchmark_export


def _grading(pass_rate, total=2):
    passed = round(pass_rate * total)
    return {"summary": {"pass_rate": pass_rate, "passed": passed, "failed": total - passed, "total": total}}


def _mk(base, eval_id, cfg, run, pr):
    d = base / f"eval-{eval_id}" / cfg / f"run-{run}"
    d.mkdir(parents=True)
    (d / "grading.json").write_text(json.dumps(_grading(pr)))


def test_export_schema(tmp_path):
    runs = tmp_path / "runs"
    for r in (1, 2):
        _mk(runs, 0, "with_skill", r, 1.0)
        _mk(runs, 0, "without_skill", r, 0.0)
    bench = benchmark_export.export_benchmark(runs, skill_name="demo")
    assert bench["metadata"]["skill_name"] == "demo"
    assert len(bench["runs"]) == 4
    assert {r["configuration"] for r in bench["runs"]} == {"with_skill", "without_skill"}
    assert bench["run_summary"]["with_skill"]["pass_rate"]["mean"] == 1.0
    assert bench["run_summary"]["delta"]["pass_rate"] == "+1.00"
    # every run carries the nested result shape the viewer expects
    sample = bench["runs"][0]
    assert {"eval_id", "configuration", "run_number", "result"} <= set(sample)
    assert "pass_rate" in sample["result"]


def test_export_writes_file(tmp_path):
    runs = tmp_path / "runs"
    _mk(runs, 0, "with_skill", 1, 1.0)
    out = benchmark_export.write_benchmark(runs, tmp_path / "benchmark.json", skill_name="demo")
    assert out.exists()
    assert json.loads(out.read_text())["metadata"]["skill_name"] == "demo"
