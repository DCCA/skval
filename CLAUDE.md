# skval — guide for Claude Code

**skval** is a Claude Code skill that scores *another* skill 0–100 across six
dimensions (structural, effectiveness, reliability, artifact quality, triggering,
and a safety gate) and returns a **Ship / Revise / Reject** verdict. The skill
itself lives in `skills/skill-validator/`; its deterministic engine is in
`skills/skill-validator/scripts/`.

## Development

- **Setup:** `uv venv && uv pip install -e ".[dev]"` — installs the `skval`
  console entrypoint.
- **Tests:** `uv run pytest` — deterministic, no network or model calls.
  Single file/test: `uv run pytest tests/test_scoring.py -k <expr>`.
- **CLI:** `uv run skval <structural|full|estimate|benchmark-export|batch|compare>`.
  `structural` is the no-model-calls path; `estimate` previews token/$ cost of a
  full run without spending anything.
- **Self-validation gate (run before every PR):**
  ```bash
  uv run python skills/skill-validator/scripts/validate_structural.py skills/skill-validator --out /tmp/skval-self
  ```
  It must report **100 / A / Ship**.
- **Python style:** formatted with `ruff format` (line-length 100, see
  `[tool.ruff]` in `pyproject.toml`). A PostToolUse hook
  (`.claude/hooks/format.sh`) reformats `.py` files on save, so keep edits
  ruff-clean.

## Architecture

Two tiers, split by whether a model is needed:

- **Deterministic engine** (`skills/skill-validator/scripts/`): plain Python,
  unit-tested, no network/model calls. Scores D1 (structural) + D6 (safety gate)
  and does all math/assembly. Flow: `resolve_skill` (dir / SKILL.md / .skill →
  canonical dir, hardened against zip-slip/symlinks/bombs) → `static_checks` +
  `safety_scan` → `scoring` (weighted composite; **safety is a veto gate, not a
  weight**) → `scorecard` (renders json + md).
- **Model-driven stages** (D2–D5): not code — prompt guides in
  `skills/skill-validator/agents/*.md` (executor, grader, artifact-judge,
  triggering, user-simulator, comparator, eval-generator), orchestrated by
  `SKILL.md` via subagents. They drop artifacts into a workspace
  (`grading.json`, `artifact_judgment.json`, `triggering.json`) which
  `validate_full.py` aggregates (`stats.py` pass^k / error bars,
  `aggregate.py`, `dimensions.py` signal→dimension mapping) into the same
  scorecard shape.

Conventions:

- `scripts/` modules are **flat top-level imports** (`import scoring`, no
  package prefix) — `[tool.setuptools.package-dir]` in `pyproject.toml` maps
  the dir to the root, and pytest's `pythonpath` mirrors it. A new module must
  be added to `py-modules` there.
- `skills/skill-validator/references/scoring-rubric.md` is the **source of
  truth** for weights and grade bands; code and docs must match it.
- `classify.py` types a skill (task / file_transform / interactive /
  discipline / reference) and that type routes the eval strategy — see the
  table in `SKILL.md`.

## UI / Design (the landing page in `docs/`)

- The site is a single, hand-tuned static page: `docs/index.html` (dark theme —
  bg `#0d1117`, accent green `#3fb950`, off-white `#e6edf3`). Keep the compact
  inline-CSS style; it is **intentionally not** run through prettier.
- When changing a **UI asset (favicon, logo)**, wire it in **consistently across
  the header, hero, and footer** — not just one spot. The brand mark is
  `docs/favicon.svg`, reused as both the browser-tab icon and the on-page logo.
- For visual changes, optimize for **legibility at small sizes** and stick to the
  brand palette. When the look is subjective, render 2–3 variants and compare them
  at real sizes *before* committing.

## Deployment workflow

- The landing page auto-deploys to **GitHub Pages**: any push to `main` that
  changes `docs/` triggers `.github/workflows/pages.yml`. Live at
  <https://dcca.github.io/skval/>.
- **Ship via PR:** create a PR → verify GitHub Actions pass → merge to `main` →
  confirm the deploy concluded `success`. The **`/ship`** skill runs this whole
  loop in one step.
- Develop on a **feature branch**, never commit directly to `main`. Commit
  identity is `Claude <noreply@anthropic.com>`.

## Tips

- Batch related git/build commands into a single chained Bash call (`&&`) instead
  of many separate calls.
- **Headless / CI review:** run skval (or a review) non-interactively, e.g.
  `claude -p "review the changed HTML for accessibility issues" --allowedTools "Read,Edit,Bash"`.
