# Evaluation Set Creation Guide for Confluence Wiki MCP Server

To test whether LLMs can effectively use your Confluence wiki MCP server, create a comprehensive evaluation set following this process.

## Evaluation Structure

Create exactly **10 evaluation questions** that test different aspects of your server's functionality. Each question must be:

- **Independent**: Not dependent on answers or actions from other questions
- **Read-Only**: Only non-destructive operations required (no creating, deleting, or modifying content)
- **Complex**: Requiring multiple tool calls to explore data and synthesize an answer
- **Realistic**: Based on actual use cases your team would encounter
- **Verifiable**: Single, clear answer that can be verified by simple string comparison
- **Stable**: Answer won't change over time (avoid questions with temporal data like "latest")

## Creation Process

Follow these four steps to create your evaluation set:

### Step 1: Tool Inspection
List all available tools your MCP server exposes:
- Space listing and querying
- Page search and retrieval
- Content viewing (including attachments, comments, history)
- Metadata extraction (dates, authors, permissions)
- Hierarchical navigation

Document what each tool does and what data it returns.

### Step 2: Content Exploration
Use READ-ONLY tools to explore your Confluence instance:
- Scan spaces and pages to understand structure and content
- Identify pages with rich content (multiple sections, links, tables)
- Note pages with historical data, metadata, or interdependencies
- Find content with specific patterns (e.g., decision documents, technical specifications)

### Step 3: Question Generation
Create 10 complex questions that:
- Require combining multiple tool calls (e.g., search → retrieve → analyze)
- Test navigation across spaces and page hierarchies
- Test extraction of structured data from content
- Require inferring answers from multiple pieces of information
- Cover different server capabilities (search, retrieval, metadata extraction)

Examples of good question patterns:
- "Find all pages by author X that mention topic Y, and count them"
- "What is the most recently updated page about Z in space S?"
- "List all pages linked from page P, sorted by creation date"
- "Find the page that discusses decision D and identify who approved it"

### Step 4: Answer Verification
For each question:
1. Use your server's tools to find the answer yourself
2. Verify the answer is correct by double-checking sources
3. Confirm the answer is a single, clear string or number (e.g., "42", "Daniel", "Confluence Architecture", not "approximately 40-50")
4. Confirm the answer is stable and won't change (avoid time-dependent answers)

## Output Format

Create an XML file with this structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<evaluation>
  <qa_pair>
    <question>Find the highest-level architecture page in the Engineering space and identify the last person who edited it. What is their username?</question>
    <answer>sarah_chen</answer>
  </qa_pair>
  
  <qa_pair>
    <question>Search for all pages in the Product space tagged with "roadmap" and count how many were created in 2024. What is the count?</question>
    <answer>7</answer>
  </qa_pair>
  
  <qa_pair>
    <question>Find the page titled "API Design Guidelines" and identify the first internal link mentioned in its content. What is the title of that linked page?</question>
    <answer>REST Best Practices</answer>
  </qa_pair>
  
  <qa_pair>
    <question>Locate the decision record about authentication strategy. What date was the decision made (YYYY-MM-DD)?</question>
    <answer>2024-03-15</answer>
  </qa_pair>
  
  <qa_pair>
    <question>List all pages in the Design Systems space that reference component naming conventions. How many such pages exist?</question>
    <answer>3</answer>
  </qa_pair>
  
  <qa_pair>
    <question>Find the page with the most comments in the Support space. How many comments does it have?</question>
    <answer>42</answer>
  </qa_pair>
  
  <qa_pair>
    <question>Search for pages containing "deployment" in the DevOps space and identify the author of the most recent one. What is their email address?</question>
    <answer>devops-team@company.com</answer>
  </qa_pair>
  
  <qa_pair>
    <question>Find the page that documents the company's incident response procedure and identify how many sections it contains.</question>
    <answer>6</answer>
  </qa_pair>
  
  <qa_pair>
    <question>Locate all pages in the Security space that mention "GDPR" and identify which one was created earliest. What is its page ID?</question>
    <answer>12847362</answer>
  </qa_pair>
  
  <qa_pair>
    <question>Find the FAQ page in the Knowledge Base space and count how many answers reference external documentation links.</question>
    <answer>8</answer>
  </qa_pair>
</evaluation>
```

## Key Guidelines

- **Single, Verifiable Answers**: Each answer must be a string or number that can be matched exactly (not "approximately X" or ranges)
- **Multiple Tool Calls**: Each question should require 2+ API calls (search, then retrieve details; navigate hierarchies; combine information)
- **No Temporal Dependencies**: Avoid questions like "latest" or "most recently created" unless your content is static
- **Comprehensive Coverage**: Span different server features (search, metadata, navigation, content analysis)
- **Realistic Scenarios**: Base questions on actual work humans do with Confluence (finding decisions, understanding architecture, following procedures)

## Running Your Evaluation

Once you've created your XML file, you can run it with your MCP server to test how well LLMs can use your tools to answer these questions. The evaluation framework will:

1. Feed each question to an LLM with your server's tools available
2. Capture the LLM's answer
3. Compare it to the expected answer using exact string matching
4. Report success/failure rates across all 10 questions

This gives you concrete data on whether your MCP server design enables effective LLM usage.
