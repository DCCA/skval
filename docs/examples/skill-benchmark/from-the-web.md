# From the web — skval over real published skills

A real `skval` **structural** run over **69 community skills** pulled from three public
GitHub collections — [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills),
[glebis/claude-skills](https://github.com/glebis/claude-skills), and
[smartnews/claude-skills](https://github.com/smartnews/claude-skills) — deterministic, no
model calls. Most are well-built; this page is about the ones skval flags, and what fixing
them looks like.

> **Safety first.** Every fetched skill was treated as **inert text** and run through skval's
> D6 safety gate *before* anything else. **0 / 69** tripped it, and none were ever executed —
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

## Case study — invalid frontmatter: 50 → 100

A real-world bug class: a `description` with an unquoted colon.

| | Score | Grade | Verdict | Finding |
|---|------:|-------|---------|---------|
| **Before** ([scorecard](improved/web-frontmatter.before.md)) | 50 | D | Revise | invalid YAML frontmatter |
| **After** ([scorecard](improved/web-frontmatter.after.md)) | 100 | A | Ship | — |

The fix skval points to — **quote the description** — is one line. skval's own diff
([`improved/web-frontmatter.compare.json`](improved/web-frontmatter.compare.json)):
`overall_delta: +50`, verdict `Revise → Ship`. What changed:
[`improved/web-frontmatter.change.md`](improved/web-frontmatter.change.md).

---

The loop is the same one skval runs everywhere: **score → read the ranked findings → fix →
re-score and confirm the gain** — here, on skills found in the wild.
