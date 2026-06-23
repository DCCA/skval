# web-frontmatter — the fix

A bug class found in **real published skills** on GitHub: the `description` contains an
unquoted colon, so the YAML frontmatter is invalid and the skill has no usable
name/description (it won't trigger or load correctly).

**Before** (invalid YAML — the colon after `Local-only` starts a YAML mapping):

```yaml
---
name: annotate
description: Build a PII gold set. Local-only: synthetic data only, nothing leaves the machine.
---
```

**After** (skval's finding applied — quote the description so the colon is safe):

```yaml
---
name: annotate
description: "Build a PII gold set. Local-only: synthetic data only, nothing leaves the machine. Use when labeling PII spans or measuring inter-annotator agreement (kappa)."
---
```

One change — wrap the description in quotes — takes the skill from **50 / D / Revise**
(skval can't read the frontmatter, so name + description count as missing) to
**100 / A / Ship**. skval's own diff (`web-frontmatter.compare.json`): `overall_delta: +50`,
verdict `Revise → Ship`.
