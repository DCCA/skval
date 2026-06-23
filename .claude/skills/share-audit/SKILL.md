---
name: share-audit
description: Audit a web page or landing page for share-readiness — Open Graph and Twitter Card meta, the link-preview image, structured data, accessibility, and content currency. Use when someone wants to check how a page or link will look when shared (Slack, X, LinkedIn, Discord, iMessage), review the og:image / social card, fix a missing link preview, or make a site "best in class for sharing".
---

# share-audit

Audit a page so its shared links render a **rich, correct preview everywhere**.

## Quick start

Run the deterministic meta check first — works on a live URL or a local HTML file:

```bash
python scripts/check_meta.py <url-or-file>
```

It reports which Open Graph / Twitter / canonical tags are present, whether the
`og:image` is reachable and its **real pixels match** the declared
`og:image:width`/`height`, and whether the JSON-LD parses. It exits non-zero if a
required tag is missing — handy as a pre-publish gate. Then do the judgment passes.

## Workflow (create a todo per section)

1. **Social meta — the core of sharing.** Confirm a complete, correct set:
   - **Open Graph:** `og:title`, `og:description`, `og:type`, `og:url`, `og:site_name`,
     `og:image` (an **absolute** URL), `og:image:width`/`height` (must match the real
     file), `og:image:alt`.
   - **Twitter:** `twitter:card` = `summary_large_image`, `twitter:title`,
     `twitter:description`, `twitter:image` (+ `twitter:image:alt`).
   - `<link rel="canonical">` with the absolute page URL.
   - **Image:** 1200×630 (1.91:1), under ~5 MB, legible at thumbnail size, on-brand.
2. **Structured data — SEO.** A valid JSON-LD block of the right `@type`
   (`SoftwareApplication`, `Article`, `Organization`, …) with accurate fields. Never
   fabricate ratings or counts.
3. **Accessibility.** `lang` on `<html>`; meaningful `alt` (empty only for decorative
   images sitting beside equivalent text); heading order with no skipped levels; link
   text that makes sense out of context (not "click here"); decorative emoji wrapped in
   `<span aria-hidden="true">`; body/dim text passes WCAG AA (≥ 4.5:1 contrast).
4. **Content currency.** Cross-check every claim against the source of truth (the repo
   or product): version numbers, counts, prices, the feature list, screenshots. Flag
   anything stale or internally inconsistent.
5. **Render & verify (live).** Load the deployed URL; confirm the `og:image` actually
   loads (`complete && naturalWidth > 0`, not a broken `<img>`); confirm nav anchors
   land below any sticky header. Optionally preview the link in a card debugger.

## Output

A **prioritized findings list** — each item: **severity** (high / medium / low), the
exact location, and the concrete fix. Lead with anything that breaks the link preview
(missing/invalid `og:image`, no card). End with the top 3–5 fixes to do first.
