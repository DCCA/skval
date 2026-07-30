# Design System Governance: Stopping Undocumented Copies

The root of your problem is that product teams feel empowered to fork rather than contribute. Fix this by making contribution easy, ownership clear, and divergence visible.

## 1. Document Your Contribution Model

Create a CONTRIBUTING.md file that explicitly names:
- **Who can propose** a new component or change? (any team, or core team only?)
- **Who reviews** proposals? (design system lead, design lead, tech lead, all three?)
- **Who approves** for merge? (single owner, consensus, LGTM + 1?)
- **What does approval mean?** (merged to main, deployed, communicated to all teams?)

Example:
```
- Proposal: Any product team or designer
- Review: Design systems lead + at least one developer
- Approval: Design systems lead merges
- Communication: Changelog + team Slack announcement
```

This removes ambiguity and makes it clear that borrowing from the system is easier than forking.

## 2. Assign a Clear Owner Per Component

Each component needs a single owner (usually a designer or pair), responsible for:
- Deciding what the component is and what it's not
- Reviewing pull requests that touch it
- Updating documentation when behavior changes
- Being the point of contact for questions

Document ownership in your component library (README or CODEOWNERS file). Without clear ownership, components decay and teams bypass them.

## 3. Build a Self-Governing Contribution Process

A good process has four gates that catch drift before it reaches production:

### Proposal Format
Contributors must fill out a template before starting work:
- What is the change and why?
- Does it fit an existing component or create a new one?
- What products/teams will use it?
- Any accessibility or performance concerns?

### Design Rationale
Tied to your component definition, not aesthetics:
- *Purpose*: One sentence on why this component exists
- *Scope*: What does it do and what's out of scope?
- *Behavior*: How does it respond to user actions, errors, loading?

### Review Checklist
Reviewers use a consistent list:
- [ ] Purpose statement is clear and distinct from similar components
- [ ] Component definition matches the proposal
- [ ] Visual design follows system constraints (tokens, grid, spacing)
- [ ] Code follows accessibility and performance standards
- [ ] Documentation is complete (do's, don'ts, states, variants)
- [ ] All related components have been considered (e.g., adding a variant to Modal affects Dialog)

### Merge Criteria
Don't merge until:
1. All checklist items pass
2. Owner approves
3. At least one other discipline (design, dev, content) reviews
4. Documentation is live and linked from the component

## 4. Resolve Ambiguity at Definition, Not After

When you see a team modify a component without proposing the change, trace back to the component definition. Odds are:
- The definition was too vague (purpose wasn't clear)
- The component didn't have an owner
- The contribution process was harder than modifying a copy

Update the definition to close the gap. If Button states weren't documented, document them. If ownership wasn't clear, assign it. Don't punish teams—make the right path easier.

## 5. Audit Production vs. Documentation Regularly

Set up a quarterly or bi-annual audit:
- **Audit checklist**: Sample 3–5 products using each core component
- **What to compare**: Does the implementation match the documented version?
- **Where they differ**: Document drift, note why (old design system in old product? bug? intentional change?)
- **Action items**: Update documentation if definition changed, or file a bug if implementation is stale

Document findings in a shared log. Share patterns (e.g., "Buttons in Payments look different because of older design tokens") with the team so they can plan migrations.

## Quick Start This Week

1. Create CONTRIBUTING.md with roles and the four gates
2. Assign an owner to your top 3 components
3. Audit one product against your Button component
4. File an issue for each discrepancy, label by severity
5. Track in your backlog alongside feature work

This tells teams: "The design system is maintained, it's safe to use, and contributing is easier than forking."
