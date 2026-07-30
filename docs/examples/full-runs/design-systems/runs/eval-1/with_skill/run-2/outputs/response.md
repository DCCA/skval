# Resolving Your Overlay Component Naming Conflict

The naming war you're in—Popup vs. Dialog—stems from skipping the definition step that determines the name in the first place. Here's the proven process to end it.

## Step 1: Write the Design Rationale (Before Any Name)

**This is the single, essential first step.** Stop debating names immediately. Instead, have your team write a **1–2 sentence design rationale** that answers: *What is this component's purpose? When and why would a user encounter it?*

Examples:
- "A Modal asks the user for a critical decision; it blocks interaction with the page until resolved."
- "A Tooltip displays contextual help on hover; it's non-blocking and dismisses automatically or on click."
- "A Popover anchors to a button or element and shows related options without blocking the page."

Write 2–3 candidate rationales. Debate *those*, not the names. The purpose is the single source of truth for naming and future evolution. Once you agree on purpose, naming is nearly automatic.

## Step 2: Convene All Disciplines

Your naming war happened because not everyone had a voice. **Bring together:**
- A designer (visual behavior, consistency with Modal/Tooltip)
- A developer (code reusability, prop complexity)
- A content strategist or maintainer (naming clarity, documentation burden)

Each discipline sees a different facet of the component. A designer might worry about visual overlap with Modal; a developer might see prop overlap that creates maintenance debt. A content person might flag that "Popup" is ambiguous across the team. All three perspectives must be reconciled.

## Step 3: Distinguish Modal, Tooltip, and Your New Component by Purpose

You likely have:
- **Modal:** Blocks page interaction, requires a decision (confirmed purpose)
- **Tooltip:** Provides help text, non-blocking, auto-dismisses (confirmed purpose)
- **Your new component:** Unclear—is it blocking like a Modal, non-blocking like a Tooltip, or something else?

Write the rationales for all three, side by side:

| Component | Purpose | Blocking? | Trigger |
|-----------|---------|-----------|---------|
| Modal | ... | Yes | User action / system state |
| Tooltip | ... | No | Hover / focus |
| New | ... | ? | ? |

If your new component's purpose is distinct from Modal and Tooltip, its name will follow naturally. If it overlaps, you don't need a new component—you need a variant or a configuration of an existing one.

## Step 4: Document Usage with Do/Don't and States

Once purpose and name are agreed, document:
- **Concept:** One-sentence summary of what it does
- **Description:** When to use it, when *not* to use it
- **Do/Don't examples:** Visual or narrative examples
- **States:** Hover, focus, open, closed, loading, error, disabled
- **Variants:** Does it accept titles, footers, custom actions? What are the boundaries?
- **Trade-offs:** Performance, accessibility, browser support concerns

This documentation becomes the guard rail. Future designers won't name variants incorrectly because the purpose is documented. Future developers won't extend it ambiguously because the API is defined.

## Why This Process Stops Naming Wars

- **Rationale first** removes personal preference; debate moves to measurable purpose
- **Multi-discipline input** surfaces hidden assumptions (e.g., "I thought this was like Modal because of how it looks")
- **Purpose-derived naming** makes the name *obvious* once context is clear, not a vote
- **Documented usage** prevents the next team from reinventing it differently

The next overlay component you define will use the exact same process, and the naming will be settled in minutes, not weeks.
