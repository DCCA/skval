# Skill Validator Framework (`skval`) — Product Requirements Document

**Status:** Draft for review · **Date:** 2026-06-18 · **Owner:** dcca12@gmail.com
**Working name:** `skval` (repo) / `skill-validator` (the skill)
**Author of this draft:** Claude (via Superpowers `brainstorming` methodology)

---

## 0. TL;DR

`skval` is a **Claude Code skill** that takes another skill as input — a directory,
a single `SKILL.md`, or a packaged `.skill` reference — runs it through a battery
of **evals and benchmarks**, and returns a **Skill Score (0–100)** with a letter
grade, a per-dimension breakdown, prioritized findings, and a **Ship / Revise /
Reject** verdict.

It is the validation/measurement counterpart to Anthropic's `skill-creator`:
where `skill-creator` helps you *write and iterate*, `skval` exists to *judge*
— rigorously, repeatably, and with defensible methodology grounded in the
agent-evaluation literature (SWE-bench, GAIA, AgentBench, τ-bench) and the
LLM-as-judge literature (Zheng et al. 2023, G-Eval, FLASK, HELM, Miller 2024).

The score is a **gated, normalized weighted composite** over six dimensions, and
it is reported as **both a single headline number and a metric vector** so
trade-offs stay visible.

---

## 1. Problem & Motivation

Skills are proliferating, but "is this skill any good?" is currently answered by
vibes. Authors don't know whether a skill:

- **Actually helps** (vs. the model just doing the task unaided),
- **Helps *reliably*** (or only sometimes — the difference between shippable and dangerous),
- **Triggers at the right times** (fires when relevant, stays silent when not),
- **Is well-built** (clear, correctly structured, safe, token-efficient),
- **Is safe** (no surprising, destructive, or injection-laden instructions).

`skill-creator` contains much of the machinery to answer these (evals, grading,
benchmarking, description optimization) but it is oriented around an *interactive
authoring loop* with a human in the seat at every step. There is no single,
opinionated entry point that says: **"Here is a skill. Give me a score and tell
me if I should ship it."**

`skval` is that entry point.

### Why now / why this shape
- The execution environment has the **`claude` CLI (v2.1.181)**, **subagents**,
  `python 3.11`, `node 22`, `uv`, and `jq` — enough to run skills both via
  subagents (behavioral evals) and via `claude -p` (triggering tests).
- `skill-creator` provides **proven, portable building blocks** (eval/grading
  schemas, `aggregate_benchmark.py`, `quick_validate.py`, grader/analyzer
  agents) we can adapt rather than reinvent.

---

## 2. Goals & Non-Goals

### Goals
1. **One-command-ish validation**: "validate the skill at `<path>`" → a scorecard.
2. **A defensible composite score (0–100)** plus a per-dimension vector and a verdict.
3. **Hybrid evals**: use the skill's bundled evals if present; otherwise auto-generate them.
4. **LLM-as-judge is a first-class scorer** — for grading eval outputs *and* for
   judging the skill artifact — with explicit bias mitigations.
5. **Reliability is measured, not assumed**: repeated trials, `pass^k`, variance/error bars.
6. **Actionable output**: findings ranked by how much they'd raise the score.
7. **All-around**: supports ship-readiness, version comparison, and triggering checks.
8. **Self-contained & portable**: lives in this repo, installable as a Claude Code skill;
   degrades gracefully where subagents or `claude -p` are unavailable.

### Non-Goals (initial)
- **Not a standalone CLI / Python package / web service.** Form factor is a
  Claude Code skill (decided). Scripts are invoked *by the skill*, not exposed as a product CLI.
- **Not a skill *authoring* tool.** `skval` judges; it hands improvement back to the
  human or to `skill-creator`/`writing-skills`. (It *may* emit fix suggestions, not auto-rewrite.)
- **Not a general prompt-eval platform.** Scope is *skills* specifically.
- **Not a security sandbox.** Safety scanning is best-effort static + LLM review, not a guarantee.
- **No fine-tuning / no training.** Pure evaluation.

---

## 3. Users & Use Cases

| User | Use case | Primary dimension(s) |
|---|---|---|
| Skill author | "Is my skill good enough to publish?" | Composite + verdict |
| Skill author (iterating) | "Did my edit actually help / did it regress?" | Effectiveness lift, reliability (version compare) |
| Skill author (discovery) | "Does my skill trigger when it should?" | Triggering accuracy |
| Reviewer / maintainer | "Score these submitted skills consistently" | Composite + findings |
| Curator / marketplace | "Rank a batch of skills" | Composite (batch mode, later) |

**Driving use case (MVP):** ship-readiness scoring of a single skill, with
version-comparison and triggering as fast-follows.

---

## 4. Inputs & Outputs

### 4.1 Inputs (the "insert a skill" resolver)
`skval` accepts any of:
- **A skill directory** — `path/to/skill/` containing `SKILL.md` (+ optional `scripts/`, `references/`, `assets/`, `evals/`).
- **A single `SKILL.md` file** — treated as a one-file skill (structural + artifact + triggering dims fully apply; behavioral evals run on just the SKILL.md).
- **A packaged `.skill` file** — unpacked to a temp dir, then treated as a directory.
- **A reference** — a local path, or a remote URL / `git` reference / GitHub `owner/repo[/path]` that is fetched into a temp dir first (subject to the environment's network policy; fail clearly if unreachable).

The resolver normalizes all of these to a **canonical skill directory** in a
workspace, records provenance (`source`, resolved path, commit hash if git), and
validates that exactly one `SKILL.md` is present.

### 4.2 Outputs (the Scorecard)
Written to a workspace (`skval-runs/<skill-name>/<timestamp>/`):

- **`scorecard.json`** — machine-readable: composite, grade, verdict, per-dimension
  vector (with mean ± stddev and standard error), `pass^k` table, findings,
  metadata (models used, N trials, eval provenance).
- **`scorecard.md`** — the human-readable report (see §8 for the template).
- **`benchmark.json`** — per-run detail in the `skill-creator` schema (so the existing
  `eval-viewer` can render it), extended with `pass_hat_k` and `std_error` fields.
- **Supporting artifacts** — generated evals, per-run transcripts, grading files.

---

## 5. Scoring Model (the heart of `skval`)

### 5.1 Design principles (from the research)
- **Two-tier scoring is universal**: cheap **deterministic** checks first, then
  **LLM-as-judge** for everything qualitative. (promptfoo, OpenAI Evals, Braintrust,
  DeepEval, Inspect, LangSmith, Ragas all do this.)
- **Report a vector *and* a composite.** HELM's lesson: collapsing to one number hides
  trade-offs (the most effective skill may be the least safe). We keep both.
- **Normalize each dimension to 0–1 *before* weighting** (AgentBench "OA" pattern) so a
  wide-range dimension can't dominate.
- **Safety is a gate, not a term.** A safety failure **vetoes** the composite (multiplier
  → 0) rather than being averaged away. (Galtea gating guidance.)
- **Reliability is its own dimension.** A skill that works *sometimes* isn't shippable;
  `pass^k` (τ-bench) turns run-to-run consistency into a score.
- **Atomic, binary criteria over Likert.** "LLMs aren't good at 1–5 scales" — we award
  points per independently-checkable criterion (FLASK/G-Eval/Hamel/Eugene Yan).

### 5.2 The six dimensions

| # | Dimension | Type | What it measures | How scored |
|---|---|---|---|---|
| D1 | **Structural integrity** | Deterministic | Frontmatter validity, naming, description rules, single-`SKILL.md`, token budget, broken refs, progressive-disclosure hygiene | Static checks (port `quick_validate.py` + extensions); fraction of checks passed → 0–1 |
| D2 | **Effectiveness** | Behavioral (LLM-judge graded) | Does the skill achieve task goals, and **how much better than no skill** (baseline lift)? | With-skill vs no-skill eval runs; graded pass rate + delta |
| D3 | **Reliability** | Behavioral | Consistency across repeated independent trials | `pass^k` + variance (mean ± stddev, std error) |
| D4 | **Artifact quality** | Intrinsic LLM-judge | Clarity, instruction design, completeness, examples, writing-skills best-practices | Decomposed rubric, binary criteria, CoT + evidence |
| D5 | **Triggering accuracy** | Behavioral (CLI) | Fires on should-trigger queries, stays silent on should-not | Precision / recall / F1 over generated query set |
| D6 | **Safety / least-surprise** | Deterministic + LLM gate | Malicious, destructive, injection, or surprising content | Static patterns + LLM review → **gate (0/1)** |

**Cost** (tokens/latency overhead the skill adds vs. baseline) is **reported
alongside** the score and may apply a small, capped penalty to D2; it is never a
large positive/negative term on its own (mirrors how SWE-bench/τ-bench report
cost as context, not the prize).

### 5.3 Composite formula

```
normalized dᵢ ∈ [0,1]   for i in {D1, D2, D3, D4, D5}
safety_gate ∈ {0, 1}    (D6: 1 = pass, 0 = veto)

raw = Σ (wᵢ · dᵢ)
SkillScore = round( 100 · safety_gate · raw )      # 0 if safety fails
```

**Default weights** (configurable in `references/scoring-rubric.md`):

| Dimension | Weight | Rationale |
|---|---|---|
| D2 Effectiveness | **0.30** | The point of a skill is to help; this is the strongest signal. |
| D3 Reliability | **0.20** | Consistency gates shippability (τ-bench insight). |
| D4 Artifact quality | **0.20** | Predicts generalization beyond the eval set; the "LLM judge" core. |
| D5 Triggering | **0.15** | A skill that never fires is worthless regardless of quality. |
| D1 Structural | **0.15** | Necessary hygiene; cheap; gameability-resistant floor. |
| D6 Safety | **gate** | Veto multiplier, not a weighted term. |

> Weights are a **starting hypothesis** to be calibrated during dogfooding (§12) so
> the composite correlates with human judgment on a labeled set of known-good and
> known-bad skills.

### 5.4 Grade bands & verdict

| Score | Grade | Verdict | Meaning |
|---|---|---|---|
| 90–100 | A | **Ship** | Strong, reliable, safe. |
| 80–89 | B | **Ship** | Good; minor findings. |
| 70–79 | C | **Revise** | Useful but has real gaps. |
| 50–69 | D | **Revise** | Significant problems; not ready. |
| 0–49 | F | **Reject** | Ineffective, unreliable, or unsafe. |
| any, safety=0 | F | **Reject** | Safety veto, regardless of other dimensions. |

### 5.5 Variance & significance (so the score is trustworthy)
- Every behavioral eval runs **N independent trials** (default **N=5**; configurable).
- Report **mean ± stddev** and the **standard error of the mean** per dimension.
- For comparisons (with vs. without skill; version A vs. B), a delta is reported as
  **significant only if it exceeds the standard error of the difference**
  (`√(SE₁² + SE₂²)`, Miller 2024 / Anthropic). Sub-threshold deltas are shown as "≈ no change."
- **`pass^k`** (D3) is computed per τ-bench: with `c` successes out of `n` trials,
  `pass^k = mean over evals of C(c,k)/C(n,k)`. `pass^1` is plain success rate; the
  decay as `k` grows is the reliability signal.

---

## 6. LLM-as-Judge Design (your "the LLM has to judge too" requirement)

The judge appears in **two places**: grading **behavioral eval outputs** (D2) and
scoring the **skill artifact** (D4). Both adopt the same hardened methodology.

### 6.1 Methodology
- **Decomposed rubric, binary/atomic criteria.** Each criterion is an independently
  checkable yes/no with cited evidence (adapted from `skill-creator`'s `grader.md`
  and FLASK/G-Eval). No holistic 1–5 scores.
- **Chain-of-thought + evidence.** The judge must quote the transcript/artifact line
  that justifies each verdict (G-Eval form-filling; grader.md "evidence" field).
- **Reference-guided where possible.** When an eval has an expected output / gold
  target, supply it to the judge (reference-guided grading sharply cuts error rates).
- **Eval self-critique.** The grader also flags non-discriminating assertions (ones a
  wrong output would still pass) — directly from `grader.md`.

### 6.2 Bias mitigations (explicit, cited)

| Bias | Mitigation in `skval` | Source |
|---|---|---|
| **Self-preference** (judge favors its own family's output) | Judge with a **different model** than the executor where available; **blind the judge to provenance** (never tell it which model/version produced an output) | Panickssery, Bowman & Feng 2024 (causal) |
| **Position bias** (favors first/second) | **Position-swapping** on every pairwise comparison; require consistent verdict across both orders or score a tie | Zheng et al. 2023 |
| **Verbosity bias** (favors longer) | Atomic rubric scores content, not length; length is a separate reported metric, never a criterion | Zheng et al. 2023; FLASK |
| **Judge nondeterminism** | N trials + mean ± stddev; flag high-variance criteria | HF eval guidebook; Miller 2024 |

> Note on sourcing: the original self-enhancement finding (Zheng 2023) is
> *underpowered* (the authors decline to confirm it); we cite the **causal** 2024
> follow-up as the basis for provenance-blinding.

### 6.3 Models
- **Executor** (runs the skill in evals): the session's model / a capable default.
- **Judge** (grades & scores): a capable model, **preferably a different family**;
  if only one family is available, blind provenance and disclose the limitation in the scorecard.
- All model IDs are recorded in `scorecard.json` metadata for reproducibility.

---

## 7. Pipeline / Architecture

```
            ┌─────────────────────────────────────────────────────────────┐
 input ───▶ │ 0. Resolve skill (dir / .md / .skill / reference) → canonical │
            └─────────────────────────────────────────────────────────────┘
                       │
   ┌───────────────────┼───────────────────────────────────────────────┐
   ▼                   ▼                                                 ▼
┌──────────┐   ┌───────────────────┐                          ┌──────────────────┐
│ 1. STATIC │   │ 2. EVAL RESOLUTION │                          │ 6. SAFETY (gate) │
│  (D1)     │   │  bundled? use it.  │                          │  static + LLM    │
│ determin- │   │  else auto-gen +   │                          │  → 0/1 veto      │
│  istic    │   │  (offer) review    │                          └──────────────────┘
└──────────┘   └───────────────────┘
                       │ evals + triggering query set
        ┌──────────────┼───────────────────────────┐
        ▼                                            ▼
┌───────────────────────────────┐        ┌──────────────────────────┐
│ 3. BEHAVIORAL RUNS (subagents) │        │ 5. TRIGGERING (claude -p) │
│  with-skill vs no-skill,       │        │  should/should-not queries │
│  N trials each → transcripts   │        │  → precision/recall/F1     │
└───────────────────────────────┘        └──────────────────────────┘
        │                                            │ (D5)
        ▼
┌───────────────────────────────┐
│ 4a. GRADE outputs (LLM judge)  │  → pass rate, baseline lift (D2)
│ 4b. JUDGE artifact (LLM judge) │  → rubric score (D4)
└───────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│ 7. AGGREGATE & SCORE: normalize dims, pass^k, error bars, gate,     │
│    weighted composite → grade → verdict → findings → scorecard.*    │
└───────────────────────────────────────────────────────────────────┘
```

### 7.1 Execution model
- **Behavioral runs (D2/D3):** spawn **subagents** — one executor *with* the skill, one
  *baseline* without — per eval per trial, exactly as `skill-creator` does. Capture
  outputs, transcript, tokens, time, tool calls.
- **Triggering (D5):** use **`claude -p`** to present queries to a model that does/doesn't
  have the skill available, and detect activation (port the approach in
  `skill-creator/scripts/improve_description.py` / `run_loop.py`).
- **Grading & artifact judging (D4):** subagent or `claude -p` judge calls.
- **Fallbacks:** if subagents are unavailable, run sequentially via `claude -p`; if
  `claude -p` is unavailable too, run **static + artifact-judge only** and clearly mark
  the scorecard as "structural/artifact-only (behavioral dims skipped)."

### 7.2 Form factor & repo layout (Claude Code skill)
```
skval/
├── skills/
│   └── skill-validator/
│       ├── SKILL.md                      # entry point + workflow (< 500 lines)
│       ├── scripts/
│       │   ├── resolve_skill.py          # input resolver → canonical dir
│       │   ├── static_checks.py          # D1 (extends quick_validate.py)
│       │   ├── safety_scan.py            # D6 static pass
│       │   ├── aggregate.py              # mean/stddev/delta + pass^k + std error
│       │   ├── score.py                  # normalize → gate → weighted composite → grade
│       │   └── generate_scorecard.py     # scorecard.json + scorecard.md
│       ├── agents/
│       │   ├── eval-generator.md         # auto-generate evals + triggering queries
│       │   ├── executor.md               # run skill on an eval (with/without)
│       │   ├── grader.md                 # D2 grade outputs (adapted)
│       │   ├── artifact-judge.md         # D4 rubric scoring of SKILL.md
│       │   └── analyzer.md               # findings synthesis (adapted)
│       ├── references/
│       │   ├── scoring-rubric.md         # dimensions, weights, bands (source of truth)
│       │   ├── judge-methodology.md      # bias mitigations, prompts
│       │   ├── schemas.md                # scorecard.json / benchmark.json schemas
│       │   └── methodology.md            # benchmark grounding (§11 distilled, cited)
│       └── assets/
│           └── scorecard-template.md
├── docs/
│   └── prd/skill-validator-prd.md        # this document
├── tests/                                # TDD fixtures: known-good & known-bad skills
└── README.md                             # what it is, install, usage
```
Installable by copying `skills/skill-validator/` into `~/.claude/skills/` or via a
plugin manifest (later). MVP keeps it a plain skill directory.

### 7.3 Reused / adapted from `skill-creator`
- `quick_validate.py` → basis for D1 static checks.
- `aggregate_benchmark.py` → basis for `aggregate.py` (extend with `pass^k`, std error).
- `agents/grader.md`, `agents/analyzer.md` → adapted for D2 grading and findings.
- `references/schemas.md` + `eval-viewer/` → reuse `benchmark.json` shape so the
  existing viewer renders `skval` runs for free.
- `evals.json` schema → the bundled-eval format `skval` reads in hybrid mode.

> We **port/adapt** these into this repo (clean, self-contained) rather than depend on
> `/mnt/skills`, which may not exist in every environment.

---

## 8. The Scorecard (illustrative output)

```markdown
# Skill Scorecard — `pdf-form-filler`
Source: ./skills/pdf-form-filler (git @a1b2c3d) · 2026-06-18
Models: executor=claude-sonnet, judge=claude-opus (cross-family ✓) · Trials: N=5

## ███████████░░░  78 / 100   Grade: C   Verdict: REVISE

| Dimension            | Score | Detail |
|----------------------|-------|--------|
| Effectiveness (D2)   |  84   | with-skill 86% ± 4% vs baseline 41% ± 7% → +45% (significant) |
| Reliability (D3)     |  62   | pass^1 0.86, pass^3 0.61 — drops under repetition |
| Artifact quality (D4)|  80   | clear; missing a worked example; 1 vague step |
| Triggering (D5)      |  90   | precision 0.92, recall 0.88, F1 0.90 |
| Structural (D1)      |  75   | SKILL.md 612 lines (>500); 1 broken ref |
| Safety (D6)          | PASS  | no destructive/injection patterns found |

Cost: +13s, +1,700 tokens avg vs baseline (acceptable).

## Top findings (ranked by score impact)
1. [Reliability +~9] Eval "multi-page form" passes 2/3 — non-deterministic field
   detection. Add the deterministic `detect_fields.py` step.
2. [Structural +~4] Split SKILL.md (612→<500 lines); move OOXML notes to references/.
3. [Artifact +~3] Step 4 ("process appropriately") is vague — specify the 3 sub-steps.
4. [Structural +~2] `references/ocr.md` linked but missing.
```

The same data lives in `scorecard.json` for automation.

---

## 9. Hybrid Eval Resolution (decided: hybrid)

1. **If `evals/evals.json` exists** in the skill → use it (the `skill-creator` schema:
   `prompt`, `expected_output`, `files`, `expectations`).
2. **Else auto-generate**: the `eval-generator` agent reads the skill and synthesizes
   **3–5 representative task prompts** with **discriminating expectations** (assertions
   a wrong output would *fail* — per `grader.md` guidance), plus a **triggering query
   set** (8–10 should-trigger + 8–10 near-miss should-not-trigger, per
   `improve_description` guidance).
3. **Offer a review gate**: present generated evals for the user to edit/approve before
   running (skippable for fully-automated mode). Bad evals → bad scores, so this matters.
4. Generated evals are saved to the workspace so a run is reproducible and the author can
   adopt them into the skill.

---

## 10. Build Plan & Methodology (using Superpowers, as requested)

We build `skval` with the Superpowers workflow:

1. **`brainstorming`** → this PRD (spec). ← *we are here*
2. **`writing-plans`** → a bite-sized, TDD, file-by-file implementation plan in
   `docs/superpowers/plans/`.
3. **`using-git-worktrees`** (optional) → isolated branch workspace.
4. **`test-driven-development`** → RED→GREEN→REFACTOR for every script (deterministic
   logic — scoring math, `pass^k`, static checks, resolver — is unit-testable first).
5. **`writing-skills`** → the SKILL.md and agent prompts are built TDD-style: write
   pressure/usage scenarios, watch baseline fail, write the skill, watch it pass.
6. **`subagent-driven-development`** *or* **`executing-plans`** → execute the plan.
7. **`verification-before-completion`** + **`requesting-code-review`** /
   **`receiving-code-review`** → quality gates.
8. **`finishing-a-development-branch`** → commit & push to `claude/vigilant-ptolemy-qyc153`.

### Milestones / phasing
- **M0 — Skeleton & deterministic core (MVP-α):** resolver + D1 static checks + D6 static
  safety + scoring/aggregation math (`pass^k`, error bars) + scorecard generation, all
  unit-tested. *No model calls yet* → fast, fully testable. Produces a partial (structural-only) scorecard.
- **M1 — Behavioral + judge (MVP):** eval resolution (hybrid) + executor/baseline subagent
  runs + D2 grading + D4 artifact judge + composite over D1/D2/D4/D6. **This is the first
  "give it a skill, get a real score" release.**
- **M2 — Reliability & triggering:** formal `pass^k` (N trials), D5 triggering via
  `claude -p`, full six-dimension composite, eval-viewer integration.
- **M3 — Comparison & polish:** version-vs-version (pairwise + position-swap),
  regression history, batch mode, plugin packaging, calibration (§12).

---

## 11. Benchmark Grounding & Prior Art (the "use benchmarks" requirement)

Every major design choice is anchored in established evaluation work.

### 11.1 Agent benchmarks → behavioral scoring
- **SWE-bench / SWE-bench Verified** — execution-grounded binary scoring via the repo's
  own tests; an instance is *resolved* only if `FAIL_TO_PASS` **and** `PASS_TO_PASS`
  both hold. → **`skval` scores effect *and* non-regression**, and prefers
  execution/assertion-grounded checks over opinion where possible.
  (arxiv 2310.06770; openai.com/index/introducing-swe-bench-verified/)
- **GAIA** — one unambiguous gold answer per task, graded by cheap **quasi-exact match**;
  difficulty **tiers** by number of steps/tools. → **`skval` uses gold-target /
  reference-guided checks where available and can tier evals by difficulty.**
  (arxiv 2311.12983)
- **AgentBench** — heterogeneous per-environment metrics (success rate / reward / F1)
  **normalized then averaged** into one "Overall" score. → **`skval` normalizes each
  dimension to 0–1 before weighting** so no dimension's scale dominates.
  (arxiv 2308.03688)
- **τ-bench** — reward requires correct **end state** *and* correct **information
  returned**; introduces **`pass^k`** over N independent trials to measure
  *consistency*. → **`skval` adopts `pass^k` as the Reliability dimension (D3)** — the
  single most important idea for validating a skill, because a skill that helps only
  sometimes is not shippable. (arxiv 2406.12045)

### 11.2 LLM-as-judge → D2/D4 grading
- **Zheng et al. 2023 (MT-Bench / Chatbot Arena)** — strong LLM judges reach ~80%
  agreement with humans (≈ human–human); names **position / verbosity /
  self-enhancement** biases; mitigations: **position-swap**, **few-shot judge**,
  **reference-guided** grading. (arxiv 2306.05685; FastChat source)
- **G-Eval** — CoT + **form-filling**, probability-weighted scores; strong human
  correlation. → judge prompts use CoT + per-criterion evidence. (arxiv 2303.16634)
- **FLASK / Prometheus** — **fine-grained, decomposed rubrics** beat holistic scores on
  reliability and reduce length bias. → D4 is a decomposed atomic rubric.
  (arxiv 2307.10928; 2310.08491)
- **Panickssery, Bowman & Feng 2024** — LLMs **recognize and favor their own
  generations** (causal). → **blind provenance / cross-family judging.** (arxiv 2404.13076)
- **HELM** — report a **metric vector**, don't collapse to one number. → scorecard keeps
  the vector beside the composite. (arxiv 2211.09110)
- **Practitioner consensus (Hamel; Eugene Yan)** — **binary pass/fail > 1–5 Likert** for
  LLM judges. → atomic binary criteria throughout.

### 11.3 Eval tooling → mechanics we mirror
- **Two-tier scoring** (deterministic checks + `llm-rubric`/`G-Eval`/`model_graded_qa`)
  is universal across **promptfoo, OpenAI Evals, Braintrust, DeepEval, Inspect,
  LangSmith, Ragas**. → D1/D6-static (deterministic) + D2/D4 (LLM-judge).
- **Pairwise comparison** (LangSmith `evaluate_comparative`, OpenAI/Braintrust `battle`,
  promptfoo matrix) → version-vs-version mode (M3).
- **CI-style gating via thresholds** (DeepEval `assert_test`, promptfoo exit codes) →
  the verdict + safety gate are the gating mechanism.

### 11.4 Statistics → trustworthy numbers
- **Miller 2024 / Anthropic "Adding Error Bars to Evals"** — eval items are a sample;
  report **standard error**, use **paired differences** and judge deltas by the
  **standard error of the difference**. → §5.5. (arxiv 2411.00640)
- **Bootstrap CIs** (LMSYS Arena), **mean ± stddev** over N runs (HF guidebook) →
  variance reporting.

### 11.5 Direct predecessor — Anthropic `skill-creator`
Provides the concrete, portable machinery `skval` adapts: `evals.json` /
`grading.json` (with `pass_rate`) / `benchmark.json` (`with_skill` vs `without_skill`,
mean ± stddev, delta) schemas; `aggregate_benchmark.py`; `quick_validate.py`;
grader/analyzer/comparator agents; description-triggering optimization; and the
**principle of least surprise** (→ D6). `skval` repackages the *measurement* half of
`skill-creator` behind a single scoring entry point.

---

## 12. How we know `skval` itself is good (meta-evaluation)
- **Dogfood corpus:** assemble a labeled set of **known-good** skills (e.g. mature public
  skills) and **known-bad** ones (deliberately broken: vague steps, no triggering,
  unsafe content). `skval` must rank them sensibly.
- **Calibration:** tune dimension weights (§5.3) so the composite **correlates with human
  judgment** on that corpus (target: high rank correlation; A/F extremes never inverted).
- **Reproducibility:** same skill + same N → scores within reported error bars.
- **Self-application:** `skval` validates itself (the `skill-validator` skill) and should
  score well — a built-in smoke test.

---

## 13. Risks & Open Questions

| Risk | Mitigation |
|---|---|
| LLM-judge **cost/latency** | Deterministic-first; configurable N; judge only what static checks can't; cache by skill content hash. |
| **Auto-generated evals** may be weak | User review gate; discriminating-assertion guidance; grader self-critique flags weak assertions. |
| **Single model family** available (self-preference) | Blind provenance; disclose limitation in scorecard metadata. |
| **Nondeterminism** inflates/deflates scores | N trials, error bars, `pass^k`, significance threshold on deltas. |
| **Environment lacks** subagents / `claude -p` | Graceful degradation to structural+artifact-only, clearly marked. |
| **Gaming** the score | Heavy weight on execution-grounded D2/D3 + structural floor; safety veto. |
| Skill needs **special inputs/tools** to run | `evals[].files` support; document tool/dependency assumptions; mark un-runnable evals as skipped, not failed. |

**Resolved (PRD review, 2026-06-18):**
1. **Default N trials = 5** (tighter error bars; still configurable).
2. **Auto-eval review gate = ON** by default (user approves generated evals); a skip flag is available for hands-free runs.
3. **Skill name = `skill-validator`** (parity with `skill-creator`).
4. **Repo layout = `skills/skill-validator/`** (plugin-style, room to grow).

---

## 14. Acceptance Criteria (for the framework, MVP = M1)
- [ ] Given a skill directory, `.md`, `.skill`, or reference, `skval` produces
      `scorecard.json` + `scorecard.md` with a 0–100 composite, grade, and verdict.
- [ ] Hybrid evals: uses bundled `evals/evals.json` when present; auto-generates otherwise.
- [ ] D2 effectiveness reports with-skill vs no-skill pass rates **with error bars** and a
      significance-aware delta.
- [ ] D4 artifact judging uses a **decomposed binary rubric with cited evidence** and
      **provenance-blinded** judging.
- [ ] D6 safety acts as a **hard gate** (unsafe ⇒ Reject regardless of other scores).
- [ ] Composite is a **normalized, gated weighted sum**; scorecard shows the **vector**.
- [ ] All deterministic logic (resolver, static checks, scoring math, `pass^k`, error
      bars) has **unit tests** (built TDD).
- [ ] Degrades gracefully and says so when behavioral execution isn't possible.
- [ ] `skval` scores itself and a known-bad fixture sensibly (smoke test).

---

## 15. Decisions locked (from kickoff)
- **Eval source:** Hybrid (bundled-if-present, else auto-generate). ✓
- **Score:** Composite (0–100) + breakdown vector; **LLM-as-judge is part of scoring**
  (grades outputs *and* judges the artifact). ✓
- **Form factor:** **Claude Code skill** (subagents + `claude -p`); no standalone CLI. ✓
- **Primary goal:** All-around validator (ship-readiness + version compare + triggering),
  delivered in phases. ✓
- **Trials N = 5; auto-eval review gate ON; skill name `skill-validator`; layout
  `skills/skill-validator/`.** ✓ (PRD review, 2026-06-18)

---

*End of PRD. Next step on approval: invoke `writing-plans` to produce the bite-sized,
test-first implementation plan for Milestone M0 → M1.*
