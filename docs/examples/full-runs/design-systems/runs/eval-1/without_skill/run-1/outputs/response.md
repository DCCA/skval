# Component Definition Process for Your Design System

## Start with Purpose, Not Names

**Stop the naming debate immediately.** Before arguing over "Popup" vs. "Dialog" vs. anything else, write a single **1–2 sentence design rationale** that answers: *Why does this component exist? What problem does it solve that our existing components don't?*

Example rationale: "This component is a centered, dismissible container for time-sensitive confirmations or short-form user input that requires explicit user action before the underlying interface responds."

Write this down. Make it the source of truth for naming and future evolution. Everything else flows from this rationale.

## Naming Follows Purpose

Once your team agrees on the purpose, the name becomes obvious. If your rationale is "dismissible confirmation container," then "Confirmation Dialog" or "Alert Dialog" emerges naturally—not "Popup" or arbitrary alternatives.

The rationale is what lasts; the name is secondary. If you're fighting over names, you haven't agreed on purpose yet.

## Distinguish from Similar Components by Documented Purpose

Your existing Modal and Tooltip exist for different purposes. Document them clearly:

- **Tooltip:** Brief, non-interactive, contextual information that appears on hover/focus, disappears on mouse leave.
- **Modal:** Blocking, full-screen or large overlay that requires dismissal before returning to the main interface. Used for important decisions or complex multi-step forms.
- **Your new component:** [Purpose statement].

Don't rely on visual appearance to distinguish them. Write down the use case for each. This prevents the "does it look like a modal?" confusion and gives you a decision tree when designers are unsure which component to use.

## Involve Multiple Disciplines

Bring the following voices into the definition meeting:

- **Designer:** Visual behavior, animation, state transitions
- **Developer:** Technical feasibility, implementation strategy, component API
- **Content strategist:** Tone, messaging, when confirmations vs. other patterns work
- **Component maintainer:** Long-term support burden, variant complexity

Each discipline catches issues the others miss. A developer might flag that your proposed variants are too flexible; a content strategist might note that a 2-button confirmation works better than a 3-button one.

## Document Usage

Write clear documentation that includes:

- **Do/Don't examples:** Show where this component fits and where it doesn't.
- **States:** Unprompted, hovered, focused, disabled, loading, error.
- **Variants:** Size, button count, iconography, confirmation vs. cancellation patterns.

Include code examples and links to live implementations. Show screenshots of the component in real product contexts, not just isolated component specimens.

## Resolution

Once this is done, the component is defined. Future disputes about usage or variants get resolved by checking the purpose statement and documentation, not by reopening the naming argument.
