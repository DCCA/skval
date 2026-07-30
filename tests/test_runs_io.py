import json

import runs_io


def _grading(pass_rate=1.0, total=2):
    passed = round(pass_rate * total)
    return {
        "summary": {
            "pass_rate": pass_rate,
            "passed": passed,
            "failed": total - passed,
            "total": total,
        }
    }


def _mk_run(base, eval_id, config, run, grading_text=None):
    d = base / f"eval-{eval_id}" / config / f"run-{run}"
    d.mkdir(parents=True)
    if grading_text is not None:
        (d / "grading.json").write_text(grading_text)
    return d


def test_load_runs_groups_by_config(tmp_path):
    for r in (1, 2):
        _mk_run(tmp_path, 0, "with_skill", r, json.dumps(_grading(1.0)))
    _mk_run(tmp_path, 0, "without_skill", 1, json.dumps(_grading(0.5)))

    runs = runs_io.load_runs(tmp_path)

    assert set(runs) == {"with_skill", "without_skill"}
    assert [(r["eval_id"], r["run_number"]) for r in runs["with_skill"]] == [(0, 1), (0, 2)]
    baseline = runs["without_skill"][0]
    assert baseline["pass_rate"] == 0.5
    assert baseline["passed"] == 1
    assert baseline["failed"] == 1
    assert baseline["total"] == 2
    # optional metrics/timing files absent -> zero defaults
    assert baseline["time_seconds"] == 0.0
    assert baseline["tokens"] == 0
    assert baseline["tool_calls"] == 0
    assert baseline["errors"] == 0


def test_load_runs_collects_across_evals(tmp_path):
    _mk_run(tmp_path, 0, "with_skill", 1, json.dumps(_grading(1.0)))
    _mk_run(tmp_path, 1, "with_skill", 1, json.dumps(_grading(0.0)))

    runs = runs_io.load_runs(tmp_path)

    assert [(r["eval_id"], r["run_number"]) for r in runs["with_skill"]] == [(0, 1), (1, 1)]


def test_load_runs_merges_metrics_and_timing(tmp_path):
    d = _mk_run(tmp_path, 0, "with_skill", 1, json.dumps(_grading(1.0)))
    (d / "outputs").mkdir()
    (d / "outputs" / "metrics.json").write_text(
        json.dumps({"total_tool_calls": 7, "errors_encountered": 2})
    )
    (d / "timing.json").write_text(
        json.dumps({"total_duration_seconds": 12.5, "total_tokens": 3400})
    )

    run = runs_io.load_runs(tmp_path)["with_skill"][0]

    assert run["tool_calls"] == 7
    assert run["errors"] == 2
    assert run["time_seconds"] == 12.5
    assert run["tokens"] == 3400
    # grading summary untouched by the merge
    assert run["pass_rate"] == 1.0


def test_load_runs_merges_partial_optional_files(tmp_path):
    d = _mk_run(tmp_path, 0, "with_skill", 1, json.dumps(_grading(1.0)))
    (d / "outputs").mkdir()
    (d / "outputs" / "metrics.json").write_text(json.dumps({"total_tool_calls": 3}))

    run = runs_io.load_runs(tmp_path)["with_skill"][0]

    assert run["tool_calls"] == 3
    assert run["errors"] == 0  # unmapped key keeps its default
    assert run["time_seconds"] == 0.0  # timing.json absent entirely


def test_load_runs_ignores_malformed_optional_files(tmp_path):
    d = _mk_run(tmp_path, 0, "with_skill", 1, json.dumps(_grading(1.0)))
    (d / "outputs").mkdir()
    (d / "outputs" / "metrics.json").write_text("[1, 2, 3]")  # parseable but not a dict
    (d / "timing.json").write_text("not json at all {{{")

    run = runs_io.load_runs(tmp_path)["with_skill"][0]

    assert run["tool_calls"] == 0
    assert run["errors"] == 0
    assert run["time_seconds"] == 0.0
    assert run["tokens"] == 0


def test_load_runs_reads_fenced_grading_json(tmp_path):
    # agent-written grading.json commonly arrives wrapped in prose + a code fence;
    # the lenient jsonutil path must still recover it.
    fenced = "Here is the grading result:\n```json\n" + json.dumps(_grading(0.5)) + "\n```\n"
    _mk_run(tmp_path, 0, "with_skill", 1, fenced)

    runs = runs_io.load_runs(tmp_path)

    assert runs["with_skill"][0]["pass_rate"] == 0.5
    assert runs["with_skill"][0]["passed"] == 1


def test_load_runs_skips_run_without_grading(tmp_path):
    _mk_run(tmp_path, 0, "with_skill", 1, json.dumps(_grading(1.0)))
    _mk_run(tmp_path, 0, "with_skill", 2, grading_text=None)  # no grading.json

    runs = runs_io.load_runs(tmp_path)

    assert [r["run_number"] for r in runs["with_skill"]] == [1]


def test_load_runs_skips_unparseable_grading(tmp_path):
    _mk_run(tmp_path, 0, "with_skill", 1, "totally not json")
    _mk_run(tmp_path, 0, "with_skill", 2, json.dumps(_grading(1.0)))

    runs = runs_io.load_runs(tmp_path)

    assert [r["run_number"] for r in runs["with_skill"]] == [2]


def test_load_runs_defaults_when_summary_absent(tmp_path):
    _mk_run(tmp_path, 0, "with_skill", 1, json.dumps({"results": []}))

    run = runs_io.load_runs(tmp_path)["with_skill"][0]

    assert run["pass_rate"] == 0.0
    assert run["passed"] == 0
    assert run["failed"] == 0
    assert run["total"] == 0


def test_load_runs_non_numeric_names(tmp_path):
    _mk_run(tmp_path, "smoke", "with_skill", "final", json.dumps(_grading(1.0)))

    run = runs_io.load_runs(tmp_path)["with_skill"][0]

    assert run["eval_id"] == "eval-smoke"  # falls back to the directory name
    assert run["run_number"] == 0


def test_load_runs_empty_and_missing_dir(tmp_path):
    assert runs_io.load_runs(tmp_path) == {}
    assert runs_io.load_runs(tmp_path / "does-not-exist") == {}


def test_load_runs_ignores_stray_files_inside_tree(tmp_path):
    _mk_run(tmp_path, 0, "with_skill", 1, json.dumps(_grading(1.0)))
    # a file next to the config dirs must not be treated as a config
    (tmp_path / "eval-0" / "notes.txt").write_text("scratch")
    # a file matching run-* has no grading.json underneath and is skipped
    (tmp_path / "eval-0" / "with_skill" / "run-log.txt").write_text("log")

    runs = runs_io.load_runs(tmp_path)

    assert set(runs) == {"with_skill"}
    assert [r["run_number"] for r in runs["with_skill"]] == [1]


def test_load_runs_accepts_str_path(tmp_path):
    _mk_run(tmp_path, 0, "with_skill", 1, json.dumps(_grading(1.0)))

    runs = runs_io.load_runs(str(tmp_path))

    assert runs["with_skill"][0]["eval_id"] == 0


def test_load_runs_ignores_plain_file_matching_eval_glob(tmp_path):
    # A stray FILE named eval-* in the bench dir must be skipped, not iterated.
    _mk_run(tmp_path, 0, "with_skill", 1, json.dumps(_grading(1.0)))
    (tmp_path / "eval-notes.txt").write_text("scratch")
    runs = runs_io.load_runs(tmp_path)
    assert len(runs["with_skill"]) == 1
