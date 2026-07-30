# MCP Evaluation Set Plan for Confluence Wiki Server

## Overview

Your evaluation set should test whether LLMs can discover, use, and reason over your MCP server's tools and content effectively. This requires 10 independent read-only questions that are realistic, complex, and verifiable.

## Evaluation Structure

Create **exactly 10 evaluation questions** as `<qa_pair>` entries in an XML file. Each pair must:

1. **Be independent**: No question should depend on the outcome of another. Each LLM attempt should be able to solve any question in isolation.

2. **Be read-only**: Use only tools that retrieve or inspect content (search, read, list, query). No mutations, deletions, or updates.

3. **Be complex**: Require the LLM to make **multiple tool calls** in sequence:
   - Example: Search for a page → read its content → extract specific information → cross-reference with related pages
   - Not: "What is the title of page X?" (single call)

4. **Be realistic**: Model actual use cases your team would do:
   - Finding documentation about a feature
   - Comparing information across multiple pages
   - Extracting structured data from unstructured content
   - Tracing dependencies or relationships

5. **Have a single, verifiable answer**: The answer must be:
   - A single string, number, or short structured output (not a paragraph)
   - Stable over time (won't change between runs unless content actually changes)
   - Verifiable by exact string matching or simple string comparison

## Creation Process

1. **Inspect your tools** (0–1 hours):
   - List all tools your server exposes (search, read, list_pages, get_metadata, etc.)
   - Document their signatures and return types
   - Identify which tools enable multi-step workflows

2. **Explore content** (2–4 hours):
   - Read representative pages from your Confluence instance
   - Identify patterns: page hierarchies, linked documents, structured metadata
   - Note which pages are stable and unlikely to change

3. **Design 10 questions** (2–3 hours):
   - For each question, imagine an LLM using your tools to solve it
   - Write the question, then solve it yourself step-by-step
   - Verify the answer is stable and string-matchable
   - Adjust the question if the answer is ambiguous or too volatile

4. **Self-verify** (1–2 hours):
   - Run each question against your server manually
   - Confirm the answer is correct and reproducible
   - Time how many tool calls each question requires (aim for 3–5 per question)

## XML Output Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<evaluation>
  <qa_pair id="1">
    <question>What is the owner of the Confluence page titled "API Authentication"?</question>
    <answer>alice@company.com</answer>
  </qa_pair>
  <qa_pair id="2">
    <question>List the titles of all child pages under "Engineering" in order of creation date.</question>
    <answer>Infrastructure Runbook; Deployment Guide; Monitoring Setup</answer>
  </qa_pair>
  <qa_pair id="3">
    <question>Find the section in the "Database Performance" documentation that discusses indexing strategy, and extract the first three recommendations as a comma-separated list.</question>
    <answer>Use clustered indexes; Analyze query patterns; Monitor index fragmentation</answer>
  </qa_pair>
  <!-- 7 more qa_pair entries ... -->
</evaluation>
```

## Example Question Design

**Question**: What is the latest version number mentioned in the "Release Notes" page, and what date was it published?

**Reasoning**:
- Requires searching for "Release Notes" page
- Requires reading the page content
- Requires extracting version and date (multiple values)
- Answer: "v2.1.4; 2025-07-15" (stable, verifiable)
- Multi-step: 2–3 tool calls

## Summary

- **10 independent, read-only questions**
- **3–5 tool calls per question** (requires multiple steps)
- **Single, stable answers** (string/date/number, verifiable)
- **XML file** with `<evaluation>` root and `<qa_pair>` children
- **Self-verified**: You solve each question before finalizing
- **Output file**: `confluence-evaluation.xml`
