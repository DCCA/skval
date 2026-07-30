# Full behavioral runs — variance & separation study

**The question this study answers:** does skval's *full* six-dimension score (not just the
deterministic D1+D6 scan) measure repeatably and discriminate between skills? Five complete
behavioral runs, executed 2026-07-30 by a 70-agent workflow (0 errors, ~23 min, ≈2.6M tokens),
every artifact committed here for audit.

## Protocol

| Element | Value |
|---|---|
| Subjects | `commit-conventions` (repo-local, run **3×** for variance) · `design-systems` · `mcp-builder` (both bundled Anthropic skills, D1 = 100 pre-verified) |
| Evals | 2–3 single-turn evals/skill, 3–5 atomic binary expectations each (commit-conventions reuses its committed eval set + triggering queries **unchanged** for comparability) |
| Trials | 3 independent executor contexts × 2 configs (with / without skill) per eval |
| Executor | `haiku` (fixed across all runs), low effort; baseline agents **forbidden** from reading any skill file |
| Grader | `sonnet`, strict, reference-guided, binary per expectation with quoted evidence |
| Judge (D4) | `sonnet`, 6 atomic binary criteria derived from the subject skill's own quality bar |
| Assembly | `validate_full.py` — deterministic aggregation (`pass^k`, paired lift, significance) |

Each `*/` directory is a full skval workspace: `evals/`, `runs/eval-*/{with,without}_skill/run-*/`
(outputs + gradings), `artifact_judgment.json`, `triggering.json`, `scorecard.{json,md}`.

## Results

| Run | D1 | D2 | D3 | D4 | D5 | Score | Baseline pass rate | Paired lift |
|---|---|---|---|---|---|---|---|---|
| commit-conventions r1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **100 / A / Ship** | 1.00 | 0 |
| commit-conventions r2 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **100 / A / Ship** | 1.00 | 0 |
| commit-conventions r3 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **100 / A / Ship** | 1.00 | 0 |
| design-systems | 1.00 | 1.00 | 1.00 | **0.67** | 1.00 | **93 / A / Ship** | 1.00 | 0 |
| mcp-builder | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **100 / A / Ship** | 0.92 | **+7.8 pp (significant)** |

### Variance: 0 across three identical-protocol runs

Same skill, same evals, same triggering queries, independent executor/grader contexts:
`[100, 100, 100]`, spread **0**, σ **0.00** — and identical per-dimension vectors. At the top of
the scale the meter is stable. *Caveat:* all three runs sit at the ceiling, so this bounds noise
only there; mid-range variance (where Ship/Revise flips) still needs a sub-ceiling subject.

### Separation: D4 discriminates; D2 mostly saturated

`design-systems` lost 7 points exactly where the judge found real gaps — its with-skill outputs
did not consistently carry the skill's *accessibility-up-front* and *semantic naming* guidance
(4/6 criteria; see [`design-systems/artifact_judgment.json`](design-systems/artifact_judgment.json)).
The only significant effectiveness lift was `mcp-builder`'s **+7.8 pp** (baseline 0.92 → 1.00,
paired SE 0.048) — driven by its *application* eval (write the actual TypeScript tool
registration: Zod schema, `readOnlyHint` annotations, `outputSchema`), not its recall evals.

### The main finding: training-data contamination saturates recall-anchored evals

The baseline (no skill, cheapest executor) reproduced a public skill's guidance almost
verbatim — e.g. the skill's line 74 *"Marketing icons: max 2 colors. 3+ colors = illustration,
not icon"* came back from the bare baseline as *"3+ colors cross into illustration territory
and shouldn't be called 'icons'"*, alongside its "gap ≥ stroke weight" and "build the large
size first" rules ([receipt](design-systems/runs/eval-0/without_skill/run-1/outputs/response.md)).

Two hypotheses were ruled out with audits committed alongside the data:

- **Grader leniency — no.** Spot-checks show every PASS backed by an accurate quote from the
  graded output.
- **Baseline cheating — no.** All 15 baseline agent transcripts were audited for file reads:
  **zero** touched any `SKILL.md` or skills path.

Conclusion: bundled/public skills (and universal conventions like Conventional Commits) are in
frontier training corpora, so *"does the model already know this guidance?"* is the wrong eval
question — the baseline knows it. Discrimination must come from **application-under-constraint**
tasks (mcp-builder's lift) and **artifact quality under the skill's own bar** (design-systems'
D4), not from recall.

**Product change shipped from this finding:** `agents/eval-generator.md` now has a
**contamination guard** step — prefer application tasks over recall tasks, and run a one-trial
baseline probe first; if the baseline already passes ≥ 80%, regenerate a harder eval set instead
of spending the full trial budget on a saturated one.

## Honest limitations

- Executors were `haiku`-class for cost control; larger executors could shift pass rates (the
  historical `commit-conventions` run with a stronger executor showed a +33 pp lift on the same
  evals — today's baseline saturates them, which is itself evidence of drift-by-model-progress).
- Grader sees config names in file paths (partial blinding); mitigated by binary
  reference-guided criteria with quoted evidence.
- Judge and executor share a model family (no cross-family judge available in this environment).
- 3 trials/config (skval's default is 5); `pass^k` error bars are in each scorecard.

## Reproduce

```bash
# assemble any workspace here into a scorecard (deterministic, no model calls):
uv run python skills/skill-validator/scripts/validate_full.py <skill-source> docs/examples/full-runs/<run>
```

The behavioral stages were driven by the agent guides in `skills/skill-validator/agents/`
(executor → grader → artifact-judge → triggering), 14 agents per run.
