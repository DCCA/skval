# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-30

Initial release.

### Added

- **Deterministic engine (D1 + D6):** input resolver (skill dir, `SKILL.md`, or
  `.skill`/`.zip`/`.tar.gz` archive), D1 structural checks, D6 static safety gate,
  `pass^k` statistics, safety-gated weighted scoring, and scorecard generation
  (`scorecard.json` + `scorecard.md`) — a structural-only path with **no model
  calls** that exits non-zero on a Reject verdict.
- **Behavioral pipeline (D2–D5) via agents:** effectiveness with lift over a
  no-skill baseline (D2), reliability as `pass^k` over repeated trials (D3),
  artifact quality via a decomposed LLM rubric (D4), and triggering
  precision/recall/F1 (D5), driven by agent prompts (eval-generator, executor,
  grader, artifact-judge, triggering, user-simulator, comparator) and assembled
  into a full scorecard by `skval full`.
- **Skill-type classification routing:** `classify.py` detects the skill type and
  routes it to a matching evaluation strategy (executor style, fixtures, grading,
  agents), with a `--type` override.
- **Multi-turn / interactive evals:** a user-simulator agent plus deterministic
  transcript analysis (`conversation.py`) make ask-before-acting expectations
  (e.g. "asks at least 2 clarifying questions") objectively checkable.
- **Eval input fixtures for file-transform skills:** the eval-generator declares
  per-eval input files and `eval_fixtures.py` stages them into each executor run
  (`missing_fixtures` pre-flight + `stage`).
- **Comparison and reporting tools:** version A/B comparison with pairwise
  position-swap (`compare.py`), regression history (`history.py`), batch
  leaderboard ranking (`batch.py`), weight calibration (`calibrate.py`), and
  eval-viewer export (`benchmark_export.py`).
- **`skval` CLI** with `structural`, `full`, `estimate`, `benchmark-export`,
  `batch`, and `compare` subcommands — including `skval estimate`, a
  deterministic token + $ cost preview of a full run (per-stage breakdown,
  low/expected/high range).
- **Hardened archive extraction:** rejects path traversal (zip-slip/tar-slip),
  symlink members, and decompression bombs (250 MiB uncompressed cap); remote/git
  sources are refused.
- **Landing page + GitHub Pages:** `docs/index.html`, auto-deployed by
  `.github/workflows/pages.yml` to <https://dcca.github.io/skval/>.
- **CI** (`.github/workflows/ci.yml`): ruff format/lint, pytest, and a
  self-validation gate — skval must score itself 100 / A / Ship.
- **Composite GitHub Action** (`action.yml`): `uses: DCCA/skval@v0.1.0` runs
  `skval structural` on a skill in CI, fails the job on a Reject verdict, and
  exposes `score` / `grade` / `verdict` outputs.
- **Claude Code plugin manifest** (`.claude-plugin/plugin.json`), so the repo
  installs as a plugin with the skill auto-discovered from `skills/`.

[Unreleased]: https://github.com/DCCA/skval/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/DCCA/skval/releases/tag/v0.1.0
