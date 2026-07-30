# Evaluation Plan for Confluence MCP Server

## Evaluation Strategy

Create exactly **10 independent, read-only test questions** that verify LLMs can navigate and synthesize information from your Confluence wiki using the MCP server tools.

### Question Design Rules

Each question must:
1. **Be Independent**: No question should require the output of another question to answer it.
2. **Be Read-Only**: Only invoke tools that retrieve or search content; no create, update, or delete operations.
3. **Be Complex**: Require at least 2 tool calls to answer (e.g., find a page, then search within that page for a specific value).
4. **Be Verifiable**: The expected answer must be a short, deterministic string that can be compared exactly (e.g., a date, a name, a numeric value, a specific phrase).
5. **Be Stable**: The expected answer should not change over time (avoid questions about "latest" unless the page is stable).
6. **Be Realistic**: Mirror how your team actually uses Confluence (e.g., finding process documentation, querying team rosters, extracting dates).

### Creation Process

1. **Tool Inspection**: List all available MCP tools on your server and their capabilities (e.g., `confluence_search_pages`, `confluence_get_page_content`, `confluence_list_spaces`).
2. **Content Exploration**: Browse your Confluence wiki and identify stable, complex content suitable for testing:
   - Policy pages with multiple sections and tables
   - Team rosters or meeting notes with extractable facts
   - Process documentation with numbered steps or embedded data
   - Reference pages with lists of projects, dates, or identifiers
3. **Question Creation**: For each of the 10 questions, manually:
   - Formulate the question as a user would ask it
   - Use your MCP server's tools to find the answer yourself
   - Verify the answer is deterministic and short
   - Document the tool call sequence needed to answer it
4. **Self-Verification**: Before finalizing, confirm each question by:
   - Calling the tools in sequence as an LLM would
   - Confirming the expected answer matches what the tools return
   - Checking the answer is stable (won't change in the next week/month)

## XML Output Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<evaluation>
  <metadata>
    <server_name>Confluence MCP Server</server_name>
    <creation_date>2026-07-30</creation_date>
    <total_questions>10</total_questions>
  </metadata>
  
  <qa_pair>
    <question>What is the official on-call rotation policy for the Platform team?</question>
    <answer>24-hour on-call windows rotate weekly among team members; primary is responsible for incident response within 15 minutes; backup assumes primary duties if primary is unavailable; escalation path goes to engineering manager.</answer>
  </qa_pair>

  <qa_pair>
    <question>In the Engineering handbook, what is the required minimum code review turnaround time?</question>
    <answer>24 hours</answer>
  </qa_pair>

  <qa_pair>
    <question>What is the email address of the current Data Engineering lead listed in the team directory?</question>
    <answer>elena.garcia@company.com</answer>
  </qa_pair>

  <qa_pair>
    <question>According to the Q3 2026 roadmap page, what feature is scheduled to ship in August?</question>
    <answer>Real-time collaboration API</answer>
  </qa_pair>

  <qa_pair>
    <question>How many total action items are listed as "Open" in the weekly standup notes for the week of July 21?</question>
    <answer>7</answer>
  </qa_pair>

  <qa_pair>
    <question>What is the deadline for the annual security audit mentioned in the compliance documentation?</question>
    <answer>2026-10-31</answer>
  </qa_pair>

  <qa_pair>
    <question>In the client onboarding runbook, what is the first step to take when a new customer signs up?</question>
    <answer>Send welcome email with API credentials and link to getting-started guide</answer>
  </qa_pair>

  <qa_pair>
    <question>According to the incident response playbook, what is the maximum time allowed to restore service during a Severity 1 incident?</question>
    <answer>4 hours</answer>
  </qa_pair>

  <qa_pair>
    <question>What technology stack is used for the new analytics dashboard mentioned in the tech decisions log from June?</question>
    <answer>React, PostgreSQL, Apache Superset</answer>
  </qa_pair>

  <qa_pair>
    <question>In the vendor management spreadsheet embedded in the procurement page, how many SaaS tools does the company currently subscribe to?</question>
    <answer>23</answer>
  </qa_pair>
</evaluation>
```

## Key Characteristics of This Format

- **Root Element**: `<evaluation>` wraps all content.
- **Metadata**: Optional section with server info and test parameters.
- **QA Pairs**: Each `<qa_pair>` contains a `<question>` and a single deterministic `<answer>`.
- **Answer Format**: Answers are short phrases, numbers, dates, or specific strings suitable for exact string matching.
- **No Sub-Questions**: Each question is self-contained; answers don't reference other questions.
- **Tool Chain Implicit**: The format doesn't encode *how* to answer (tool names, sequences); that's internal to your grading harness. It only encodes *what* to ask and *what* the right answer is.

## Implementation Checklist

- [ ] Create 10 questions by manually testing your Confluence MCP tools against stable wiki content.
- [ ] Verify each answer is deterministic and remains unchanged over at least a week.
- [ ] Ensure no question depends on the output of another.
- [ ] Export as XML with the schema above.
- [ ] Use this evaluation set to test LLM performance by:
  - Providing the questions to an LLM client configured with your MCP server
  - Recording the LLM's answers
  - Comparing each answer to the expected answer (exact string match)
  - Computing accuracy as (correct_answers / 10) × 100%
