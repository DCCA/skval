# Resolving Component Definition Conflicts: A Process-First Approach

Your naming debate is actually a symptom of a deeper problem: the component's purpose hasn't been agreed upon. Before you settle on "Popup" vs. "Dialog," follow this process to define the component correctly.

## Step 1: Write the Design Rationale First

**Before any naming discussion**, write a **1–2 sentence design rationale** that captures the component's core purpose:

> This component surfaces important information or actions that requires user attention and blocks interaction with the background. It's distinguished by [purpose-specific characteristic, e.g., "being triggered by user action" or "requiring explicit dismissal"].

The rationale is your source of truth. Everything else—the name, the API, the visual treatment—follows from this statement. A rationale forces your team to agree on *why* the component exists, not just what it looks like.

**Why this matters:** Once the purpose is clear and documented, the name becomes obvious. A component meant to disrupt workflow and demand attention is different from one meant to offer optional information. The naming war stops because you're no longer choosing a name arbitrarily—you're deriving it from the rationale.

## Step 2: Involve Multiple Disciplines

Bring together:
- **Designers**: How does the component fit into the visual hierarchy?
- **Developers**: What are the technical constraints and API needs?
- **Content strategist**: How will this communicate to users? What's the label, help text, error messaging?
- **Maintainer/Component owner**: How will this live in the system long-term?

Each discipline has a different mental model of the component. A designer might focus on visual modality; a developer on event handling; a content person on clarity. Syncing these perspectives upfront prevents later rework.

## Step 3: Distinguish from Similar Components by Purpose, Not Appearance

You have Modal, Tooltip, Popup, and Dialog candidates. Each likely has a distinct purpose:

- **Modal**: Typically used for critical decisions or branching workflows. User cannot proceed without addressing it.
- **Dialog**: A conversation-like exchange, often with specific structured content and actions.
- **Tooltip**: Quick, contextual information that appears on hover or focus. Non-blocking.
- **Popup**: Less formal than Dialog; might be used for promotions, confirmations, or lightweight forms.

Write a sentence for each existing component explaining its purpose. Then write one for your new component. **If the purposes overlap, you don't need a new component—refine an existing one.**

If the purposes are distinct, the names naturally fall into place. Documentation should emphasize purpose, not visual appearance:

> **When to use Modal:** When a user must make a critical decision or complete a branching action before proceeding.
> 
> **When to use Dialog:** When you need a formal, structured exchange with specific input fields or options.
> 
> **When to use your new component:** When [its distinct purpose].

## Step 4: Document Usage with Do/Don't Examples

Once purpose is agreed, create usage guidelines:

**Do:**
- Use this component for [purpose example 1]
- Pair with [recommended patterns]
- Keep content [guidance on length, tone, etc.]

**Don't:**
- Use for [anti-pattern 1 that violates the purpose]
- Nest inside [conflicting patterns]
- Mix with [competing components]

Include **states and variants**:
- Open / Closed
- Loading state (if applicable)
- Error state (if applicable)
- Different content types (text-only, with actions, etc.)
- Responsive behavior (mobile vs. desktop)

Document when Modal is better than your component, and vice versa. This prevents future teams from duplicating or misusing the component.

## Summary

The naming war reflects unclear purpose. **Resolve it by writing purpose first**—then the name, the API, and the usage guidelines all follow logically. A well-defined component with clear purpose reduces future naming debates and prevents duplication.
