"""Command-line interface for skval."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import batch
import benchmark_export
import compare
import cost_estimate
import resolve_skill
import scorecard
import validate_full
import validate_structural


def _load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def _friendly_error(exc: Exception) -> str:
    return f"ERROR: {exc}"


def _cmd_structural(args: argparse.Namespace) -> int:
    try:
        sc = validate_structural.validate_structural(
            args.source, Path(args.out), type_override=args.type
        )
    except (FileNotFoundError, ValueError, NotImplementedError) as exc:
        print(_friendly_error(exc), file=sys.stderr)
        return 2
    print(scorecard.render_markdown(sc))
    return 1 if sc["verdict"] == "Reject" else 0


def _cmd_full(args: argparse.Namespace) -> int:
    try:
        sc = validate_full.validate_full(
            args.skill_source,
            Path(args.workspace),
            Path(args.out) if args.out else None,
            type_override=args.type,
        )
    except (FileNotFoundError, ValueError, NotImplementedError) as exc:
        print(_friendly_error(exc), file=sys.stderr)
        return 2
    print(scorecard.render_markdown(sc))
    return 1 if sc["verdict"] == "Reject" else 0


def _cmd_estimate(args: argparse.Namespace) -> int:
    plan = cost_estimate.RunPlan(
        evals=args.evals,
        trials=args.trials,
        configs=args.configs,
        trigger_queries=args.triggering_queries,
        trigger_reps=args.triggering_reps,
        executor_model=args.executor_model,
        judge_model=args.judge_model,
    )
    try:
        if args.write:
            # producing run: resolve + write estimate.json under --out
            out = Path(args.out)
            resolved = resolve_skill.resolve(args.source, out / "resolved")
            est = cost_estimate.estimate(resolved["skill_dir"], plan)
            out.mkdir(parents=True, exist_ok=True)
            (out / "estimate.json").write_text(json.dumps(est, indent=2, sort_keys=True))
            print(cost_estimate.render_markdown(est))
            print(f"wrote {out / 'estimate.json'}", file=sys.stderr)
        else:
            # read-only preview: resolve into a temp dir so nothing lands on disk
            with tempfile.TemporaryDirectory() as tmp:
                resolved = resolve_skill.resolve(args.source, Path(tmp) / "resolved")
                est = cost_estimate.estimate(resolved["skill_dir"], plan)
            print(cost_estimate.render_markdown(est))
    except (FileNotFoundError, ValueError, NotImplementedError) as exc:
        print(_friendly_error(exc), file=sys.stderr)
        return 2
    return 0


def _cmd_benchmark_export(args: argparse.Namespace) -> int:
    out = benchmark_export.write_benchmark(
        args.runs_dir,
        args.out_path,
        skill_name=args.skill_name,
        executor_model=args.executor_model,
    )
    print(f"wrote {out}")
    return 0


def _cmd_batch(args: argparse.Namespace) -> int:
    cards = [_load_json(path) for path in args.scorecards]
    print(batch.render_batch_table(batch.rank_scorecards(cards)), end="")
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    result = compare.compare_scorecards(
        _load_json(args.old_scorecard), _load_json(args.new_scorecard)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skval", description="Validate and score Claude Code skills."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    structural = sub.add_parser(
        "structural", help="Run structural-only validation with no model calls."
    )
    structural.add_argument("source", help="skill directory, SKILL.md file, or .skill/.zip archive")
    structural.add_argument(
        "--out", default="skval-runs/latest", help="output directory for the scorecard"
    )
    structural.add_argument(
        "--type",
        choices=validate_structural.classify.TYPES,
        default=None,
        help="force the skill type (overrides auto-classification)",
    )
    structural.set_defaults(func=_cmd_structural)

    full = sub.add_parser(
        "full", help="Assemble a full scorecard from collected behavioral artifacts."
    )
    full.add_argument("skill_source", help="skill directory, SKILL.md, or .skill/.zip")
    full.add_argument(
        "workspace", help="workspace dir with runs/ + artifact_judgment.json + triggering.json"
    )
    full.add_argument("--out", default=None, help="output dir (default: workspace)")
    full.add_argument(
        "--type",
        choices=validate_full.classify.TYPES,
        default=None,
        help="force the skill type (overrides auto-classification)",
    )
    full.set_defaults(func=_cmd_full)

    estimate = sub.add_parser(
        "estimate",
        help="Estimate the token + $ cost of a full run before launching it (no model calls).",
    )
    estimate.add_argument("source", help="skill directory, SKILL.md file, or .skill/.zip archive")
    estimate.add_argument("--evals", type=int, default=cost_estimate.DEFAULT_EVALS)
    estimate.add_argument("--trials", type=int, default=cost_estimate.DEFAULT_TRIALS)
    estimate.add_argument(
        "--configs",
        type=int,
        choices=[1, 2],
        default=cost_estimate.DEFAULT_CONFIGS,
        help="1 = with-skill only, 2 = with-skill + baseline",
    )
    estimate.add_argument(
        "--triggering-queries", type=int, default=cost_estimate.DEFAULT_TRIGGER_QUERIES
    )
    estimate.add_argument("--triggering-reps", type=int, default=cost_estimate.DEFAULT_TRIGGER_REPS)
    estimate.add_argument("--executor-model", default=cost_estimate.DEFAULT_EXECUTOR_MODEL)
    estimate.add_argument("--judge-model", default=cost_estimate.DEFAULT_JUDGE_MODEL)
    estimate.add_argument(
        "--out", default="skval-runs/estimate", help="dir for resolved skill + estimate.json"
    )
    estimate.add_argument("--write", action="store_true", help="also write estimate.json to --out")
    estimate.set_defaults(func=_cmd_estimate)

    bench = sub.add_parser(
        "benchmark-export", help="Export skval runs to eval-viewer benchmark.json format."
    )
    bench.add_argument("runs_dir", help="workspace runs/ directory")
    bench.add_argument("out_path", help="output benchmark.json path")
    bench.add_argument("--skill-name", default="", help="skill name to store in benchmark metadata")
    bench.add_argument(
        "--executor-model", default="", help="executor model to store in benchmark metadata"
    )
    bench.set_defaults(func=_cmd_benchmark_export)

    batch_parser = sub.add_parser("batch", help="Rank scorecards into a Markdown leaderboard.")
    batch_parser.add_argument("scorecards", nargs="+", help="scorecard.json files")
    batch_parser.set_defaults(func=_cmd_batch)

    compare_parser = sub.add_parser("compare", help="Compare two scorecard JSON files.")
    compare_parser.add_argument("old_scorecard", help="baseline scorecard.json")
    compare_parser.add_argument("new_scorecard", help="candidate scorecard.json")
    compare_parser.set_defaults(func=_cmd_compare)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
