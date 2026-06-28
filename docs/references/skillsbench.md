# SkillsBench reference note

Source: [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://arxiv.org/abs/2602.12670)  
DOI: <https://doi.org/10.48550/arXiv.2602.12670>  
Current arXiv version consulted: v4, last revised 2026-06-14

## Why this matters for skval

SkillsBench provides a research-backed framing for the problem `skval` is trying to make practical: **Agent Skills should be evaluated as measurable runtime artifacts**, not treated as prompt/documentation assets that are assumed to help.

Where SkillsBench is a broad benchmark across tasks, domains, models, and agent harnesses, `skval` is intended to be the local, CI-friendly validation layer for individual Claude skills.

## Current arXiv abstract facts to preserve

- Agent Skills are structured procedural-knowledge packages that augment LLM agents at inference time.
- SkillsBench evaluates matched **no-Skills** vs **curated-Skills** conditions.
- Current inventory: **87 tasks** across **8 domains**.
- Latest aggregate evaluation: **18 model-harness configurations**.
- Curated Skills raise average pass rate from **33.9%** to **50.5%**.
- Absolute gain: **+16.6 percentage points**.
- Normalized gain: **25.5%**.
- Configuration-level gains range from **+4.1pp** to **+25.7pp**.
- Focused Skills with at most **three modules** outperform larger or exhaustive bundles.
- Smaller models with Skills can match larger models without Skills.
- Evaluation uses deterministic verifiers rather than only subjective judgment.

Note: earlier public snippets for v1 describe 86 tasks / 11 domains / 7 configurations and include self-generated Skills. Prefer the current arXiv v4 abstract for headline numbers unless intentionally discussing version history.

## Design implications for skval

### 1. Treat paired evaluation as the center of D2

`skval` already models D2 Effectiveness as **with-skill vs no-skill pass rate + baseline lift**. SkillsBench strengthens that design choice and gives us language for why this is the core signal.

Future improvement: make the paired-eval output more visible in scorecards:

```text
No-skill pass rate:    X%
With-skill pass rate:  Y%
Absolute lift:         +Z pp
Normalized gain:       G%
```

### 2. Prefer focused skill bundles

SkillsBench reports that focused Skills with at most three modules outperform larger or exhaustive bundles. `skval` can turn this into a structural/artifact-quality signal:

- warn on overly large `SKILL.md` files;
- flag too many always-loaded modules;
- reward progressive disclosure;
- report token/context overhead as a cost metric;
- suggest moving long docs into `references/` rather than main instructions.

### 3. Keep deterministic verifiers first-class

SkillsBench relies on deterministic verifiers. `skval` should keep pushing skills toward evals that can be checked by scripts, fixtures, assertions, or explicit rubrics before falling back to LLM judgment.

Future improvement: add a scorecard field for verifier strength:

```text
verifier_strength: deterministic | hybrid | llm_judge_only | manual
```

### 4. Evaluate model + harness + skill together

SkillsBench reports at the model-harness configuration level because harness behavior affects skill discovery and usage. `skval` should record:

- model;
- harness / agent runtime;
- skill-loading mechanism;
- skill invocation/triggering evidence;
- tool availability;
- number of trials.

### 5. Position skval clearly

Suggested positioning language:

> skval is SkillsBench-lite for real-world Claude skills: a repeatable validator that measures whether a skill actually improves agent behavior before you ship it.

Alternative:

> The missing eval layer for Claude Skills.

## Potential future repo improvements

- Add a `paired-eval` command or documented workflow with explicit no-skill vs with-skill output.
- Add normalized gain to D2 alongside absolute lift.
- Add context-overhead / module-count heuristics informed by the focused-vs-exhaustive result.
- Add an example scorecard showing a skill before and after improvement.
- Add a short “Research basis” section to README linking this note.
- Add CI examples where a skill must keep a minimum score or avoid regression.

## Citation

```bibtex
@misc{li2026skillsbench,
  title = {SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks},
  author = {Li, Xiangyi and Liu, Yimin and Chen, Wenbo and others},
  year = {2026},
  eprint = {2602.12670},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  doi = {10.48550/arXiv.2602.12670},
  url = {https://arxiv.org/abs/2602.12670}
}
```
