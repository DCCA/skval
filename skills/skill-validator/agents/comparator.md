# Comparator (skval) — version A/B

Decide whether version **B** (candidate) is better than version **A** (baseline/old).
Two levels; use both when it matters.

## Level 1 — scorecard diff (cheap, deterministic)
Validate both versions (full run each, ideally reusing the same generated evals), then:
```python
import compare
diff = compare.compare_scorecards(card_a, card_b)
```
`diff` gives the overall score delta, per-dimension deltas, and `significant` flags
(true only when a delta clears the standard error of the difference). Prefer this first —
if B wins clearly and significantly, you may not need Level 2.

## Level 2 — blind pairwise judging (for close calls)
For a given eval, judge the two outputs head-to-head with an LLM, controlling for bias:
- **Blind provenance:** label the outputs only "Output 1 / Output 2"; never reveal which
  is the old/new version or which model produced them (self-preference is causal —
  Panickssery et al. 2024).
- **Position-swap (required):** run the judge **twice** — once with [A, B], once with
  [B, A]. Record each winner as the *original* label ("A", "B", or "tie").
- Collapse the two orders:
```python
verdict = compare.decide_pairwise(winner_when_AB, winner_when_BA)  # "A" | "B" | "tie"
if compare.position_bias_detected(winner_when_AB, winner_when_BA):
    note = "judge showed position bias; treating as tie"
```
Only a winner consistent across both orders counts; disagreement collapses to a tie.

## Output — `workspace/comparison.json`
```json
{
  "level1": {"overall_delta": 7, "dimensions": {"D2": {"delta": 0.12, "significant": true}}},
  "level2": [{"eval_id": 0, "winner_ab": "B", "winner_ba": "B", "verdict": "B", "position_bias": false}],
  "summary": "B wins: +7 overall (D2 +0.12 significant); pairwise B 1, tie 0."
}
```
