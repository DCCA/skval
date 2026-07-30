# TypeScript MCP Tool: GitHub List Issues

## Tool Registration Code

```typescript
import { z } from "zod";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

// Define the input schema using Zod
const ListIssuesInputSchema = z.object({
  owner: z
    .string()
    .min(1)
    .describe("The repository owner (user or organization)"),
  repo: z
    .string()
    .min(1)
    .describe("The repository name"),
  state: z
    .enum(["open", "closed", "all"])
    .optional()
    .default("open")
    .describe("Filter issues by state: 'open', 'closed', or 'all'"),
  page: z
    .number()
    .int()
    .min(1)
    .default(1)
    .describe("Page number for pagination (starts at 1)"),
  per_page: z
    .number()
    .int()
    .min(1)
    .max(100)
    .default(30)
    .describe("Number of issues per page (1-100)"),
});

// Define the output schema for structured responses
const IssueSchema = z.object({
  id: z.number(),
  number: z.number(),
  title: z.string(),
  state: z.enum(["open", "closed"]),
  url: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

const ListIssuesOutputSchema = z.object({
  issues: z.array(IssueSchema),
  total_count: z.number(),
  page: z.number(),
  per_page: z.number(),
});

// Register the tool on the MCP server
server.registerTool({
  name: "github_list_issues",
  description:
    "List issues for a GitHub repository with optional filtering and pagination. Supports filtering by state (open, closed, or all). Returns paginated results with issue details including title, state, and timestamps.",
  inputSchema: ListIssuesInputSchema,
  outputSchema: ListIssuesOutputSchema,
  annotations: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false,
  },
  handler: async (input) => {
    const { owner, repo, state, page, per_page } = input;

    // Call GitHub API
    const queryParams = new URLSearchParams({
      state: state || "open",
      per_page: per_page.toString(),
      page: page.toString(),
    });

    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/issues?${queryParams}`,
      {
        headers: {
          Authorization: `token ${process.env.GITHUB_TOKEN}`,
          Accept: "application/vnd.github.v3+json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        `GitHub API error: ${response.status} - ${response.statusText}`
      );
    }

    const issues = await response.json();

    // Get total count from Link header or request
    const totalCountResponse = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/issues?${new URLSearchParams({
        state: state || "open",
        per_page: "1",
      })}`,
      {
        headers: {
          Authorization: `token ${process.env.GITHUB_TOKEN}`,
          Accept: "application/vnd.github.v3+json",
        },
      }
    );

    const total_count = parseInt(
      totalCountResponse.headers.get("X-Total-Count") || "0"
    );

    // Construct structured response
    const structuredData = {
      issues: issues.map((issue: any) => ({
        id: issue.id,
        number: issue.number,
        title: issue.title,
        state: issue.state,
        url: issue.html_url,
        created_at: issue.created_at,
        updated_at: issue.updated_at,
      })),
      total_count,
      page,
      per_page,
    };

    return {
      content: [
        {
          type: "text",
          text: `Found ${structuredData.issues.length} issue(s) on page ${page} (total: ${total_count}):\n\n${structuredData.issues
            .map((i: any) => `#${i.number}: ${i.title} (${i.state})`)
            .join("\n")}`,
        },
        {
          type: "structuredContent",
          data: structuredData,
        },
      ],
    };
  },
});
```

## Key Implementation Details

### Input Schema (Zod)
- **owner**: Required, non-empty string with clear description
- **repo**: Required, non-empty string for the repository name
- **state**: Optional enum (open/closed/all) with sensible default
- **page**: Pagination support with minimum value constraint
- **per_page**: Pagination support with range constraint (1-100)

All fields include descriptions to help clients understand each parameter.

### Annotations
- **readOnlyHint: true** — This tool only reads data, doesn't modify anything
- **destructiveHint: false** — Safe operation
- **idempotentHint: true** — Same parameters always return same results
- **openWorldHint: false** — Doesn't generate open-ended content

### Output Schema
The `outputSchema` defines the structured response format with:
- Array of issues with standardized fields
- Total count for pagination awareness
- Page and per_page for context about the returned slice

### Response Format
Returns both text content (human-readable summary) and structuredContent (machine-parseable data), allowing clients to choose how to process the results.

### Pagination Support
- Users can specify `page` (starting at 1) and `per_page` (up to 100 items)
- Enables LLM agents to retrieve large result sets across multiple calls
- Structured output includes pagination metadata for client awareness
