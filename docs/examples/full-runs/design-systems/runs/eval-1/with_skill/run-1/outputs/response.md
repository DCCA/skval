# Resolving the Popup vs. Dialog Component Definition

Your naming war is a symptom of something deeper: **you haven't agreed on purpose.** The solution is not to vote, but to follow a definition process that roots naming in documented rationale.

---

## Step 1: Write a Design Rationale (Before Any Naming)

Stop naming. Instead, gather your team and write a **1–2 sentence purpose statement** for this new component. This statement answers: *What problem does this component solve, and what behavior does the user expect?*

Example rationales:

- **Modal:** "A Modal asks the user for confirmation or captures critical information. The rest of the page is blocked until the user responds or dismisses."
- **Popup/Popover:** "A Popover reveals contextual information or options relative to a trigger element without blocking the rest of the page."
- **Tooltip:** "A Tooltip displays brief, non-interactive help text on hover or focus."
- **Dialog (your new component?):** "A Dialog captures user input or presents a task within a contained context. Unlike a Modal, the user can navigate away from a Dialog without interruption."

**This rationale is your single source of truth.** It determines naming, behavior, and how the component evolves. Write it first.

---

## Step 2: Involve All Disciplines

Don't let designers or developers decide alone. Gather:

- **Designer** — ensures visual and interaction consistency across the system
- **Developer** — ensures the component is implementable and efficient in code
- **Content strategist (or product)** — ensures the microcopy and behavior align with user needs
- **System maintainer** — ensures the component fits into the governance model and doesn't create ambiguity with siblings

Each discipline will see different issues. The developer might spot that "Popup" doesn't specify whether it auto-closes on click-outside (the designer thought yes; the developer thought no). The content strategist might note that users need to distinguish a destructive action from a neutral one. Resolve these together.

---

## Step 3: Derive the Name from Purpose

Once the rationale is agreed, the name follows naturally. If your rationale says "captures input without blocking the page," "Dialog" works better than "Popup" (which reads like a dismissible notification). If it says "reveals contextual options near a trigger," "Popover" is clearer.

**Never name from aesthetics.** "It looks like a dialog, so call it Dialog" is backwards. The rationale drives the name.

---

## Step 4: Document How It Differs From Similar Components

Write a short comparison table:

| Component | Purpose | User Can Dismiss | Rest of Page | Use Case |
|-----------|---------|------------------|--------------|----------|
| Modal | Critical action requiring confirmation | On explicit action only | Blocked (dimmed) | "Delete account?" "Confirm purchase?" |
| Dialog | Contained task without blocking the page | Yes, but loses data | Active (clickable) | "Refine search filters" "Edit profile" |
| Popover | Contextual options or info near a trigger | On click-outside or explicit close | Active | "Font options" "Share settings" |
| Tooltip | Non-interactive help text | On blur or timeout | Active | "This email is optional" |

This table lives in your system documentation and prevents drift.

---

## Step 5: Document Usage With Do/Don't, States, and Variants

For your new component, document:

**Do:**
- Use a Dialog for tasks that take multiple steps (e.g. multi-step form)
- Place the primary action on the right, destructive on the left
- Keep the Dialog title short and action-oriented ("Refine Filters" not "Settings")

**Don't:**
- Use a Dialog for critical warnings (use Modal instead)
- Stack Dialogs without a strong reason (three nested Dialogs confuses users)
- Hide critical information in a scrollable Dialog body without clear scrolling affordance

**States:**
- Default (resting)
- Hover (on buttons inside the dialog)
- Focus (keyboard navigation)
- Disabled (if applicable)
- Error (validation failure in form)

**Variants:**
- With form (input fields)
- With confirmation (yes/no actions)
- With single action (just a close button)

---

## Why This Process Works

When teams argue over "Popup vs. Dialog," they're arguing over semantics without shared context. By starting with purpose, involving all perspectives, and documenting the rationale, you remove the ambiguity that caused the war. Future component proposals will follow the same process, and naming disputes become non-issues because the answer is in the documented rationale.

This is the single source of truth. Naming follows. Future evolution follows. Compliance follows.
