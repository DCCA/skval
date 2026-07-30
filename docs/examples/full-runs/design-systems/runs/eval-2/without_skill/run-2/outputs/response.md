# Design System Governance and Contribution Process

Your teams are forking components because your governance model isn't clear, and your documentation is ambiguous enough that it's easier to copy-paste and modify than to contribute back. Here's how to fix this.

## Document Your Contribution Model

**Define who can do what:**

1. **Who can propose a change or new component?**
   - Any designer? Any developer? Only system team members?
   - Set a clear bar (e.g., "anyone can propose; the system team reviews for fit")

2. **Who reviews?**
   - Designate a review group: design system lead, component owner, cross-functional stakeholder
   - Set review turnaround expectations (e.g., "48 hours")

3. **Who approves and merges?**
   - Typically the system owner or a designated maintainer
   - Approval should be gated on review feedback being addressed

**Make this visible.** Write it in your contribution guide with clear roles. An owner looking at your system for the first time should immediately understand the process.

## Assign Clear Component Ownership

Each component needs a single accountable owner:

- **Owner responsibilities:**
  - Reviews requests to change the component
  - Maintains consistent design rationale and documentation
  - Decides when a variant is justified vs. when a fork is created
  - Responds to questions from product teams using the component
  - Advocates for updates when production usage diverges from spec

- **Make it visible:** Document the owner in your component library (e.g., "Button—owned by [Name, team]")

- **Rotate if needed:** If one person owns everything, that's a bottleneck. Distribute ownership so contributions don't stall.

When product teams know who owns a component, they contact the owner to propose changes instead of forking silently.

## Build a Self-Governing Contribution Process

A self-governing process requires clear, documented structure. Enforce these elements:

### 1. Proposal Format
Teams proposing a new component or significant change must submit:
- Component name and purpose (1–2 sentence design rationale)
- Use case(s): where and why it's needed
- Variants: which states, sizes, or configurations are required
- API sketch: rough outline of props, events, or styling hooks
- Figma file or sketch: visual reference or design exploration

Without this structure, proposals are vague and reviews go in circles.

### 2. Design Rationale
Every component must have a documented purpose statement:

> This component [does what]. It is used for [specific scenarios]. It differs from [existing components] because [purpose difference].

The rationale is not "a button that's big." It's "a button used for primary actions at the end of workflows; it draws attention through size and color contrast."

Store the rationale in your component documentation. When disputes arise (e.g., "should this button also handle secondary actions?"), the rationale is your arbiter.

### 3. Review Checklist
Reviewers should use a standardized checklist:

- [ ] Does the new component have a clear, documented purpose distinct from existing components?
- [ ] Does the design follow established patterns (spacing, typography, color)?
- [ ] Are all states documented (default, hover, active, disabled, loading)?
- [ ] Does the API/props list follow the system's conventions?
- [ ] Is there a do/don't guide that shows intended vs. misuse?
- [ ] Have we considered accessibility (WCAG compliance, keyboard navigation)?
- [ ] Does it work at all required breakpoints/contexts?
- [ ] Is the code quality consistent with the rest of the system?

A checklist prevents reviewer drift and ensures consistency.

### 4. Merge Criteria
Define what it takes to merge:

- [ ] Purpose is distinct and documented
- [ ] At least two reviewers sign off (or one owner + one peer)
- [ ] All checklist items are addressed
- [ ] Code is tested and documented
- [ ] Example usage is provided
- [ ] Changelog is updated

## Resolve Ambiguity at the Component Definition Stage

Your current situation stems from components being poorly defined. A team sees a "button" that doesn't quite fit, so they modify it. Instead:

- **Audit your existing components.** For each one, write a clear purpose statement. If the purpose is fuzzy, the component definition needs work.
- **Document the decision tree.** If you have Button, IconButton, and ButtonGroup, document when to use each one:
  - Button: text-based primary action
  - IconButton: icon-only actions in tight spaces
  - ButtonGroup: multiple related actions shown together
  
  Make the choice obvious so teams don't second-guess it.

- **Create an escape hatch.** If a team's use case genuinely doesn't fit, the process should allow it—but with visibility. They submit a proposal, and if it's approved, they contribute it back rather than fork it.

## Regular Audits: Compare System to Production

**Set up quarterly audits.** Pick 5–10 key components and audit production:

1. Take a screenshot of how the component is actually being used in shipped products
2. Compare it to the system specification
3. Document discrepancies:
   - Are colors off? Typography? Spacing?
   - Are there undocumented variants?
   - Are there patterns the system should support?

4. Use audit findings to drive prioritized updates:
   - If many teams need a variant, add it officially
   - If a component is misused, clarify the documentation and add do/don't examples
   - If teams are forking because of genuine gaps, close those gaps in the system

Audits create accountability. Teams know you're checking, and they're more likely to follow the system.

---

## Quick Summary

| Element | Action |
|---------|--------|
| **Contribution Model** | Document who proposes, reviews, approves |
| **Ownership** | Assign an owner per component |
| **Process** | Require proposal, rationale, review checklist, merge criteria |
| **Ambiguity** | Resolve at definition time with clear purpose statements |
| **Audits** | Compare system to production quarterly; close gaps |

Your teams are forking because it's easier than contributing. Make contributing easier—give them a clear process, responsive owners, and a system they can trust is authoritative. Audits keep it honest.
