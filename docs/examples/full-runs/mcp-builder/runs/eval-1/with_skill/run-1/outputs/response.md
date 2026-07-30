# TypeScript Tool Registration: GitHub List Issues

Here's the complete TypeScript code to register the `github_list_issues` tool on your MCP server using the official MCP TypeScript SDK:

```typescript
import { z } from "zod";

// Define the input schema with constraints
const github_list_issues_inputSchema = z.object({
  owner: z
    .string()
    .min(1)
    .describe("GitHub repository owner (username or organization)"),
  repo: z
    .string()
    .min(1)
    .describe("GitHub repository name"),
  state: z
    .enum(["open", "closed", "all"])
    .optional()
    .default("open")
    .describe("Filter issues by state: 'open', 'closed', or 'all'. Defaults to 'open'."),
  page: z
    .number()
    .int()
    .positive()
    .optional()
    .default(1)
    .describe("Page number for pagination (starts at 1)"),
  per_page: z
    .number()
    .int()
    .min(1)
    .max(100)
    .optional()
    .default(30)
    .describe("Number of results per page (1-100, default 30)"),
});

// Define the output schema for structured responses
const github_list_issues_outputSchema = z.object({
  issues: z.array(
    z.object({
      number: z.number().describe("Issue number"),
      title: z.string().describe("Issue title"),
      state: z.string().describe("Issue state: 'open' or 'closed'"),
      body: z.string().nullable().describe("Issue description"),
      created_at: z.string().describe("ISO 8601 timestamp when issue was created"),
      updated_at: z.string().describe("ISO 8601 timestamp when issue was last updated"),
      url: z.string().describe("GitHub issue URL"),
      author: z.string().describe("GitHub username of issue author"),
    })
  ),
  total_count: z.number().describe("Total number of issues matching the filter"),
  page: z.number().describe("Current page number"),
  per_page: z.number().describe("Results per page"),
  has_more: z.boolean().describe("Whether more pages are available"),
});

// Register the tool on the server
server.registerTool(
  {
    name: "github_list_issues",
    description:
      "List issues in a GitHub repository with filtering and pagination support. " +
      "Returns issue metadata including title, state, author, and URLs. " +
      "Use this to find, filter, and explore repository issues.",
    inputSchema: github_list_issues_inputSchema,
    outputSchema: github_list_issues_outputSchema,
    annotations: {
      readOnlyHint: true,
      idempotentHint: true,
      openWorldHint: false,
    } as Record<string, boolean>,
  },
  async (input) => {
    const { owner, repo, state, page, per_page } = input;

    try {
      // Call GitHub API with pagination
      const response = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/issues?` +
          `state=${state}&page=${page}&per_page=${per_page}`,
        {
          headers: {
            Authorization: `token ${process.env.GITHUB_TOKEN}`,
            Accept: "application/vnd.github.v3+json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          `GitHub API error: ${response.status} ${response.statusText}`
        );
      }

      const issues = await response.json();
      const totalCount = parseInt(
        response.headers.get("x-total-count") || "0",
        10
      );
      const hasMore = issues.length === per_page && page * per_page < totalCount;

      // Format structured response
      const structuredIssues = issues.map((issue: any) => ({
        number: issue.number,
        title: issue.title,
        state: issue.state,
        body: issue.body,
        created_at: issue.created_at,
        updated_at: issue.updated_at,
        url: issue.html_url,
        author: issue.user.login,
      }));

      // Return both text and structured content
      const textSummary = `Found ${structuredIssues.length} issues on page ${page} ` +
        `(${totalCount} total matching "${state}" state)`;

      return {
        content: [
          {
            type: "text",
            text: textSummary,
          },
          {
            type: "resource",
            resource: {
              uri: `github://repos/${owner}/${repo}/issues`,
              mimeType: "application/json",
              text: JSON.stringify(
                {
                  issues: structuredIssues,
                  total_count: totalCount,
                  page,
                  per_page,
                  has_more: hasMore,
                },
                null,
                2
              ),
            },
          },
        ],
      };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      return {
        content: [
          {
            type: "text",
            text: `Error listing issues: ${errorMessage}. ` +
              `Verify the repository exists, you have access, and your GitHub token is valid.`,
          },
        ],
        isError: true,
      };
    }
  }
);
```

## Key Features

**Input Schema with Zod:**
- `owner` and `repo` are required strings with validation
- `state` has an enum constraint limiting to GitHub's valid states
- `page` and `per_page` are integers with sensible defaults and constraints

**Annotations:**
- `readOnlyHint: true` — this tool only reads data, doesn't modify anything
- `idempotentHint: true` — calling it multiple times with the same parameters returns the same result
- `openWorldHint: false` — results are deterministic, not open-ended

**Output Schema:**
- Defines structured JSON format for the response
- Helps clients understand and process issue data
- Includes metadata like `total_count` and `has_more` for pagination

**Pagination Support:**
- `page` parameter for offset-based pagination
- `per_page` to control result size (capped at 100 per GitHub's API)
- `has_more` flag so clients know when to fetch the next page

**Error Handling:**
- Catches HTTP errors and API failures
- Returns actionable error messages suggesting causes and solutions
