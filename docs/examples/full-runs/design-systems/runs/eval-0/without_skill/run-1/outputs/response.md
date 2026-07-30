# Icon Set Guidelines for Startup

## Sizing Strategy

Establish **24px as your primary base size**. This is the sweet spot for most UI use cases—readable on screens while staying crisp when exported.

Build out sizes using multiples of 8: **16px, 24px, and 32px**. Use these three sizes to cover your product UI needs. Only add 40px or 48px sizes if your design system includes larger CTAs or cards that require oversized icons. Avoid creating every possible size; restrict yourself to multiples of 8 to keep exports lean and grid-aligned.

## Color Rules

**Product UI icons:** Use exactly 1 color (usually a neutral dark or your primary brand color). This keeps them lightweight, easy to recolor, and consistent across your interface.

**Marketing icons:** Allow up to 2 colors maximum. Marketing materials benefit from slightly more visual interest, but 3+ colors cross into illustration territory and shouldn't be called "icons."

## Stroke Treatment

All strokes in a single icon set must share one consistent weight. This creates visual harmony; mixing stroke weights makes a set feel incoherent.

The gap between strokes must be **at least equal to the stroke weight itself**. For example, if your stroke is 1.5px, gaps should be 1.5px or wider. This ensures strokes don't optically merge and maintains clarity at smaller sizes.

If using filled icons alongside stroked icons in the same set, do so with intention and clear visual separation by use case—never mix them arbitrarily within the same icon collection.

## Production Workflow

**Build the large size first.** Design your 32px icon with all detail needed for that size, then systematically simplify for 24px and 16px. You'll discover which details are necessary at smaller sizes and eliminate visual noise.

Never start with the 16px size and scale up; you'll add unnecessary complexity that doesn't contribute to clarity.

For each smaller size, remove internal details that don't read well at that scale, simplify curves to geometric shapes when it helps legibility, and keep stroke weight optically consistent by adjusting slightly if needed (though ideally you'll stick to one weight).

Export each size separately and test them at actual rendering sizes in your product UI before finalizing. Icons that look good in Figma at 100% zoom often need tweaks when displayed in your actual app.
