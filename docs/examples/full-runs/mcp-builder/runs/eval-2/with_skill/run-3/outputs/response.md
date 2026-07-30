# Creating Evaluations for Your Confluence MCP Server

Your evaluation set must demonstrate that LLMs can effectively use your MCP server to solve realistic, complex problems. Here's exactly what to do.

## Evaluation Requirements

### Count & Independence
- **10 total questions** (exactly this count—no more, no fewer)
- Each question must be **independent** of the others. Agents should be able to answer any question without first answering another question. This ensures they work in any order and test your server reliably.

### Read-Only & Non-Destructive
- **Only non-destructive operations**: Questions can only require read-only tool calls
- No create, update, or delete operations
- No wiki modifications
- Agents must not need to assume successful previous operations

### Complexity, Realism & Verifiability
- **Complex**: Each question requires multiple tool calls and deep exploration, not just a single API call
  - Example: "List all pages in space X" is too simple
  - Better: "Find all pages in space X tagged with 'urgent' that were updated in the last week by members of team Y, and list their modification dates"
- **Realistic**: Based on real use cases—questions humans actually need answered about their wiki
  - Example tasks: finding documentation by topic, tracking recent changes, discovering related content
- **Verifiable**: Each answer is a single, clear fact that can be verified by string comparison
  - Answers must be deterministic and won't change between test runs
  - Example answers: a page ID, a specific string from a page, a count of matching pages
- **Stable**: Answer won't change over time or due to wiki updates
  - Avoid questions whose answers depend on current date or rapidly changing data
  - Better: questions about stable content, historical facts, or structural elements

## Evaluation Creation Process

### Phase 1: Tool Inspection
1. List all tools your MCP server provides
2. For each tool, note:
   - What data it retrieves
   - What filters/parameters it accepts
   - What fields are returned
3. Understand what combinations of tools enable complex queries

### Phase 2: Read-Only Content Exploration
1. Use your server's read-only operations to explore actual wiki content
2. Discover:
   - What spaces exist and their content
   - What pages contain what information
   - What metadata is available (creation dates, authors, tags)
   - What relationships exist between pages
3. Map out realistic scenarios that would require tool combinations

### Phase 3: Question Generation
1. For each complex scenario you discovered, write a question that:
   - Requires multiple tool calls across different aspects of the wiki
   - Has a single, clear answer
   - Is verifiable (you've already found the answer in Phase 2)
   - Won't change between runs
2. Make the question realistic and specific to your wiki's content

### Phase 4: Answer Verification
1. For each question, solve it yourself using your MCP server
2. Document the exact answer—this is your ground truth
3. Verify it won't change if the question is asked again
4. Verify the answer is simple enough to verify by string comparison

## Output Format: XML

Create a single XML file with this exact structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<evaluation>
  <qa_pair>
    <question>Your first complex question here</question>
    <answer>The exact, verifiable answer</answer>
  </qa_pair>
  <qa_pair>
    <question>Your second complex question here</question>
    <answer>The exact, verifiable answer</answer>
  </qa_pair>
  <!-- ... 8 more qa_pair elements for a total of 10 ... -->
</evaluation>
```

### XML Requirements
- Root element: `<evaluation>`
- Each question/answer pair: `<qa_pair>` element
- Each pair contains:
  - `<question>` — The full question text (can be multiple sentences)
  - `<answer>` — The exact answer (string, number, or brief fact)
- One pair per question; 10 pairs total
- Answers must be verifiable by exact string match (case-sensitive)

## Example Evaluation (Confluence Wiki)

Here's a sample evaluation structure to illustrate the concepts:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<evaluation>
  <qa_pair>
    <question>In the Engineering space, find all pages created in the last 30 days that have the 'frontend' label, then identify which one has the most recent update timestamp. What is the title of that page?</question>
    <answer>React Component Guidelines</answer>
  </qa_pair>
  <qa_pair>
    <question>Search for all pages in the Documentation space that mention both "API authentication" and "OAuth". How many such pages exist?</question>
    <answer>3</answer>
  </qa_pair>
  <qa_pair>
    <question>Find the page titled "Database Architecture" in the Engineering space. What is the ID of the parent page it is nested under?</question>
    <answer>ENG-42857</answer>
  </qa_pair>
  <qa_pair>
    <question>List all pages created by the user "alice.dev" in spaces that start with "Team-". What is the creation date of the most recently created page?</question>
    <answer>2024-03-15</answer>
  </qa_pair>
  <qa_pair>
    <question>In the Product Roadmap space, find all pages with the "Q2-2024" label that reference (via child pages or content) pages in the Marketing space. How many such cross-space relationships exist?</question>
    <answer>2</answer>
  </qa_pair>
  <qa_pair>
    <question>Search for pages containing the word "deprecation" in all spaces. Identify the space that contains the most such pages. What is the name of that space?</question>
    <answer>Engineering</answer>
  </qa_pair>
  <qa_pair>
    <question>Find all pages in the Engineering space that were updated by "bob.architect" in the past 60 days. What is the title of the oldest (earliest update date) among them?</question>
    <answer>Infrastructure Standards</answer>
  </qa_pair>
  <qa_pair>
    <question>In the Company Handbook space, find the page titled "Vacation Policy". What is the date it was last modified?</question>
    <answer>2024-02-28</answer>
  </qa_pair>
  <qa_pair>
    <question>Search across all spaces for pages labeled both "security" and "compliance". Count how many such pages exist and verify: if there are 5 or fewer, what is the title of the most recently updated one?</question>
    <answer>SOC 2 Audit Checklist</answer>
  </qa_pair>
  <qa_pair>
    <question>List all spaces in the wiki that contain at least one page with the "archived" label. How many spaces meet this criteria?</question>
    <answer>4</answer>
  </qa_pair>
</evaluation>
```

## Summary Checklist

Before finalizing your evaluation file:
- [ ] Exactly 10 qa_pair elements
- [ ] Each question is independent (can answer in any order)
- [ ] Each question requires only read-only operations
- [ ] Each question is complex (multiple tool calls)
- [ ] Each question is realistic (based on actual use cases)
- [ ] Each answer is a single, clear, verifiable value
- [ ] Answers are stable (won't change over time)
- [ ] I've verified each answer myself
- [ ] XML structure is valid (root `<evaluation>`, each pair has `<question>` and `<answer>`)
- [ ] File encoding is UTF-8
