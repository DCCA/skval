# Icon Set Guidelines for Your Startup

## 1. Icon Sizing

Pick **24px as your base size** for all product UI icons. This is the most common standard for desktop and mobile interfaces.

**Sizes at multiples of 8:**
- **16px** — dense UI, compact tables, secondary actions
- **24px** — primary standard for buttons, toolbars, list items
- **32px** — hero states, large touch targets, prominence

Only add additional sizes (beyond 16/24/32) if glyph complexity genuinely requires it. For marketing icons on your landing page, you may use larger sizes like 48px or 64px, but these are typically the exception, not the rule.

**Guiding principle:** Start by building all icons at 24px. If an icon works well when scaled down to 16px, you're done. Scale it down only when the glyph complexity demands it—never design small first, then scale up. Always build large and simplify.

---

## 2. Color Rules

**Product UI Icons:** Use exactly **1 color** (typically black or your primary brand color). Single-color icons are:
- Easier for designers to compose into layouts
- Flexible for backgrounds and hover states
- Instantly recognizable within your ecosystem

**Marketing Icons:** Use at most **2 colors**. Two-color icons add visual interest while remaining manageable. Any more than 2 colors reads as illustration, not icon, and loses the efficiency that makes icons work as a system.

---

## 3. Stroke Treatment

**All strokes in your set must share one weight.** Pick either 1.5px or 2px and stick with it everywhere. Mixing weights within a set breaks visual cohesion.

**Gap between strokes:** Must be at least equal to the stroke weight. If your stroke is 2px, the gap is at least 2px. This prevents strokes from visually merging at smaller sizes.

**Pixel grid alignment:** Align straight lines to the pixel grid to prevent anti-aliasing blur. Use an optical grid (accounting for the perceptual center of mass—circles appear smaller than squares at the same visual size) to balance visual weight within your fixed-size container.

**Filled vs. stroked:** Be consistent within a set. Never mix filled and stroked icons side by side without intention. Filled icons have higher recognizability; stroked icons support finer detail. Choose one approach and stick with it.

---

## 4. Production Workflow: Building at Multiple Sizes

1. **Design at 24px first.** Build your icon at full complexity and detail.
2. **Test at 24px.** Ensure every line is crisp, every stroke weight is uniform, and every gap is intentional.
3. **Simplify for 16px.** Remove or merge detail that becomes muddy at the smaller size. Thin strokes or small gaps may need to close or be removed.
4. **Test at 16px.** Verify legibility and that no strokes are bleeding together.
5. **Scale for 32px** (if needed). If your 24px version works at 32px without looking hollow, you're done. If not, add intentional detail for the larger size.
6. **Export consistently.** Use the same naming convention for each size (e.g., `icon-name-16.svg`, `icon-name-24.svg`, `icon-name-32.svg`).

---

## Why This Matters

A tight, well-documented icon system becomes a design asset your team reuses across platforms. Ambiguity in sizing or color leads to custom one-off icons that fracture the system. Lock down these decisions now, and your system will scale as you grow.
