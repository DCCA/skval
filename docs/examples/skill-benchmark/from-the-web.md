# From the web — skval over real published skills

A real `skval` **structural** run over **123 community skills** pulled from four public
GitHub collections — [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills),
[glebis/claude-skills](https://github.com/glebis/claude-skills),
[smartnews/claude-skills](https://github.com/smartnews/claude-skills), and
[anthropics/skills](https://github.com/anthropics/skills) — deterministic, no model calls.
Most are well-built; this page is about the ones skval flags, and what fixing them looks like.

> **Safety first.** Every fetched skill was treated as **inert text** and run through skval's
> D6 safety gate *before* anything else. **0 / 123** tripped it, and none were ever executed —
> only the `SKILL.md` text was read and statically analysed.
>
> *(Symlink/pointer entries — where the raw file is just a path to another location — were
> excluded; they aren't real skill content.)*

## What skval found

Most skills score a clean 100 / A. The genuine sub-100 classes:

| Class | What it is | Severity |
|-------|------------|----------|
| **Invalid YAML frontmatter** | an unquoted colon in `description` (e.g. `Local-only: synthetic…`) breaks the YAML, so the skill has no usable name/description | critical → Revise/Reject |
| **`<` / `>` in `description`** | angle brackets break some parsers and the triggering surface | major |
| **Oversized `SKILL.md`** | over the size budget; remedy is progressive disclosure (`references/`) | minor |

## The skval upgrade these skills drove

The **invalid-YAML class used to crash skval** — `parse_frontmatter` caught `ValueError`
but not `yaml.YAMLError`, so a malformed real-world skill raised instead of being scored. A
validator has to survive the messy real world, so skval now reports invalid frontmatter as a
finding and scores the skill. Pinned in
[`tests/test_precision.py`](../../../tests/test_precision.py)
(`test_invalid_yaml_frontmatter_scores_not_crashes`).

## Case studies — score → fix → re-score

Real published skills, scored verbatim, then fixed against skval's ranked findings and
re-scored. Every "after" is the actual re-score of the fixed skill (no remaining findings).

| Skill | Source | Finding class | Before | After | Δ |
|-------|--------|---------------|:------:|:-----:|:--:|
| [`daydream`](https://github.com/glebis/claude-skills) | glebis | no frontmatter at all | [38 / F / Reject](improved/web-daydream.before.md) | [100 / A / Ship](improved/web-daydream.after.md) | **+62** |
| [`disk-cleanup`](https://github.com/glebis/claude-skills) | glebis | invalid YAML frontmatter | [50 / D / Revise](improved/web-disk-cleanup.before.md) | [100 / A / Ship](improved/web-disk-cleanup.after.md) | **+50** |
| [`annotate`](https://github.com/glebis/claude-skills) | glebis | invalid YAML frontmatter | [50 / D / Revise](improved/web-frontmatter.before.md) | [100 / A / Ship](improved/web-frontmatter.after.md) | **+50** |
| [`rehydrate`](https://github.com/glebis/claude-skills) | glebis | `<` / `>` in description | [92 / A / Ship](improved/web-rehydrate.before.md) | [100 / A / Ship](improved/web-rehydrate.after.md) | **+8** |

**The fixes are tiny, one each:**

- **`daydream`** had *no YAML frontmatter* — no `name`, no `description`, so it can't trigger.
  Adding a frontmatter block takes it from **38 / F / Reject → 100 / A / Ship** (skval's biggest
  turnaround in the set, `overall_delta +62`). What changed:
  [`web-frontmatter.change.md`](improved/web-frontmatter.change.md) shows the same class on `annotate`.
- **`disk-cleanup` / `annotate`** ship an unquoted colon in `description` (`… Local-only: synthetic …`)
  that breaks the YAML — quote the description and both go **50 → 100**.
- **`rehydrate`** has `<` / `>` in `description` (breaks parsers / triggering) — drop the angle
  brackets, **92 → 100**.

---

The loop is the same one skval runs everywhere: **score → read the ranked findings → fix →
re-score and confirm the gain** — here, on skills found in the wild.
