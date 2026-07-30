# Design System Governance & Contribution Process

The root cause of your problem is ambiguous documentation. When teams don't know what a component is supposed to be, they'll quietly ship their own version. Fix this with a documented, self-governing contribution process.

## 1. Define a Contribution Model

Document who can do what:

**Propose:** Who can propose changes to the design system?
- Any designer or developer (low barrier to entry; ideas come from the trenches)

**Review:** Who reviews proposals?
- At least one designer and one developer (catches cross-discipline problems early)
- Optionally: a content strategist (for components with user-facing text)

**Approve & Merge:** Who has final say?
- A design system owner or steward (one person or a small team, typically 1–2 people)
- They're responsible for consistency and long-term coherence

**Example:**
```
Propose: Anyone—design or eng teams
Review: 1 designer + 1 engineer (assign in PR/issue)
Approve: @design-systems-owner
```

This prevents bottlenecks (anyone can propose) while ensuring quality (reviewers bring different perspectives).

## 2. Assign Component Owners

Each component in your system needs a clear owner:

```
Button — @designer-a (designer), @engineer-b (engineer)
Modal — @designer-c (designer), @engineer-d (engineer)
Toast — @designer-e (designer), @engineer-a (engineer)
```

An owner isn't an emperor—they're the person who understands the component best and is responsible for:
- Keeping documentation up to date
- Reviewing PRs that change the component
- Flagging when production code drifts from the documented spec
- Proposing evolution (new states, new sizes) when teams ask for it

Assign owners to **pairs** (one designer, one engineer) so there's cross-discipline ownership from the start.

## 3. Build a Self-Governing Contribution Process

Create a formal process. This doesn't have to be complex; it just has to be **explicit and enforced**.

### A. Proposal Format

When a team wants to add or change a component, they must submit (via GitHub issue or a design doc—pick one):

1. **Component name & ID** (e.g., "Tabs")
2. **Design rationale** (1–2 sentences on purpose; see the component definition skill)
3. **Proposed behavior** (states, variants, accessibility requirements)
4. **Design files** (Figma link or screenshot)
5. **Code / implementation** (branch or PR, even if rough)
6. **Justification:** Why doesn't an existing component solve this?

### B. Design Rationale

This is non-negotiable. It's the single source of truth and prevents the naming wars you're having now. See the "Component Definition Process" skill for how to write one.

### C. Review Checklist

Reviewers must check:

- [ ] Design rationale is clear and distinct from existing components
- [ ] Proposed name aligns with your naming conventions
- [ ] Behavior and states are documented with do/don't examples
- [ ] Design matches your tokens (spacing, color, typography)
- [ ] Code follows your component API conventions (props, slots, events)
- [ ] Accessibility is baked in (ARIA, keyboard nav, contrast)
- [ ] Documentation is complete enough that another team could use it without asking

### D. Merge Criteria

Approve only when:
1. Design rationale is approved by the designer owner
2. Code quality and API are approved by the engineer owner
3. All checklist items are resolved
4. The component is added to your design tool (Figma), not just documented

Don't merge until the component exists in **both** design and code, visible to teams who need it.

## 4. Document the Ambiguities Away

The reason teams ship modified copies is usually:
- The component definition is vague ("it looks like a button but sometimes..." — like what?)
- Documentation is missing ("does this component support X?" — nobody knows)
- Accessibility is unclear ("can I disable this?" — no guidance)

Resolve these **at definition time**, not after shipping. If a reviewer isn't sure whether a component should support something, it goes back for clarification. This is not slowing you down—it prevents the silent drift that's killing your consistency now.

## 5. Audit Production Against System

Once a quarter (or monthly for a fast-moving product):

1. **Walk production** — actually use your product
2. **Screenshot components** as they appear live
3. **Compare against your system** — Figma files, documented specs
4. **Log discrepancies** — "Button in Settings page uses old color" or "Modal in Checkout missing close button"
5. **Create issues** to bring production back in line
6. **Assign to component owners** to fix

Audits catch silent drift early. They also help you see which components need evolution (if production keeps deviating the same way, your design system is probably missing a variant).

## Implementation Checklist

- [ ] Document your contribution model (one-pager: propose/review/approve roles)
- [ ] Assign owners to each existing component (pairs: 1 designer + 1 engineer)
- [ ] Create a proposal template (GitHub issue or doc template)
- [ ] Add review checklist to your contribution guide
- [ ] Post this all in your design system docs (Notion, Confluence, or a `CONTRIBUTING.md` file)
- [ ] Schedule the first audit and assign someone to run it monthly
- [ ] For existing components that lack rationale, add one in the next sprint (owner's job)

This is governance, not bureaucracy. The goal is to make it easier for teams to do the right thing (use your system) than the easy thing (ship their own copy). Once the process is clear and the components are well-documented, compliance becomes automatic.
