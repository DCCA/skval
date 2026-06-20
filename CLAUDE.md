# skval — guide for Claude Code

**skval** is a Claude Code skill that scores *another* skill 0–100 across six
dimensions (structural, effectiveness, reliability, artifact quality, triggering,
and a safety gate) and returns a **Ship / Revise / Reject** verdict. The skill
itself lives in `skills/skill-validator/`; its deterministic engine is in
`skills/skill-validator/scripts/`.

## Development

- **Tests:** `uv run pytest` — deterministic, no network or model calls.
- **Self-validation gate (run before every PR):**
  ```bash
  uv run python skills/skill-validator/scripts/validate_structural.py skills/skill-validator --out /tmp/skval-self
  ```
  It must report **100 / A / Ship**.
- **Python style:** formatted with `ruff format` (line-length 100, see
  `[tool.ruff]` in `pyproject.toml`). A PostToolUse hook
  (`.claude/hooks/format.sh`) reformats `.py` files on save, so keep edits
  ruff-clean.

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
