# Design System Governance & Contribution Process

## The Root Problem

Product teams fork and modify your components because either:
1. The component doesn't quite fit their need, or
2. Your documentation is unclear about how to request a change

Fixing governance without fixing documentation makes it worse. Start by acknowledging that component definition, not enforcement, solves this problem.

## Document Your Contribution Model

Create a **CONTRIBUTING.md** file for your design system that specifies:

**Who can propose changes?**
- Anyone on product teams can open a proposal issue with a template.
- Anyone on the design systems team can fast-track proposals for critical issues.

**Who reviews?**
- Default: two people (one designer, one developer) from the design systems team.
- For breaking changes: add a project lead or design director.

**Who approves and merges?**
- Design systems lead or delegated component owner.

Make these roles and permissions explicit. A proposal that sits unreviewed for 3 weeks creates the incentive to fork and ship.

## Assign Clear Ownership

Each component needs one owner—not a committee. The owner is responsible for:
- Reviewing change proposals
- Making final decisions on variants and behavior
- Updating documentation when changes land
- Auditing production usage quarterly

A single owner (with a backup) makes decisions faster and prevents the "no one's responsible" trap.

## Create a Self-Governing Contribution Process

A self-governing process replaces arbitrary gatekeeping. Automate where possible and make decisions based on written criteria.

### Proposal Format
Require proposers to fill out:
- **Title:** Brief description of the change
- **Problem:** Why the current component isn't sufficient
- **Proposed solution:** What needs to change (visual spec, API changes, new variant)
- **Impact:** Which products use this component and how they're affected
- **Design rationale:** Why this is the right solution (not just "we need it")

### Design Rationale
For any new component or major change, require a 1–2 sentence statement of purpose. This is non-negotiable. Without it, you're making visual tweaks without understanding why, and the component drifts over time.

### Review Checklist
Reviewers check:
- [ ] Does the proposal solve the stated problem?
- [ ] Is the design rationale clear and aligned with the system's purpose?
- [ ] Are the changes backward-compatible, or is a migration plan documented?
- [ ] Does the component work across all required screen sizes and viewports?
- [ ] Are new variants or props necessary, or can the existing API support this?
- [ ] Is the documentation update included in the proposal?
- [ ] Does this duplicate or contradict an existing component?

### Merge Criteria
Merge only when:
- Design and code review both sign off
- The design rationale is documented and added to the system's reference
- Updated documentation (with examples, states, variants) is included
- At least one product team has tested the change in their own code

## Resolve Ambiguity at the Definition Stage

The reason product teams ship modified copies is that your component definitions are ambiguous. A Button component that doesn't specify when to use outline vs. solid, or what sizes are allowed, invites unofficial variants.

Before shipping a component, write down:
- **Purpose:** What is this component for?
- **When to use it:** Specific use cases
- **When NOT to use it:** What other components should be used instead
- **Variants & sizes:** What's supported and what isn't
- **Do/Don't examples:** Real screenshots showing correct and incorrect usage

This documentation is the gate. If a product team's need doesn't match any of your documented variants, they have grounds to request a new variant or exception. You can then decide: is this a legitimate gap, or are they using the component wrong?

## Audit Production Regularly

Set up a quarterly audit process:

1. **Snapshot:** Export all component instances from production code (Figma, Storybook, code repos).
2. **Compare:** List what components actually exist vs. what's documented.
3. **Investigate gaps:** For each discrepancy, ask: Is this a genuine new variant that should be documented, or an off-system fork?
4. **Action items:** Create proposals to either document the new variant or migrate the off-system version back to the system.

This audit catches drift before it becomes insurmountable. It also gives you data on which components are fragile (too many undocumented variants) vs. stable.

## Implementation Timeline

1. **Week 1:** Document your current contribution model and ownership assignments.
2. **Week 2–3:** Audit production to find all off-system variants and document them.
3. **Week 4:** Publish updated component definitions with clear purpose statements and do/don't examples.
4. **Ongoing:** Review all proposals within 5 business days. Audit production quarterly.

Governance without documentation is theater. Documentation with clear ownership and review criteria is what actually stops forking.
