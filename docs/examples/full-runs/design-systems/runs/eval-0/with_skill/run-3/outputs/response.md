# Icon Set Guidelines

## Icon Sizing

For your startup with 20 product UI icons plus marketing icons, use a **single base size of 24px** as your primary working size. This is the most practical choice for product UI.

**Size scale:** Restrict additional sizes to multiples of 8:
- **16px** — for compact UI, secondary contexts, or when space is constrained
- **24px** — your primary base size; build all icons at this size first
- **32px** — for larger touches or lower-density layouts

Add other sizes (like 80px for marketing icons) **only when glyph complexity truly requires it**. Before expanding your scale, design at 24px and confirm visually that simplification isn't possible.

**Critical rule:** Always design the largest size first, then simplify down. Never design small first—you'll end up with icons that can't scale up without losing detail or requiring redrawing.

## Color Rules

**Product UI icons (the 20):** Use **exactly 1 color**—typically black or a brand color. Single-color icons are:
- Instantly consistent across your product
- Easy for designers and developers to leverage (simple overrides for hover/disabled/dark mode)
- Unambiguous in meaning

**Marketing icons (landing page):** Use **at most 2 colors**. Any icon with 3+ colors reads as illustration, not icon, and will look out of place in your system.

## Stroke Treatment

**Stroke weight:** Pick one weight for all strokes in your product icon set (e.g. 1.5px or 2px). All icons must use that same weight—consistency is essential.

**Gap between strokes:** The gap between any two strokes must be **at least equal to the stroke weight**. This ensures strokes read as separate elements, not a muddy blend.

**Filled vs. stroked:** Decide whether your set is primarily filled or stroked, and stick with it. Don't mix filled and stroked icons side-by-side without intention—the visual inconsistency will feel broken.

**Edge padding:** Add padding equal to your stroke weight on the edges. This balances the visual weight of the icon within its 24×24 container and accounts for stroke offset.

## Pixel Grid & Optical Grid

- Align all straight lines to the pixel grid to avoid blur
- Use an optical grid to account for perceptual center of mass—circles optically read smaller than squares in the same bounding box, so adjust their position slightly to feel centered

## Production Workflow

1. **Design at 24px** in your design tool (Figma, Illustrator, etc.)
2. **Export at 24px** as your master
3. **For 16px:** Simplify by removing fine details and thinning strokes if needed; don't just scale down
4. **For 32px:** Scale up and strengthen lines/details if they weaken at size
5. **Test at actual size** in your UI before finalizing—don't rely on preview thumbnails
