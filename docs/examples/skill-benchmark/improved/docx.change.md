# docx — improvement applied

**skval finding (raw → 92 / A):**
1. `[D1]` SKILL.md is 599 lines (> 500); consider splitting
2. `[D1]` SKILL.md ~5142 tokens (> 5000); move detail to references/

**Fix (exactly what the finding recommends — progressive disclosure):**
Moved the dense `## XML Reference` section (~128 lines) out of `SKILL.md` into
`references/xml-reference.md`, leaving a short pointer + link in its place. Only `SKILL.md`
and the new `references/xml-reference.md` changed; `scripts/` was untouched, so no references
break.

**Result:** `SKILL.md` 599 → 473 lines, ~5142 → under 5000 tokens → **re-scored 100 / A, no findings.**

Reproduce:
```bash
cp -r /path/to/docx ./docx-improved
# move the "## XML Reference" body into references/xml-reference.md, leave a linked pointer
uv run skval structural ./docx-improved      # 92 -> 100
```
See [`docx.compare.json`](docx.compare.json) for skval's own before/after diff (`overall_delta: +8`).
