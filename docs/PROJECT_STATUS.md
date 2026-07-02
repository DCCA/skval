# Project status

A dated logbook of where skval stands at the end of each work session. Newest entry
first. For usage see [USAGE.md](USAGE.md); for architecture see the repo `CLAUDE.md`.

## 2026-07-02 - Project review, competitor research, and D2 statistics upgrade

**Where we were:** skval's deterministic engine, six-dimension scoring, and landing
page were all shipped and green (163 tests, self-validation 100/A/Ship). The
`CLAUDE.md` documented commands and design but not setup, the CLI surface, or the
two-tier architecture, and CI ran tests without enforcing formatting/lint.

**What we did:**
- Expanded `CLAUDE.md` (setup/install, `skval` CLI subcommands, single-test command,
  and an architecture section: deterministic engine vs model-driven agent stages,
  flat `scripts/` imports, rubric as source of truth); added a `ruff format --check`
  + `ruff check` step to CI; dropped the hardcoded test count in the README (#48).
- Ran a deep-research survey of similar eval frameworks (105 agents, 23 sources, 25
  adversarially verified claims). Key result: skval's core design is externally
  validated (SkillsBench for lift-vs-baseline, tau-bench for pass^k), and the highest
  value-per-effort gaps are statistical. Full findings are in the 2026-07-02 chat.
- Implemented the top two research items on the D2 effectiveness dimension (#49):
  Hake **normalized gain** `g = (skill − baseline) / (1 − baseline)` reported in the
  scorecard, and **paired-difference significance** (Miller 2024) that pairs per-eval
  means when ≥2 evals exist in both configs, falling back to the unpaired SE for one
  eval. New pure helpers `stats.normalized_gain` / `stats.paired_diff`, TDD, +6 tests
  (now 169 passing, ruff clean, self-validation still 100/A/Ship).

**Decisions:** kept `baseline_lift` and its unpaired SE unchanged (new fields are
additive) so nothing downstream breaks. Deferred the Bayesian/Bayes@N verdict rework
(research item 3) to its own design pass because it changes what the score *means* -
not a drop-in like normalized gain was.

**Pending / next:** (from the research backlog, roughly by value-per-effort)
- [ ] Item 4 - named deterministic safety checks in `safety_scan.py` (tool over-grant,
      unpinned deps, `eval`/`exec`, `curl | sh`), per OWASP Agentic / SkillCheck. Best
      next PR: cheap greps, deterministic, high signal.
- [ ] Item 5 - score cost/latency, not just record them: `runs_io` already loads
      token/time metrics; surface actual spend per config in the scorecard.
- [ ] Item 3 - Bayes@N posterior verdicts with credible intervals + adaptive trial
      allocation. Needs a design pass first (pass^k all-k vs pass@k semantics, how
      credible intervals map onto the 0-100 bands and Ship/Revise/Reject).
- [ ] Item 6 - Agent-as-a-Judge (multi-agent) for D4, or route more of D4 through
      deterministic end-state checks where ground truth is checkable.
- [ ] Item 7 - description-optimization loop when D5 triggering scores low.
- [ ] Follow-up research: the mainstream-framework half (promptfoo/DeepEval/Braintrust
      CI gating + reporting UX) produced no verified claims - worth a targeted pass.
