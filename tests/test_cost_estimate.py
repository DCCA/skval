"""Tests for the deterministic pre-run cost estimator."""

import pytest

import cost_estimate as ce


@pytest.fixture
def skill_dir(tmp_path):
    (tmp_path / "SKILL.md").write_text("# Skill\n" + "word " * 400, encoding="utf-8")
    refs = tmp_path / "references"
    refs.mkdir()
    (refs / "guide.md").write_text("detail " * 800, encoding="utf-8")
    return tmp_path


def test_measure_skill_tokens(skill_dir):
    md, ref = ce.measure_skill_tokens(skill_dir)
    assert md > 0 and ref > 0
    # references file is larger than SKILL.md here
    assert ref > md


def test_measure_handles_missing_references(tmp_path):
    (tmp_path / "SKILL.md").write_text("# x\n", encoding="utf-8")
    md, ref = ce.measure_skill_tokens(tmp_path)
    assert md > 0
    assert ref == 0


def test_ranges_are_monotonic(skill_dir):
    est = ce.estimate(skill_dir)
    t = est["totals"]
    assert t["tokens"]["low"] <= t["tokens"]["expected"] <= t["tokens"]["high"]
    assert t["cost_usd"]["low"] <= t["cost_usd"]["expected"] <= t["cost_usd"]["high"]
    for st in est["stages"]:
        assert st["tokens"]["low"] <= st["tokens"]["expected"] <= st["tokens"]["high"]
        assert st["cost_usd"]["low"] <= st["cost_usd"]["expected"] <= st["cost_usd"]["high"]


def test_totals_equal_sum_of_stages(skill_dir):
    est = ce.estimate(skill_dir)
    for s in ("low", "expected", "high"):
        assert est["totals"]["tokens"][s] == sum(st["tokens"][s] for st in est["stages"])
        assert est["totals"]["cost_usd"][s] == pytest.approx(
            sum(st["cost_usd"][s] for st in est["stages"])
        )


def test_more_trials_costs_more(skill_dir):
    small = ce.estimate(skill_dir, ce.RunPlan(trials=2))
    big = ce.estimate(skill_dir, ce.RunPlan(trials=10))
    assert big["totals"]["cost_usd"]["expected"] > small["totals"]["cost_usd"]["expected"]


def test_more_evals_costs_more(skill_dir):
    small = ce.estimate(skill_dir, ce.RunPlan(evals=2))
    big = ce.estimate(skill_dir, ce.RunPlan(evals=8))
    assert big["totals"]["tokens"]["expected"] > small["totals"]["tokens"]["expected"]


def test_single_config_drops_baseline_executor(skill_dir):
    two = ce.estimate(skill_dir, ce.RunPlan(configs=2))
    one = ce.estimate(skill_dir, ce.RunPlan(configs=1))
    names_two = [s["name"] for s in two["stages"]]
    names_one = [s["name"] for s in one["stages"]]
    assert "executor_baseline" in names_two
    assert "executor_baseline" not in names_one
    assert one["totals"]["cost_usd"]["expected"] < two["totals"]["cost_usd"]["expected"]


def test_bigger_skill_costs_more(tmp_path):
    small = tmp_path / "small"
    small.mkdir()
    (small / "SKILL.md").write_text("# x\n" + "a " * 50, encoding="utf-8")
    big = tmp_path / "big"
    big.mkdir()
    (big / "SKILL.md").write_text("# x\n" + "a " * 5000, encoding="utf-8")
    assert (
        ce.estimate(big)["totals"]["tokens"]["expected"]
        > ce.estimate(small)["totals"]["tokens"]["expected"]
    )


def test_unknown_model_flagged_not_crashed(skill_dir):
    est = ce.estimate(skill_dir, ce.RunPlan(executor_model="gpt-4o"))
    assert "gpt-4o" in est["pricing_unknown"]
    # tokens still counted, but the gpt stages cost $0
    assert est["totals"]["tokens"]["expected"] > 0
    # judge stages still priced, so total cost is positive
    assert est["totals"]["cost_usd"]["expected"] > 0


@pytest.mark.parametrize(
    "plan",
    [
        ce.RunPlan(configs=0),
        ce.RunPlan(configs=-1),
        ce.RunPlan(configs=3),
        ce.RunPlan(evals=0),
        ce.RunPlan(trials=0),
        ce.RunPlan(trigger_reps=0),
        ce.RunPlan(trigger_queries=-1),
    ],
)
def test_invalid_plan_raises(skill_dir, plan):
    with pytest.raises(ValueError):
        ce.estimate(skill_dir, plan)


def test_valid_plans_do_not_raise(skill_dir):
    for plan in (ce.RunPlan(configs=1), ce.RunPlan(configs=2), ce.RunPlan(trigger_queries=0)):
        ce.estimate(skill_dir, plan)  # no exception


def test_render_markdown_smoke(skill_dir):
    md = ce.render_markdown(ce.estimate(skill_dir))
    assert "Cost estimate" in md
    assert "Total" in md
    assert "$" in md


def test_render_flags_unknown_pricing(skill_dir):
    md = ce.render_markdown(ce.estimate(skill_dir, ce.RunPlan(judge_model="mystery-model")))
    assert "No price on file" in md
    assert "mystery-model" in md
