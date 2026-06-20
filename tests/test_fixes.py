"""Regression tests for issues found in the review pass."""

import json

import benchmark_export
import runs_io
import safety_scan
import scoring
import static_checks as sc


# --- safety: home/glob deletes must veto (the \b-after-~/* gap) ---
def test_home_and_glob_delete_vetoed(tmp_path):
    for i, cmd in enumerate(("rm -rf ~", "rm -rf *", "rm -rf ~/work", "rm -rf */")):
        d = tmp_path / f"s{i}"
        d.mkdir()
        (d / "SKILL.md").write_text(f"---\nname: x\ndescription: y\n---\n{cmd}\n")
        assert safety_scan.scan(d)["safety_pass"] is False, cmd


def test_glob_with_extension_not_flagged(tmp_path):
    d = tmp_path / "ok"
    d.mkdir()
    (d / "SKILL.md").write_text(
        "---\nname: x\ndescription: y\n---\nrm -rf *.tmp in your build dir\n"
    )
    assert safety_scan.scan(d)["safety_pass"] is True


# --- scoring: zero-weight guard + clamping ---
def test_composite_zero_weight_no_crash():
    assert scoring.composite({"D1": 0.8}, True, {"D1": 0.0}) == 0


def test_composite_clamps_out_of_range():
    assert scoring.composite({"D1": 2.0}, True) == 100
    assert scoring.composite({"D1": -0.5}, True) == 0


# --- static_checks: CRLF, reference-style links, angle-bracket destinations ---
GOOD = (
    "---\nname: my-skill\ndescription: Use when you need a clean fixture.\n---\n# My Skill\nBody.\n"
)


def _write(tmp_path, body, name):
    d = tmp_path / name
    d.mkdir()
    (d / "SKILL.md").write_text(body)
    return d


def test_crlf_frontmatter_parses(tmp_path):
    body = "---\r\nname: ok-name\r\ndescription: Use when CRLF authored.\r\n---\r\n# x\r\nbody\r\n"
    checks = {c.id: c for c in sc.run_checks(_write(tmp_path, body, "crlf"))}
    assert checks["frontmatter_valid_yaml"].passed
    assert checks["name_kebab_case"].passed


def test_reference_style_broken_link_detected(tmp_path):
    body = GOOD + "\nSee the [guide][g].\n\n[g]: references/missing.md\n"
    checks = {c.id: c for c in sc.run_checks(_write(tmp_path, body, "refdef"))}
    assert not checks["no_broken_local_refs"].passed


def test_angle_bracket_existing_link_ok(tmp_path):
    d = _write(tmp_path, GOOD + "\nSee [h](<scripts/real.py>).\n", "angle")
    (d / "scripts").mkdir()
    (d / "scripts" / "real.py").write_text("# ok\n")
    checks = {c.id: c for c in sc.run_checks(d)}
    assert checks["no_broken_local_refs"].passed


def test_skill_name_helper(tmp_path):
    d = _write(tmp_path, GOOD, "nm")
    assert sc.skill_name(d / "SKILL.md") == "my-skill"
    assert sc.skill_name(d / "nope.md") is None


def test_prose_label_not_flagged_as_broken_ref(tmp_path):
    # A prose heading "[Subagent returns]:" and a "[Note]: see below" line are not links.
    body = (
        GOOD
        + "\n[Subagent returns]:\n\nStrengths: what went well\n\n[Note]: see the section below\n"
    )
    checks = {c.id: c for c in sc.run_checks(_write(tmp_path, body, "prose"))}
    assert checks["no_broken_local_refs"].passed


# --- runs_io: optional metrics/timing flow through ---
def _mk_run(base, eval_id, cfg, run, pr, metrics=None, timing=None):
    d = base / f"eval-{eval_id}" / cfg / f"run-{run}"
    (d / "outputs").mkdir(parents=True)
    passed = round(pr * 2)
    (d / "grading.json").write_text(
        json.dumps(
            {"summary": {"pass_rate": pr, "passed": passed, "failed": 2 - passed, "total": 2}}
        )
    )
    if metrics is not None:
        (d / "outputs" / "metrics.json").write_text(json.dumps(metrics))
    if timing is not None:
        (d / "timing.json").write_text(json.dumps(timing))


def test_load_runs_optional_metrics_timing(tmp_path):
    _mk_run(
        tmp_path,
        0,
        "with_skill",
        1,
        1.0,
        metrics={"total_tool_calls": 7, "errors_encountered": 1},
        timing={"total_duration_seconds": 12.5, "total_tokens": 900},
    )
    r = runs_io.load_runs(tmp_path)["with_skill"][0]
    assert r["tool_calls"] == 7 and r["errors"] == 1
    assert r["time_seconds"] == 12.5 and r["tokens"] == 900


def test_benchmark_export_flows_metrics_and_n(tmp_path):
    runs = tmp_path / "runs"
    _mk_run(
        runs,
        0,
        "with_skill",
        1,
        1.0,
        metrics={"total_tool_calls": 5, "errors_encountered": 0},
        timing={"total_duration_seconds": 9.0, "total_tokens": 400},
    )
    _mk_run(runs, 0, "with_skill", 2, 1.0)
    bench = benchmark_export.export_benchmark(runs, skill_name="demo")
    res = next(r["result"] for r in bench["runs"] if r["run_number"] == 1)
    assert res["tool_calls"] == 5 and res["time_seconds"] == 9.0 and res["tokens"] == 400
    assert bench["metadata"]["runs_per_configuration"] == 2  # max runs in the (config,eval) bucket
