# Icon Guidelines for Your Startup

## Base Size and Scale System

Start with **24px as your primary base size**. This is the most common size for product UI icons across web and mobile platforms. If you need additional sizes, restrict them to a consistent scale using **multiples of 8**:

- 16px (small/compact)
- 24px (standard/base)
- 32px (large/prominent)
- 40px (extra large, if needed)

Only create a new size when the icon's geometric complexity genuinely requires it. Don't create every size by default—start with 24px and add 16px or 32px only when 24px is too detailed or too sparse.

## Color Treatment

**Product UI icons (the 20 standard icons):**
- Use exactly **1 color per icon**
- Maintain consistency across the set—all icons should feel like they belong to the same system
- Choose a neutral dark color (like #1a1a1a or your brand's primary) for light backgrounds, or a light color for dark backgrounds
- Avoid using multiple colors for product icons; it dilutes the system's coherence and reads as illustration rather than iconography

**Marketing icons (the larger landing page icons):**
- Use a maximum of **2 colors per icon**
- This gives you more visual interest for marketing purposes while maintaining hierarchy
- 3+ colors starts to read as illustration rather than icon, losing the system's authority
- If you do use 2 colors, ensure they have intentional contrast and relationship (e.g., primary + accent, or primary with a highlight)

## Stroke Treatment

**Uniform stroke weight:**
- All strokes in your icon set must share the same weight (typically 1.5px to 2px at 24px size)
- This consistency makes the set feel professionally crafted and reduces visual chaos
- Don't mix filled and stroked icons side by side without a clear structural reason—pick one approach per set or clearly separate them by type

**Stroke gaps and spacing:**
- The gap between strokes must be at least equal to the stroke weight itself
- For example, if your stroke is 2px wide, gaps between parallel strokes should be 2px or wider
- This prevents visual mudding and keeps icons legible at smaller sizes
- Alternatively, use edge padding (empty space around the icon) equal to the stroke weight to balance visual weight

**Pixel alignment:**
- Snap straight lines to the pixel grid at your base size (24px) to ensure clean, crisp rendering
- You can use an optical grid to help center elements perceptually, not just mathematically

## Production Workflow

**Build large first, simplify down:**
- Start by designing your icons at 32px or even 40px
- Then carefully simplify the geometry for smaller sizes (24px, 16px)
- This approach ensures legibility at small sizes and preserves the structural integrity of your forms
- Never design the small size first and enlarge it—small sizes hide complexity that doesn't translate upward

**Technical steps:**
1. Create your source file at 32px or 40px
2. Test each icon at its intended usage size
3. Simplify for 24px if that's your primary size
4. Further simplify for 16px if needed (may require removing details)
5. Export as SVG with a consistent naming convention

**Color and stroke consistency:**
- When exporting, use a single swatch color for all icons (not individual colors)
- This lets product teams easily change icon colors via CSS or props without requiring new assets
- Store as SVG where possible—it scales infinitely and reduces file size

---

Start with these fundamentals, and your icon set will feel coherent and scalable even as your product grows. The constraint of 1–2 colors and a uniform stroke creates professional polish without requiring a large team.
