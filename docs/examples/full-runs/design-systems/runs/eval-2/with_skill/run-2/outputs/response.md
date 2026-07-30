# Governance and Contribution Process for Your Design System

The root cause is not that your teams are malicious—it's that your system hasn't defined who can change what, and how. Product teams ship modified copies because the official process is unclear or too slow. Fix the process; compliance follows.

## 1. Define Your Contribution Model

**Document explicitly:**
- **Who can propose** a new component or change? (Any team? Architects only? Anyone with a write token?)
- **Who reviews** proposals? (Design leads? Design + engineering pair?)
- **Who approves** and merges? (A single maintainer? A committee?)
- **What's the escalation path** if a proposal is rejected?

Example model:
```
Propose: Any product team or designer (via GitHub issue + RFC template)
Review: Design system team + one engineer from the requesting team
Approve: Design system lead (or rotating approver)
Timeline: Decisions within 5 business days; if rejected, written feedback within 2 days
```

Post this publicly in your documentation. Link to it from every new-component form.

## 2. Assign Clear Ownership

**Each component must have a named owner** — not a committee, a person or small pair who:
- Writes and maintains the design rationale
- Responds to questions and edge cases
- Leads design reviews when the component evolves
- Monitors production usage (see #4)

Ownership prevents orphaned components and diffuses accountability. "Who can I ask about the Button component?" should have a clear answer.

## 3. Implement a Self-Governing Contribution Process

Your contribution workflow should have four gates:

### Gate 1: Proposal Format
Teams must submit:
- **Problem statement:** What gap or friction are we solving?
- **Design rationale:** One sentence: what is this component's purpose?
- **Comparison to existing components:** How does this differ from [Modal, Button, etc.]? Why can't we reuse?
- **Acceptance criteria:** What does "done" look like?

Example template (in your docs or GitHub):
```markdown
## New Component Proposal

**Problem:** Our marketing pages need a testimonial card that combines media, quote, and attribution.

**Rationale:** A Testimonial displays social proof in a visually distinctive format without blocking user flow.

**Comparison:** Unlike our Card component (generic container) or Quote component (text-only), a Testimonial integrates image + text + source.

**Acceptance Criteria:**
- Accessible at WCAG AA
- Works with responsive images
- Supports dark mode
```

### Gate 2: Design Rationale Review
Before any design work begins, the design system team validates the rationale. Is this truly a new component, or a variant of an existing one? Does the purpose make sense? This catches false positives before weeks of design time.

### Gate 3: Review Checklist
Once the component is designed and coded, a review checklist ensures quality:
- [ ] Does the design rationale still hold? Any conflicts with other components?
- [ ] Are all states documented (hover, focus, disabled, error)?
- [ ] Are tokens used consistently (colors, spacing, typography)?
- [ ] Does the code follow your naming conventions?
- [ ] Is the accessibility audit complete?
- [ ] Is documentation clear with do/don't examples?
- [ ] Has a stakeholder from design, engineering, and content signed off?

### Gate 4: Merge Criteria
Merge only when:
- All checklist items are complete
- No conflicts with existing components
- No technical debt or shortcuts accepted
- Documentation is in the main branch alongside the code/design

## 4. Resolve Ambiguity at Definition Time, Not After

**This is critical:** your compliance problem exists because teams invent workarounds when the documented component doesn't quite fit their use case. The fix is to make the definition phase thorough and collaborative.

When a team says "We need a modified Button," ask: "What's different? Why?" and add it to the next round of Button variants *if it's general-purpose*, or reject it *if it's bespoke to their product*. Don't let ambiguity linger; resolve it together.

## 5. Conduct Regular Production Audits

**Quarterly or biannually**, audit what's actually shipped:
- Do a visual scan of your product surface
- Catalog components by type
- Flag any that don't match the documented system
- Document deviations and their reasons

Create a simple audit artifact (screenshot + notes):
```
Q3 Audit Notes
- Marketing site uses Button variant not in system (color: teal). Approve and document or remove? → Decision: Add to system as accent-secondary
- Onboarding flow has custom Modal overlay. Reason: ??? (track down owner, resolve)
- Settings pages use undocumented spacing scale (24px not in tokens). Root cause: team didn't know about it → Action: Training session
```

Share audit findings with product leadership. Show how deviations cost time (rebuild vs. reuse).

## 6. Make the Process Frictionless

- **RFC template** in your GitHub (or Figma space)
- **Approval SLA** — decisions within N days (no open-ended review)
- **Clear rejection reasons** — if "not now," explain why and when to revisit
- **Lightweight fast-track** — small variants of existing components skip full review
- **Slack notification** when proposals are ready for review (make it easy to participate)

## Why This Works

Teams stop shipping modified copies when:
1. The official process is faster than going rogue
2. Ownership is clear, so they know who to talk to
3. The definition process is rigorous, so they trust the system
4. Audits surface deviations before they spread

You'll catch the next unauthorized Button variant in your first audit and bring it into the system, because you have a process and someone to hold accountable.
