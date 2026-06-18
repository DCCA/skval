# Artifact Judge (skval) — D4

Judge the **skill artifact itself** (the SKILL.md + bundled resources) against a
decomposed, binary rubric. This is the LLM-as-judge for D4. Use a judge model from a
**different family** than the executor when possible, and never reveal who authored the
skill (provenance-blind). Score each criterion independently — no holistic 1–5 score.

## Inputs
- `skill_dir` — the skill to judge. Read `SKILL.md` and skim referenced files.

## Method
For each criterion below, decide **passed: true/false** and cite **evidence** (quote or
point to the specific line/section). Reason step by step before deciding. Judge content,
**not length** — a longer skill is not automatically better.

## Rubric (each criterion is binary)
| id | Passes when |
|----|-------------|
| `description_triggering` | The `description` states *when to use* (concrete triggers/symptoms), not merely what it does. |
| `overview_clear` | An overview states the purpose and core principle in 1–2 sentences. |
| `instructions_actionable` | Steps are concrete and unambiguous — no vague "process appropriately". |
| `progressive_disclosure` | SKILL.md stays focused; heavy detail lives in `references/` or scripts. |
| `example_present` | At least one concrete, adaptable example exists (or N/A is clearly justified for a pure-reference skill). |
| `output_defined` | The expected output/format is specified where the task has one. |
| `self_contained` | A fresh agent could follow it without missing context or dangling references. |
| `appropriately_scoped` | Focused on one coherent capability, not many unrelated ones. |

## Output — `workspace/artifact_judgment.json`
```json
{
  "criteria": [
    {"id": "description_triggering", "passed": true, "evidence": "description starts 'Use when...'"},
    {"id": "instructions_actionable", "passed": false, "evidence": "Step 4 says 'handle it appropriately'"}
  ],
  "notes": "Optional overall observations."
}
```
`dimensions.d4_artifact` scores D4 as the fraction of criteria passed.
