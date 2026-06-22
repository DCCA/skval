"""Pre-run token + cost estimate for a full skval validation (deterministic).

Enterprise users pay by tokens and want to know what a full ``skval full`` run
will cost *before* spawning the behavioral subagents. This module projects the
token spend of each model-driven stage (eval generation, executors, graders,
artifact judge, triggering) for a given run plan, prices it via ``pricing``, and
reports a low / expected / high range. It makes **no model calls** — the
deterministic structural + safety scan it complements is itself free.

The numbers are a transparent heuristic, not a guarantee: per-stage base token
assumptions (anchored to observed runs ~18-20k tokens/executor, ~22-24k/judge)
scaled by the plan, with a spread for agentic-loop variance and skill size. The
constants below are tunable and calibration-ready (e.g. from ``history.json``).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pricing

# ---- run-plan defaults (mirror SKILL.md) ----------------------------------
DEFAULT_EVALS = 4
DEFAULT_TRIALS = 5
DEFAULT_CONFIGS = 2  # with-skill + no-skill baseline
DEFAULT_TRIGGER_QUERIES = 16  # ~8 should-trigger + ~8 should-not
DEFAULT_TRIGGER_REPS = 3  # majority-vote repeats per query
DEFAULT_EXECUTOR_MODEL = "claude-sonnet-4-6"
DEFAULT_JUDGE_MODEL = "claude-opus-4-8"

# ---- per-stage base token assumptions (expected; skill load added on top) --
# (base_input, base_output) per call, excluding the skill tokens added to
# skill-loaded stages. Anchored to the observed `ship` validation run.
_STAGE_BASE = {
    "eval_generation": (3000, 2000),
    "executor": (14000, 3000),
    "grader": (5000, 1000),
    "artifact_judge": (4000, 3000),
    "triggering": (1000, 100),
}

# scenario multipliers on the agentic base tokens
_FACTORS = {"low": 0.65, "expected": 1.0, "high": 2.0}
_SCENARIOS = ("low", "expected", "high")


def _tok(text: str) -> int:
    """Rough token count: 1 token ~= 4 chars (the heuristic used in static_checks)."""
    return len(text) // 4


def measure_skill_tokens(skill_dir: str | Path) -> tuple[int, int]:
    """Return ``(skill_md_tokens, reference_tokens)`` for a resolved skill dir.

    SKILL.md loads into every skill-aware stage; ``references/`` loads on demand,
    so it widens the high end of the estimate rather than the floor.
    """
    skill_dir = Path(skill_dir)
    md = skill_dir / "SKILL.md"
    md_tokens = _tok(md.read_text(encoding="utf-8", errors="replace")) if md.exists() else 0

    ref_tokens = 0
    refs = skill_dir / "references"
    if refs.is_dir():
        for f in sorted(refs.rglob("*")):
            if f.is_file():
                try:
                    ref_tokens += _tok(f.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    continue
    return md_tokens, ref_tokens


@dataclass
class RunPlan:
    evals: int = DEFAULT_EVALS
    trials: int = DEFAULT_TRIALS
    configs: int = DEFAULT_CONFIGS
    trigger_queries: int = DEFAULT_TRIGGER_QUERIES
    trigger_reps: int = DEFAULT_TRIGGER_REPS
    executor_model: str = DEFAULT_EXECUTOR_MODEL
    judge_model: str = DEFAULT_JUDGE_MODEL


def _validate(plan: RunPlan) -> None:
    """Reject incoherent plans so every reachable estimate is well-formed.

    The cost model only supports 1 config (with-skill) or 2 (with-skill + one
    no-skill baseline) — the two configs of a real skval run. Out-of-range values
    would otherwise produce negative or internally-inconsistent estimates.
    """
    if plan.evals < 1:
        raise ValueError("evals must be >= 1")
    if plan.trials < 1:
        raise ValueError("trials must be >= 1")
    if plan.configs not in (1, 2):
        raise ValueError("configs must be 1 (with-skill) or 2 (with-skill + baseline)")
    if plan.trigger_queries < 0:
        raise ValueError("trigger_queries must be >= 0")
    if plan.trigger_reps < 1:
        raise ValueError("trigger_reps must be >= 1")


def _skill_scenarios(md_tokens: int, ref_tokens: int) -> dict[str, int]:
    """Skill tokens loaded per scenario: floor=SKILL.md, ceiling=+references."""
    return {
        "low": md_tokens,
        "expected": md_tokens + ref_tokens // 2,
        "high": md_tokens + ref_tokens,
    }


def _stage(name: str, model: str, count: int, skill_loaded: bool, skill: dict[str, int]) -> dict:
    base_in, base_out = _STAGE_BASE[name]
    input_each, output_each, tokens, cost = {}, {}, {}, {}
    known = pricing.is_known(model)
    for s in _SCENARIOS:
        f = _FACTORS[s]
        ie = round(base_in * f) + (skill[s] if skill_loaded else 0)
        oe = round(base_out * f)
        input_each[s] = ie
        output_each[s] = oe
        tokens[s] = count * (ie + oe)
        cost[s] = pricing.cost_usd(model, count * ie, count * oe) if known else 0.0
    return {
        "name": name,
        "model": model,
        "count": count,
        "skill_loaded": skill_loaded,
        "input_each": input_each,
        "output_each": output_each,
        "tokens": tokens,
        "cost_usd": cost,
    }


def estimate(skill_dir: str | Path, plan: RunPlan | None = None) -> dict:
    """Estimate token + $ cost of a full validation run for ``skill_dir``."""
    plan = plan or RunPlan()
    _validate(plan)
    md_tokens, ref_tokens = measure_skill_tokens(skill_dir)
    skill = _skill_scenarios(md_tokens, ref_tokens)

    et = plan.evals * plan.trials
    stages = [
        _stage("eval_generation", plan.judge_model, 1, True, skill),
        _stage("executor", plan.executor_model, et, True, skill),  # with-skill config
    ]
    if plan.configs >= 2:
        # baseline (no-skill) executors: same task, skill not loaded
        base = _stage("executor", plan.executor_model, et, False, skill)
        base["name"] = "executor_baseline"
        stages.append(base)
    stages.append(_stage("grader", plan.judge_model, et * plan.configs, False, skill))
    stages.append(_stage("artifact_judge", plan.judge_model, 1, True, skill))
    stages.append(
        _stage(
            "triggering", plan.judge_model, plan.trigger_queries * plan.trigger_reps, False, skill
        )
    )

    totals_tokens = {s: sum(st["tokens"][s] for st in stages) for s in _SCENARIOS}
    totals_cost = {s: sum(st["cost_usd"][s] for st in stages) for s in _SCENARIOS}

    unknown = sorted({st["model"] for st in stages if not pricing.is_known(st["model"])})

    return {
        "skill_dir": str(skill_dir),
        "plan": vars(plan),
        "skill_tokens": {"skill_md": md_tokens, "references": ref_tokens},
        "stages": stages,
        "totals": {"tokens": totals_tokens, "cost_usd": totals_cost},
        "pricing_unknown": unknown,
        "notes": [
            "Heuristic estimate (low/expected/high), not a guarantee.",
            "Prompt caching is not modeled, so real cost often runs lower.",
            "Excludes the free deterministic structural + safety scan.",
        ],
    }


# ---- rendering -------------------------------------------------------------

_STAGE_LABELS = {
    "eval_generation": "Eval generation",
    "executor": "Executor (with skill)",
    "executor_baseline": "Executor (baseline)",
    "grader": "Grader",
    "artifact_judge": "Artifact judge",
    "triggering": "Triggering",
}


def _fmt_tokens(n: float) -> str:
    n = round(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}k"
    return str(n)


def _fmt_usd(x: float) -> str:
    return f"${x:,.2f}"


def render_markdown(est: dict) -> str:
    p = est["plan"]
    t = est["totals"]
    lines = [
        "# Cost estimate — full skval run",
        "",
        f"Skill: `{est['skill_dir']}` · "
        f"plan: {p['evals']} evals × {p['configs']} configs × {p['trials']} trials, "
        f"{p['trigger_queries']}×{p['trigger_reps']} triggering",
        f"Executor: `{p['executor_model']}` · Judge: `{p['judge_model']}`",
        "",
        f"## {_fmt_usd(t['cost_usd']['low'])} – {_fmt_usd(t['cost_usd']['expected'])} "
        f"– {_fmt_usd(t['cost_usd']['high'])}   "
        f"({_fmt_tokens(t['tokens']['low'])} – {_fmt_tokens(t['tokens']['expected'])} "
        f"– {_fmt_tokens(t['tokens']['high'])} tokens)",
        "",
        "| Stage | Model | Calls | Exp tokens | Cost (low–exp–high) |",
        "|-------|-------|------:|-----------:|---------------------|",
    ]
    for st in est["stages"]:
        label = _STAGE_LABELS.get(st["name"], st["name"])
        c = st["cost_usd"]
        lines.append(
            f"| {label} | `{st['model']}` | {st['count']} | "
            f"{_fmt_tokens(st['tokens']['expected'])} | "
            f"{_fmt_usd(c['low'])} – {_fmt_usd(c['expected'])} – {_fmt_usd(c['high'])} |"
        )
    lines.append(
        f"| **Total** | | | **{_fmt_tokens(t['tokens']['expected'])}** | "
        f"**{_fmt_usd(t['cost_usd']['low'])} – {_fmt_usd(t['cost_usd']['expected'])} "
        f"– {_fmt_usd(t['cost_usd']['high'])}** |"
    )
    lines.append("")
    if est["pricing_unknown"]:
        lines.append(
            "> ⚠ No price on file for: "
            + ", ".join(f"`{m}`" for m in est["pricing_unknown"])
            + " — those stages are counted in tokens but cost $0 here. Add them to `pricing.PRICES`."
        )
        lines.append("")
    for n in est["notes"]:
        lines.append(f"- {n}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":  # pragma: no cover
    import sys
    import tempfile

    import resolve_skill

    with tempfile.TemporaryDirectory() as _tmp:
        _resolved = resolve_skill.resolve(sys.argv[1], Path(_tmp) / "resolved")
        print(render_markdown(estimate(_resolved["skill_dir"])))
