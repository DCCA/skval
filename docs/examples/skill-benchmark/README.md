# Skill benchmark — 10 widely-used skills, scored and improved

A real `skval` run over **10 widely-used skills** (Anthropic's public skills, popular examples,
and a Superpowers technique skill), plus two **raw → improved** case studies driven by skval's
own findings.

Scored with the **deterministic structural path** (D1 structure + D6 safety gate — no model
calls), so every number here is reproducible offline:

```bash
uv run skval structural <skill-source> --out skval-runs/<name>
```

The behavioral dimensions (D2 effectiveness / D3 reliability / D4 artifact / D5 triggering)
need model calls and aren't included in this offline benchmark.

## Leaderboard

Ranked by skval (`scripts/batch.py`). Full scorecards are in [`raw/`](raw).

| Rank | Skill | Type | Score | Grade | Verdict | Findings |
|------|-------|------|-------|-------|---------|----------|
| 1 | [mcp-builder](raw/mcp-builder.md) | task | 100 | A | Ship | — |
| 2 | [frontend-design](raw/frontend-design.md) | task | 100 | A | Ship | — |
| 3 | [test-driven-development](raw/test-driven-development.md) | discipline | 100 | A | Ship | — |
| 4 | [pdf](raw/pdf.md) | file_transform | 100 | A | Ship | — |
| 5 | [web-artifacts-builder](raw/web-artifacts-builder.md) | task | 100 | A | Ship | — |
| 6 | [pptx](raw/pptx.md) | file_transform | 100 | A | Ship | — |
| 7 | [canvas-design](raw/canvas-design.md) | file_transform | 100 | A | Ship | — |
| 8 | [xlsx](raw/xlsx.md) | file_transform | 100 | A | Ship | — |
| 9 | [skill-creator](raw/skill-creator.md) | file_transform | 96 | A | Ship | SKILL.md ~8246 tokens (> 5000) |
| 10 | [docx](raw/docx.md) | file_transform | 92 | A | Ship | 599 lines (> 500); ~5142 tokens (> 5000) |

**Takeaways**
- **8 / 10 ship as-is (100 / A).** skval doesn't invent problems — well-built skills score clean.
- The two with findings hit the **size budget** (SKILL.md too big), whose remedy is the same:
  move reference detail into `references/` (progressive disclosure).
- skval also classified each skill's **type** and routed accordingly (file_transform / task /
  discipline) — shown on every scorecard's `Type:` line.

## Wild run — the full installed population

The leaderboard above is curated. For the **unfiltered** set, see
**[wild-skills.md](wild-skills.md)** — a real skval run over **75 installed skills**
(Anthropic plugins, the Vercel suite, Superpowers). It doubles as a **false-positive
regression set**: running skval over real, in-the-wild skills exposed four precision bugs
(a regex in frontmatter read as a link, defensive `rm -rf`/`mkfs` in blocking hooks, an
over-broad `dd` rule, and a too-strict frontmatter allow-list), now fixed and locked in
[`tests/test_precision.py`](../../../tests/test_precision.py). Net after the fixes: **34/75
clean**, the rest splitting into vendored-duplicate `SKILL.md` (e.g. [nextjs](raw/nextjs.md),
77/C/Revise), size budget, vendor-specific keys, and 4 real `rm -rf ~/…`.

## Case study 1 — `docx`: 92 → 100 (real skill)

skval flagged `docx`'s `SKILL.md` as over the size budget. Applying the finding — moving the
`## XML Reference` section into `references/xml-reference.md` — fixed it.

| | Score | Grade | D1 | Findings |
|---|---|---|---|---|
| **Raw** ([scorecard](raw/docx.md)) | 92 | A | 0.92 | 2 (line + token budget) |
| **Improved** ([scorecard](improved/docx.after.md)) | 100 | A | 1.00 | 0 |

skval's own diff ([`improved/docx.compare.json`](improved/docx.compare.json)): `overall_delta: +8`,
D1 `0.92 → 1.00`. What changed: [`improved/docx.change.md`](improved/docx.change.md).

## Case study 2 — `bad-skill`: 73 → 100 (multiple finding types)

A fixture with four common mistakes, fixed one-for-one against skval's findings:

| Raw finding | Fix |
|---|---|
| name `Bad_Name` not kebab-case | → `bad-name` |
| description contains `<` / `>` | removed the angle brackets |
| missing referenced path `scripts/missing.py` | created the referenced file |
| unexpected frontmatter key `foo` | removed it |

Result: **73 / C / Revise → 100 / A / Ship** (skval diff
[`improved/bad-skill.compare.json`](improved/bad-skill.compare.json): `overall_delta: +27`,
verdict `Revise → Ship`). Before: [`improved/bad-skill.before.md`](improved/bad-skill.before.md) ·
After: [`improved/bad-skill.after.md`](improved/bad-skill.after.md).

---

The pattern both cases show is skval's core loop: **score → read the ranked findings → fix →
re-score and confirm the gain.**
