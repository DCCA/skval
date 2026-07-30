# Icon Set Guidelines for Your Startup

## Base Size and Additional Sizes

**Start with a single base size of 24px.** This is the most common production icon size and supports your use case well.

Add additional sizes *only when glyph complexity requires it*. For a 20-icon set, you likely need:
- **16px** — compact UI, tight navigation, smaller contexts
- **24px** — primary, standard UI (your base)
- **32px** — larger touch targets, accessibility

All sizes must be multiples of 8, respecting your baseline grid.

**Critically: Design the 24px size first, then simplify down to 16px.** Never design the small size first — you'll create features that can't be simplified legibly. After 24px is locked, remove unnecessary details and test legibility at 16px before proceeding.

## Color Rules

**Product icons:** Use exactly **1 color only** (black or your primary brand color). A single-color icon set has maximum leverage across UI contexts — buttons, navigation, status indicators, lists. More colors constrain how they can be used and fragment your system.

**Marketing icons (landing page):** Allow up to **2 colors maximum.** Do not go beyond 2. Three or more colors reads as illustration, not icon, and breaks the family cohesion.

This distinction keeps your system disciplined: product icons are infinitely composable; marketing work has narrative flexibility.

## Stroke Treatment

**Uniform stroke weight across the entire set.** Pick one stroke weight (commonly 1.5px or 2px at 24px base size) and apply it consistently to every icon. Inconsistent strokes break visual harmony and signal lack of system.

**Gap between strokes must be at least equal to your stroke weight.** If you're using 2px strokes, strokes should be separated by at least 2px. This maintains optical balance and legibility, especially at smaller sizes.

**Do not mix filled and stroked icons side by side** unless intentional (e.g., a clear "filled = selected" pattern). Decide early: is your set filled, stroked, or split by semantic purpose? Make it explicit in your guidelines.

## Pixel Grid and Optical Adjustment

- **Align all straight lines to the pixel grid.** Horizontal and vertical edges must sit on clean pixel boundaries, never half-pixels.
- **Use an optical grid** to account for perceptual weight. Circles and diagonals optically appear smaller than squares of the same bounding box—adjust inner padding to compensate.
- **Edge padding equal to your stroke weight** balances visual weight in a fixed-size container. A 2px-stroked icon should have ~2px internal padding from the 24px bounding box edge.

## Production Workflow

1. **Design 24px master** in your vector tool (Figma, Illustrator, etc.) with all refinement locked in
2. **Create 16px version** by removing complexity: simplify details, slightly increase stroke weight optically, remove internal elements if needed
3. **Create 32px version** by scaling 24px up, checking for stroke weight consistency
4. **Export all three sizes** in your format of choice (SVG, PNG, webfont)
5. **Name semantically:** use `arrow-right`, `chevron-down`, `check-circle`, not `icon-23`

This approach ensures a coherent, production-ready icon family at launch.
