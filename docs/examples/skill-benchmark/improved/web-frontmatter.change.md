# web-frontmatter — the fix

A real published skill: **`annotate`** from
[glebis/claude-skills](https://github.com/glebis/claude-skills). Its `description` contains an
unquoted colon (`… Local-only: synthetic or consented data only …`), so the YAML frontmatter
is invalid and the skill has no usable name/description — it won't trigger or load correctly.
Scored verbatim, before and after the one-line fix.

**Before** (invalid YAML — the colon after `Local-only` starts a YAML mapping):

```yaml
---
name: annotate
description: Build and verify a PII gold set … Local-only: synthetic or consented data only; …
---
```

**After** (skval's finding applied — wrap the description in quotes so the colon is safe):

```yaml
---
name: annotate
description: "Build and verify a PII gold set … Local-only: synthetic or consented data only; …"
---
```

One change — wrap the description in quotes — takes the skill from **50 / D / Revise**
(skval can't read the frontmatter, so name + description count as missing) to
**100 / A / Ship**. skval's own diff (`web-frontmatter.compare.json`): `overall_delta: +50`,
verdict `Revise → Ship`.
