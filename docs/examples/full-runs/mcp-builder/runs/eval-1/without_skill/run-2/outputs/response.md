# GitHub List Issues Tool Registration

Here's the TypeScript code to register a tool that lists GitHub issues:

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, Tool } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

const server = new Server({
  name: "github-server",
  version: "1.0.0",
});

// Define input schema for github_list_issues
const listIssuesInputSchema = z.object({
  owner: z.string().describe("Repository owner (username or organization)"),
  repo: z.string().describe("Repository name"),
  state: z
    .enum(["open", "closed", "all"])
    .optional()
    .default("open")
    .describe("Filter by issue state: open, closed, or all"),
  page: z
    .number()
    .int()
    .positive()
    .optional()
    .default(1)
    .describe("Page number for pagination (1-indexed)"),
  per_page: z
    .number()
    .int()
    .min(1)
    .max(100)
    .optional()
    .default(30)
    .describe("Number of issues per page (1-100)"),
});

type ListIssuesInput = z.infer<typeof listIssuesInputSchema>;

// Register the tool
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "github_list_issues") {
    const params = listIssuesInputSchema.parse(request.params.arguments);
    return handleListIssues(params);
  }
  throw new Error(`Unknown tool: ${request.params.name}`);
});

// Define the tool
const listIssuesTool: Tool = {
  name: "github_list_issues",
  description:
    "List issues in a GitHub repository. Supports filtering by state and pagination.",
  inputSchema: {
    type: "object" as const,
    properties: {
      owner: {
        type: "string",
        description: "Repository owner (username or organization)",
      },
      repo: {
        type: "string",
        description: "Repository name",
      },
      state: {
        type: "string",
        enum: ["open", "closed", "all"],
        description: "Filter by issue state",
      },
      page: {
        type: "number",
        description: "Page number for pagination",
      },
      per_page: {
        type: "number",
        description: "Number of issues per page",
      },
    },
    required: ["owner", "repo"],
  },
  annotations: {
    readOnlyHint: true,
  },
};

// Tool implementation
async function handleListIssues(params: ListIssuesInput) {
  const { owner, repo, state, page, per_page } = params;

  // Example: Construct GitHub API URL
  const url = new URL(`https://api.github.com/repos/${owner}/${repo}/issues`);
  url.searchParams.set("state", state);
  url.searchParams.set("page", String(page));
  url.searchParams.set("per_page", String(per_page));

  try {
    const response = await fetch(url.toString(), {
      headers: {
        Accept: "application/vnd.github.v3+json",
        Authorization: `token ${process.env.GITHUB_TOKEN}`,
      },
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    const issues = await response.json();

    return {
      content: [
        {
          type: "text",
          text: `Found ${issues.length} issues in ${owner}/${repo}`,
        },
        {
          type: "text",
          text: JSON.stringify(issues, null, 2),
        },
      ],
      isError: false,
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error fetching issues: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
}

// Initialize the server
async function start() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("GitHub MCP server running on stdio");
}

start().catch(console.error);
```

## Key Features:

1. **Input Schema with Zod**: Defines typed, constrained fields:
   - `owner` and `repo` are required strings
   - `state` is an enum constrained to "open", "closed", or "all"
   - `page` and `per_page` provide pagination with sensible defaults and bounds

2. **Tool Annotations**: Declares `readOnlyHint: true` since listing issues is a read-only operation

3. **Structured Response**: Returns both text content and structured JSON representation of the issues

4. **Pagination Support**: Includes `page` and `per_page` parameters to handle large result sets

5. **Tool Naming**: Uses `github_list_issues` following the service_action naming convention

6. **Error Handling**: Properly catches and reports API errors
