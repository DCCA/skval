# MCP Server Evaluation Plan: Creating a Comprehensive Test Suite

## Overview

Your evaluation set should contain **10 independent questions** designed to test whether LLMs can effectively use your Confluence MCP server to accomplish realistic tasks. Each question should require multiple tool calls and deep exploration to answer.

## Question Requirements

Each of your 10 evaluation questions must satisfy these criteria:

### 1. **Independent**
Questions should not depend on answers to other questions. Each should be solvable in isolation. This allows evaluation across different runs and clients without cascading failures.

### 2. **Read-Only**
Only use non-destructive operations. No creating, updating, or deleting pages. This ensures evaluations can run repeatedly without side effects.

### 3. **Complex**
Each question should require:
- Multiple MCP tool calls to answer
- Deep exploration across different pages, spaces, or content
- Combining data from multiple sources
- Not just a single lookup

### 4. **Realistic**
Ground questions in actual use cases people have with their wiki:
- Finding specific information across the knowledge base
- Extracting patterns or comparisons from related pages
- Answering business or technical questions using wiki content
- Identifying documentation gaps or inconsistencies

### 5. **Verifiable**
Each question must have:
- A **single, clear answer** that can be verified by string comparison
- No subjective interpretation
- Exact values (numbers, dates, specific terms) when possible

### 6. **Stable**
Answers must not change over time. Avoid questions about:
- Current dates or "latest" content
- Frequently updated pages
- Temporary announcements or statuses
- Data that expires

Prefer questions about established documentation, historical records, or static reference material.

---

## Creation Process

Follow this four-step workflow:

### Step 1: Tool Inspection
List all available tools your Confluence MCP server exposes. For example:
- `confluence_search_pages`
- `confluence_get_page`
- `confluence_list_spaces`
- `confluence_get_page_children`
- `confluence_list_page_labels`

Document each tool's capabilities to understand what data exploration is possible.

### Step 2: Content Exploration
Using only READ-ONLY operations, explore your Confluence instance:
- Search for key topics and recurring themes
- Navigate space hierarchies
- Identify pages with rich relational data (pages with many children, heavily cross-referenced content)
- Note pages with structured data (tables, lists, code samples, metadata)
- Look for opportunities to ask questions requiring multi-step reasoning

### Step 3: Question Generation
Create 10 questions based on your exploration. For each question:
- Choose a realistic information-seeking task
- Ensure it requires exploring multiple pages or filtering across many results
- Write the question clearly and unambiguously
- Identify the expected answer in advance

**Example question structure:**
"Find pages in the Engineering space tagged with 'api-design'. Among those, identify the page with the most child pages. What is the exact title of that page?"

### Step 4: Self-Verification
**Solve each question yourself** using your MCP server tools before finalizing:
- Walk through the exact steps an LLM would take
- Document which tools you called and in what order
- Verify the answer is stable and won't change over time
- Confirm the question is unambiguous

---

## Output Format: XML Specification

Create an XML file named `evaluations.xml` with this structure:

```xml
<evaluation>
  <qa_pair>
    <question>What is the title of the API design guide page in the Engineering space?</question>
    <answer>API Design Guide v2</answer>
  </qa_pair>
  <qa_pair>
    <question>How many distinct teams are documented in the Organizational Structure page?</question>
    <answer>7</answer>
  </qa_pair>
  <qa_pair>
    <question>Find all pages tagged with 'deprecated' in the Engineering space. What is the exact name of the oldest page (by creation date)?</question>
    <answer>Legacy Authentication Module</answer>
  </qa_pair>
  <!-- 7 more qa_pairs... -->
</evaluation>
```

### XML Requirements:
- **Root element**: `<evaluation>` wraps all questions
- **Each question**: Contained in a `<qa_pair>` element
- **Question field**: `<question>` with the full, unambiguous question text
- **Answer field**: `<answer>` with the exact expected answer (string that can be matched exactly)
- **Total**: Exactly 10 `<qa_pair>` elements

---

## Quality Checklist

Before finalizing your evaluation set, verify:

- [ ] All 10 questions are present
- [ ] Each question is independent (can be answered without other questions)
- [ ] Each question uses only read-only operations
- [ ] Each question requires at least 2 tool calls to answer
- [ ] Each question is grounded in realistic use cases
- [ ] Each answer is a single, stable value (not a list or multi-part answer)
- [ ] No answer depends on current date, "latest", or frequently-changing data
- [ ] Questions cover different tool capabilities (search, list, get, etc.)
- [ ] Questions explore different spaces/pages in your wiki
- [ ] All answers have been verified by you running the tools yourself

---

## Running the Evaluation

Once your XML file is created, you can evaluate whether LLMs can effectively use your Confluence MCP server by:
1. Providing an LLM access to your MCP server
2. Presenting each question
3. Checking if the LLM's answer matches the expected answer exactly
4. Calculating accuracy across all 10 questions

This provides quantitative feedback on how well your tool design enables real-world use.
