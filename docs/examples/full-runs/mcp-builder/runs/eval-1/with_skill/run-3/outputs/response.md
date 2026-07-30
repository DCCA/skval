# GitHub List Issues Tool Registration

Here's the complete TypeScript code to register the `github_list_issues` tool on your MCP server using the official MCP TypeScript SDK:

```typescript
import { z } from "zod";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { TextContent, ToolResult } from "@modelcontextprotocol/sdk/types.js";

// Define the input schema with Zod
const ListIssuesInputSchema = z.object({
  owner: z
    .string()
    .min(1)
    .describe("GitHub repository owner (user or organization)"),
  repo: z
    .string()
    .min(1)
    .describe("GitHub repository name"),
  state: z
    .enum(["open", "closed", "all"])
    .default("open")
    .describe("Filter issues by state: 'open', 'closed', or 'all' (default: 'open')"),
  page: z
    .number()
    .int()
    .min(1)
    .default(1)
    .describe("Page number for pagination (default: 1)"),
  per_page: z
    .number()
    .int()
    .min(1)
    .max(100)
    .default(30)
    .describe("Number of results per page (1-100, default: 30)"),
});

// Define the output schema for structured responses
const IssueSchema = z.object({
  id: z.number(),
  number: z.number(),
  title: z.string(),
  state: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  html_url: z.string(),
});

const ListIssuesOutputSchema = z.object({
  issues: z.array(IssueSchema),
  total_count: z.number(),
  page: z.number(),
  per_page: z.number(),
});

// Register the tool on the server
server.registerTool(
  "github_list_issues",
  "List issues for a GitHub repository with filtering and pagination support",
  ListIssuesInputSchema,
  async (input) => {
    const { owner, repo, state, page, per_page } = input;

    try {
      // Construct the API URL with query parameters for pagination and filtering
      const url = new URL(
        `https://api.github.com/repos/${owner}/${repo}/issues`
      );
      url.searchParams.set("state", state);
      url.searchParams.set("page", page.toString());
      url.searchParams.set("per_page", per_page.toString());

      // Make the API request
      const response = await fetch(url.toString(), {
        headers: {
          Accept: "application/vnd.github.v3+json",
          Authorization: `token ${process.env.GITHUB_TOKEN}`,
        },
      });

      if (!response.ok) {
        throw new Error(
          `GitHub API error: ${response.status} ${response.statusText}`
        );
      }

      const issues = await response.json();

      // Parse and validate the output
      const result = ListIssuesOutputSchema.parse({
        issues: issues.map((issue: any) => ({
          id: issue.id,
          number: issue.number,
          title: issue.title,
          state: issue.state,
          created_at: issue.created_at,
          updated_at: issue.updated_at,
          html_url: issue.html_url,
        })),
        total_count: issues.length,
        page,
        per_page,
      });

      // Return both text content and structured content
      return {
        content: [
          {
            type: "text" as const,
            text: `Found ${result.issues.length} issue(s) for ${owner}/${repo} (state: ${state})\n\n${result.issues
              .map(
                (issue) =>
                  `#${issue.number}: ${issue.title} (${issue.state})\n${issue.html_url}`
              )
              .join("\n\n")}`,
          },
          {
            type: "structuredContent" as const,
            data: result,
            mimeType: "application/json",
          },
        ],
      } as ToolResult;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      return {
        content: [
          {
            type: "text" as const,
            text: `Error fetching issues: ${errorMessage}`,
            isError: true,
          },
        ],
      } as ToolResult;
    }
  },
  {
    // Tool annotations
    readOnlyHint: true,
    idempotentHint: true,
    openWorldHint: false,
    // Optional: output schema for clients that support structured responses
    outputSchema: ListIssuesOutputSchema,
  }
);
```

## Tool Definition Summary

**Tool Name**: `github_list_issues`
- Follows consistent naming convention with service prefix and action-oriented form

**Input Schema** (Zod):
- `owner` (required): Repository owner with length constraint
- `repo` (required): Repository name with length constraint
- `state` (optional): Enum filter for issue state with sensible default
- `page` (optional): Pagination page number with minimum constraint
- `per_page` (optional): Results per page (1-100) with maximum constraint

**Annotations**:
- `readOnlyHint: true` — This operation does not modify state
- `idempotentHint: true` — Multiple identical calls return the same result
- `openWorldHint: false` — Behavior is fully determined by inputs

**Output**:
- Returns both human-readable text content and structured JSON via `structuredContent`
- Includes `outputSchema` definition so clients understand the response structure
- Text format lists issues with links; structured format provides machine-readable data

**Pagination Support**:
- `page` and `per_page` parameters enable paginating through large result sets
- Clients can fetch subsequent pages by incrementing the `page` number
- Per-page limit of 100 respects API rate limiting and response size constraints
