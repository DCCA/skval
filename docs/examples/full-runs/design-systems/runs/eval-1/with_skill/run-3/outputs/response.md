# Component Definition Process: Popup vs. Dialog

Your naming war is a symptom of a deeper problem—you're debating names without agreeing on purpose. Here's the process to fix it:

## Step 1: Write a Design Rationale First

**Before choosing any name**, write a 1–2 sentence purpose statement:

> "A modal dialog asks the user for confirmation or critical input and blocks interaction with the page behind it. It requires explicit action to dismiss."

> "A popup tooltip provides contextual information on hover and automatically dismisses when the user moves away or clicks elsewhere."

This rationale is your **single source of truth**. It answers: What problem does this component solve? When does it appear? What behavior does it require? Name and behavior follow naturally from here.

## Step 2: Invite All Disciplines

Bring together:
- **Designer** — visual cohesion, when this component feels right vs. wrong
- **Developer** — code efficiency, how this component slots into the codebase
- **Content strategist** — how the words in this component work (labels, help text, error states)
- **Maintainer** — governance, how this component stays consistent as the product evolves

Each perspective surfaces a different requirement. A designer might say "this needs consistent padding"; a developer might say "this should accept a slot for custom content"; the content strategist might flag that button labels need flexibility. These constraints don't conflict—they refine the rationale.

## Step 3: Distinguish by Documented Purpose, Not Visual Appearance

Your overlap problem (Modal vs. Tooltip vs. Popup vs. Dialog) exists because you're comparing visual traits. Instead, write one sentence for each and compare the purpose:

| Component | Purpose | When It Appears | User Action |
|---|---|---|---|
| Modal | Blocks interaction and demands a response | When critical info or a choice is needed | User must click a button to proceed |
| Dialog | Opens conversation; user may cancel or proceed | When the system needs input or confirmation | User can dismiss or submit |
| Tooltip | Provides contextual help on interaction | On hover or focus of a UI element | Auto-dismisses when user moves away |
| Popup | Provides additional info or actions near a trigger | On click or hover of a specific element | User can dismiss or interact |

Once purpose is clear, the naming becomes obvious: a "Dialog" is for dialogs (back-and-forth with the system); a "Tooltip" is for tips on demand. If designers and developers disagree on whether something is a "Popup" or "Dialog," the disagreement is really about purpose—write the rationale first and the name resolves.

## Step 4: Document Usage

For the new component (let's assume it's a Dialog), document:

**Concept:** One-sentence rationale

**Description:** When and why to use this. "Use Dialog when you need the user to make a choice or provide input before continuing. Do not use Dialog for error messages (use Toast) or contextual help (use Tooltip)."

**Do/Don't:**
- ✓ DO use a Dialog for a multi-step form
- ✓ DO include a cancel button
- ✗ DON'T use for confirmations shorter than one sentence (use a confirmation Toast instead)
- ✗ DON'T trap users in a Dialog with no way to dismiss

**States & Variants:**
- Loading (user clicked submit; form is validating)
- Error (validation failed; user can edit and retry)
- Success (action completed; Dialog auto-closes)
- Sizes: small (400px), medium (600px), large (900px)

## Step 5: Lock It In

Once documented, this becomes the definition. Future debates ("Should we add a Drawer?" "Is this a Popover?") are now resolved by checking whether the new component's purpose matches an existing one. If it doesn't, you propose a new component—with its own rationale, not by just disagreeing on the name.

This process also prevents the "quiet shipping of modified copies" problem because everyone has the same source of truth.
