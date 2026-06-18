# Contributing to skval

Thanks for your interest! **skval** is a Claude Code skill with a deterministic Python core
and model-driven agent prompts. Contributions — bug reports, new checks, better evals — are
welcome.

## Dev setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/DCCA/skval && cd skval
uv run pytest            # 108 deterministic tests, no network/model calls
```

## Conventions

- **TDD.** Write a failing test first, then the implementation (see `tests/`).
- **Keep the engine deterministic.** Everything in `skills/skill-validator/scripts/*.py` must
  stay free of network/model calls — the model-driven parts live in the agent prompts
  (`skills/skill-validator/agents/*.md`). The test suite must remain hermetic (no API calls).
- **Dogfood.** skval validates itself; this must stay green:
  ```bash
  uv run python skills/skill-validator/scripts/validate_structural.py skills/skill-validator
  ```
  (Expected: 100 / A / Ship.)
- **Respect the budgets.** Keep `SKILL.md` under the size budget the checks enforce; push
  detail into `references/`.

## Where things live

- `scripts/` — the deterministic engine (structural checks, safety gate, stats, scoring,
  aggregation, comparison, classification, fixtures, conversation analysis).
- `agents/` — the prompt guides the orchestrating agent follows (eval-generator, executor,
  grader, artifact-judge, triggering, user-simulator, comparator).
- `references/scoring-rubric.md` — the **source of truth** for weights and bands (mirror any
  change into `scripts/scoring.py`).

## Adding a check or dimension

1. Add the check in the relevant `scripts/*.py` module **with a test**.
2. If it affects scoring, update both `references/scoring-rubric.md` and `scripts/scoring.py`.
3. Run `uv run pytest` and confirm the skill still self-validates.

## Pull requests

Keep changes focused, include tests, and make sure `uv run pytest` is green and the skill
self-validates before opening a PR.
