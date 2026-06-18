# Grader (skval) — D2

Grade one execution run's outputs against its eval expectations. Dispatch as a fresh
subagent (or run inline) per run. Adapted from Anthropic skill-creator's grader.

## Inputs
- `expectations` — the eval's list of assertions.
- `outputs_dir` — `run_dir/outputs/` with the deliverables (+ optional `metrics.json`, `user_notes.md`).
- `transcript_path` — `run_dir/transcript.md`.
- `expected_output` (optional) — a gold/reference description; **use it when present**
  (reference-guided grading is markedly more reliable).

## Process
1. Read the transcript and **examine the output files themselves** — don't trust the
   transcript's claims about what it produced. For spreadsheet/binary deliverables,
   **evaluate computed values** (load with the right library; recalculate formulas if
   needed) — a good skill often emits formulas like `=SUM(...)`, so a raw value scan can
   miss a correct answer.
2. For each expectation, decide **PASS/FAIL** with **cited evidence** (quote the file
   content or transcript line). No partial credit; no holistic score.
   - PASS only when the evidence reflects genuine task completion, not surface compliance
     (right filename but empty/wrong content = FAIL).
3. **Critique the evals:** flag any assertion that a clearly-wrong output would still pass,
   or any important outcome no assertion covers.
4. **Multi-turn evals:** read `run_dir/transcript.json` and grade interaction expectations
   (e.g. "asks ≥2 questions before delivering", "asks about budget before ordering). Use
   `scripts/conversation.py` for the objective counts (`questions_before_delivery`,
   `asked_about`) and cite the specific turn(s) as evidence.

## Output — `run_dir/grading.json`
Write **only raw JSON** to this file — no Markdown ` ``` ` fences and no prose before or
after; the scorer parses the file directly and silently drops a run whose JSON is malformed.
```json
{
  "expectations": [
    {"text": "Output includes the computed margin 23.4%", "passed": true,
     "evidence": "report.md line 4: 'Margin: 23.4%'"}
  ],
  "summary": {"passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67},
  "eval_feedback": {"suggestions": [{"assertion": "...", "reason": "..."}], "overall": "..."}
}
```
`summary.pass_rate` (0.0–1.0) is what `aggregate.py` reads. A run counts as a full
success for `pass^k` only when `pass_rate == 1.0`.
