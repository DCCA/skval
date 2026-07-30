# Resolving the Popup/Dialog Naming Conflict: A Purpose-First Process

The naming war is a symptom of ambiguous purpose. Here's how to resolve it at the root.

## Step 1: Write a Purpose Statement (Before Any Name)

Stop debating names. Instead, gather your team and write a **1–2 sentence purpose statement** that answers: *Why does this component exist and what user problem does it solve?*

Examples:
- "A lightweight overlay for confirming a single, low-risk action without disrupting the main workflow."
- "A focused container for a specific subtask that requires user attention and decision."

This statement becomes your source of truth. The name should follow from it, not precede it.

## Step 2: Distinguish by Purpose, Not Appearance

Your existing Modal and Tooltip exist because they solve different problems. Distinguish your new component the same way:

| Component | Purpose | Dismissal | Focus |
|-----------|---------|-----------|-------|
| **Tooltip** | Provide contextual help on hover/focus | Auto-dismiss or click-away | Read-only info |
| **Modal** | Block the app for a significant decision or multi-step form | Force acknowledgment | Requires interaction |
| **Dialog** (if that's your new component) | Request confirmation or input for a single, bounded action | User choice to dismiss | Quick response |

Write this table in your component definition. The purpose, not the visual appearance, is what distinguishes them.

## Step 3: Assemble a Cross-Discipline Team

Naming and behavior need buy-in from:
- **Designer**: visual consistency and when to use it in flows
- **Developer**: implementation complexity, browser support, accessibility
- **Content Strategist**: microcopy tone and clarity
- **System Maintainer**: long-term sustainability and edge cases

Schedule a 1-hour sync. Share the purpose statement. Discuss what the component should do and what it shouldn't. Document decisions as you go.

## Step 4: Derive the Name From the Purpose

Once purpose is agreed, naming becomes straightforward. If the purpose is "confirm a low-risk action," names like "Confirmation Dialog" or "Action Prompt" are stronger than debating "Popup" vs. "Tooltip." 

**The rationale is the source of truth for future evolution.** Any future "should we add feature X?" gets answered by checking the purpose statement, not by voting again.

## Step 5: Document Usage With Do's, Don'ts, States, and Variants

Once named and purposed, document:
- **Do's & Don'ts**: When to use this component vs. Modal, vs. Tooltip
- **States**: default, loading, error, success
- **Variants**: size/modality (modal vs. non-blocking), button arrangements
- **Accessibility**: keyboard navigation, ARIA labels, focus management
- **Content guidelines**: recommended text length, button labels

Example do/don't:
- ✓ Use for: "Are you sure you want to delete this item?"
- ✗ Don't use for: Complex multi-step workflows (use Modal)
- ✗ Don't use for: Passive tooltips on hover (use Tooltip)

## Why This Stops Future Wars

This process shifts the conversation from opinion to evidence. When the next naming debate comes up, you have a decision record showing *why* you chose this component's name and purpose. New contributors can understand and extend the system because the logic is documented, not debated.
