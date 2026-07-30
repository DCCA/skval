# Confluence MCP Server Evaluation Set Guide

## Evaluation Set Specification

### Overview
Your Confluence MCP evaluation set should contain **10 independent, read-only, complex questions** that test whether LLMs can effectively use your server to retrieve, search, and synthesize information from your wiki.

### Required Question Properties

1. **Independent**: Each question must stand alone. An LLM answering question 5 should not need context from answering question 3. This ensures each evaluation measures actual tool usage, not knowledge carried from previous answers.

2. **Read-Only**: Questions must require only non-destructive operations (search, retrieve, list). No creating, updating, or deleting pages.

3. **Complex**: Each question should require **multiple tool calls** to answer:
   - Example: "Search for all pages mentioning a specific feature, then retrieve the most recent one to extract a specific detail."
   - Complexity differentiates random guessing from actual tool usage.

4. **Verifiable**: Answers must be a single, clear, string-comparable result:
   - ✅ Good: "The performance SLA is 99.5% uptime"
   - ❌ Avoid: "The document discusses performance, budget, and timeline" (too vague)

5. **Stable**: Questions and answers must not change if re-run:
   - Avoid questions about "the most recent meeting notes" (answers drift over time)
   - Use stable reference points: "According to the Q4 2025 budget page..."

### Creation Process

#### Step 1: Tool Inspection
Enumerate all MCP tools your server exposes:
- Search/query tools (e.g., `search_pages`, `search_by_label`)
- Retrieval tools (e.g., `get_page`, `list_pages_in_space`)
- Metadata tools (e.g., `get_space_info`, `list_spaces`)

#### Step 2: Content Exploration
Perform read-only content exploration of your Confluence instance:
- Identify stable, factual pages (policies, specifications, reference docs)
- Note pages with multi-level information (e.g., a policy page with nested sub-pages or sections)
- Record page IDs, titles, and key terms for reference

#### Step 3: Question Design
For each tool or tool combination, design a question that:
- Requires that tool + at least one other tool call
- Targets stable, factual content
- Has a single, verifiable answer

Example workflow:
- Tool combo: `search_pages` + `get_page` → Question: "Search for pages about [topic], then extract [specific fact]"
- Tool combo: `list_spaces` + `search_pages` → Question: "List all spaces, identify the one matching [criterion], then find [specific content]"

#### Step 4: Self-Verification
Before finalizing each question:
- Answer it yourself using your MCP tools
- Verify the answer is stable and unambiguous
- Verify at least 2 tool calls are needed

### Output Format: XML

Your evaluation set must be saved as `evaluation.xml` with the following structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<evaluation>
  <qa_pair>
    <question>What is the documented on-call rotation schedule for the infrastructure team?</question>
    <answer>The on-call rotation is defined in 2-week sprints, rotating between Alice, Bob, and Charlie, with escalation to the team lead if no response within 15 minutes.</answer>
  </qa_pair>

  <qa_pair>
    <question>Which spaces in the Confluence instance are owned by the Product team, and what is the primary document format they use for requirements?</question>
    <answer>The Product team owns the 'Product Requirements' and 'Roadmap' spaces. Their primary document format is structured requirements tables with status columns.</answer>
  </qa_pair>

  <qa_pair>
    <question>Find all pages labeled 'security-critical' in the Engineering space and identify which one was last updated most recently.</question>
    <answer>Pages with 'security-critical' label: 'Authentication Best Practices', 'Data Encryption Standards', 'Third-party Vendor Review'. The 'Data Encryption Standards' page was last updated on 2025-07-15.</answer>
  </qa_pair>

  <!-- ... 7 more qa_pair elements, total of 10 -->

  <qa_pair>
    <question>Search the wiki for pages mentioning 'API rate limits' and summarize the maximum requests per minute for the public API tier.</question>
    <answer>The public API tier allows a maximum of 1000 requests per minute per API key, as documented in the 'API Rate Limiting Policy' page under the Public Tier section.</answer>
  </qa_pair>
</evaluation>
```

### Key Rules

- **10 questions exactly**: The full evaluation should contain 10 `<qa_pair>` entries
- **Single XML file**: Save as `evaluation.xml` or `confluence_evaluation.xml`
- **One answer per question**: No multiple valid answers or "any of the following"
- **No markdown or HTML in answers**: Keep answers as plain text for reliable string comparison
- **Include page names or spaces in questions** where relevant, to provide context for stability and verification

### Quality Checklist

Before finalizing your evaluation set:
- [ ] All 10 questions are independent (can be answered in any order)
- [ ] All questions are read-only (no tool calls that modify Confluence)
- [ ] Each question requires at least 2 MCP tool calls to answer correctly
- [ ] All answers are single, verifiable strings (no "or" alternatives)
- [ ] All answers reference stable content (dates, policies, specifications)
- [ ] Answers were verified by the author using the MCP server
- [ ] XML is well-formed and valid
- [ ] No answers contain markdown, HTML, or line breaks
