# skval — Skill Validator Framework

Give it a skill, get a score. **skval** is a Claude Code skill that takes another
skill — a directory, a `SKILL.md`, or a packaged `.skill` — runs it through evals
and benchmarks, and returns a **Skill Score (0–100)** with a letter grade, a
per-dimension breakdown, ranked findings, and a **Ship / Revise / Reject** verdict.

It is the measurement counterpart to Anthropic's `skill-creator`: where that helps
you *write* a skill, skval exists to *judge* one — rigorously and repeatably, grounded
in the agent-evaluation literature (SWE-bench, GAIA, AgentBench, τ-bench), the
LLM-as-judge literature (Zheng et al. 2023, G-Eval, FLASK, HELM, Miller 2024), and
paired Agent Skills evaluation work such as
[SkillsBench](docs/references/skillsbench.md).

> 📖 **New here? Start with the [step-by-step usage guide](docs/USAGE.md)** — from
> install to reading a full scorecard, with screenshots and copy-paste commands.
>
> 🌐 **Live site:** [dcca.github.io/skval](https://dcca.github.io/skval/)

## Scoring model

A **safety-gated, normalized weighted composite** over six dimensions — reported as a
vector *and* a single number:

| Dim | Dimension | Weight | Type |
|-----|-----------|--------|------|
| D1 | Structural integrity | 0.15 | deterministic |
| D2 | Effectiveness (pass rate + lift over a no-skill baseline) | 0.30 | behavioral, LLM-graded |
| D3 | Reliability (`pass^k` over N=5 trials) | 0.20 | behavioral |
| D4 | Artifact quality (decomposed LLM rubric) | 0.20 | LLM-as-judge |
| D5 | Triggering (precision/recall/F1) | 0.15 | behavioral |
| D6 | Safety / least-surprise | **gate** | deterministic + LLM |

`SkillScore = round(100 · safety_gate · Σ wᵢdᵢ)`. Bands: A≥90, B≥80 (Ship); C≥70,
D≥50 (Revise); else F (Reject). A safety failure vetoes the score regardless of the
rest. See [`skills/skill-validator/references/scoring-rubric.md`](skills/skill-validator/references/scoring-rubric.md).

## Status

- **M0 — deterministic core (done):** input resolver; D1 structural checks; D6 static
  safety gate; the statistics engine (`pass^k`, error bars); the scoring engine
  (composite/gate/grade/verdict); scorecard generation; and a **structural-only**
  end-to-end path that produces a real scorecard with **no model calls**.
- **M1 — behavioral + LLM-judge (done):** behavioral aggregation (`pass^k`, baseline
  lift, significance), dimension mapping (D2–D5), the full-validation assembler, and
  agent prompts (`agents/`: eval generation, executor, grader, artifact judge,
  triggering) wired into the skill. The deterministic computation is unit-tested; the
  model-driven runs are agent-orchestrated per `SKILL.md`.
- **M2–M3 — comparison & polish (done):** version A/B with pairwise **position-swap**
  (`compare.py` + `agents/comparator.md`), regression **history** (`history.py`), **batch**
  ranking (`batch.py`), **eval-viewer export** (`benchmark_export.py`), weight
  **calibration** (`calibrate.py`), and a Claude Code **plugin manifest**
  (`.claude-plugin/`). See the
  [implementation plan](docs/plans/2026-06-18-skill-validator.md) and
  [PRD](docs/prd/skill-validator-prd.md).

## Install (as a Claude Code skill)

```bash
cp -r skills/skill-validator ~/.claude/skills/
```

Then ask Claude to "validate / score / grade a skill," or run the deterministic path
directly (below). The repo also ships a `.claude-plugin/plugin.json`, so it can be
installed as a Claude Code plugin (skills are auto-discovered from `skills/`).

## Use the deterministic scan now

```bash
uv venv && uv pip install -e ".[dev]"
uv run skval structural <skill-source> --out skval-runs/<name>
```

Script fallback if you do not want the console entrypoint:

```bash
uv run python skills/skill-validator/scripts/validate_structural.py <skill-source> --out skval-runs/<name>
```

Example output (a known-good fixture):

```
## ██████████████  100 / 100   Grade: A   Verdict: Ship
```

It writes `scorecard.json` + `scorecard.md` and exits non-zero on a Reject verdict —
handy as a CI gate. The full six-dimension validation (D2–D5) is driven by the skill
itself via subagents and `claude -p`, following `skills/skill-validator/SKILL.md`.

## Preview the cost before a full run

The full validation spawns dozens of subagents (~1M tokens for a default run). For
token-billed / enterprise users, `skval estimate` projects the **token + $ cost**
first — deterministic, no model calls:

```bash
uv run skval estimate <skill-source>
# → ## $4.04 – $6.19 – $12.23   (684k – 1.04M – 2.04M tokens)
```

It prints a per-stage breakdown (executors, graders, judge, triggering) as a
low / expected / high range, priced from a per-model rate table. Tune the plan with
`--evals` / `--trials` / `--configs` / `--executor-model` / `--judge-model`, and pass
`--write` to also save `estimate.json`. It reads the skill but writes nothing unless
`--write` is given.

## Repo layout

```
skills/skill-validator/   # the skill (SKILL.md + scripts/ + references/)
docs/prd/                 # product requirements
docs/plans/               # implementation plan
tests/                    # pytest suite + fixtures (good / bad / unsafe skills)
```

## Develop

```bash
uv run pytest          # 163 tests, deterministic, no network/model calls
```

Built with the [Superpowers](https://github.com/obra/superpowers) methodology
(brainstorming → writing-plans → TDD).

## Security

skval ingests untrusted skills, so archive extraction rejects path traversal (zip-slip /
tar-slip), symlink members, and decompression bombs; the deterministic engine makes no
network calls and uses `yaml.safe_load`. See [SECURITY.md](SECURITY.md).

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Please run `uv run pytest`
and confirm the skill still self-validates (100/A) before opening a PR.

## License

[MIT](LICENSE) © 2026 DCCA.
