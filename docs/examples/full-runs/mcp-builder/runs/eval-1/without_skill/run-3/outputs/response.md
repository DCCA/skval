```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
  TextContent,
  StructuredContent,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { Octokit } from "@octokit/rest";

// Initialize GitHub client (assumes GITHUB_TOKEN is set)
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

// Define the input schema for listing issues
const GitHubListIssuesInputSchema = z.object({
  owner: z.string().describe("The repository owner (user or organization)"),
  repo: z.string().describe("The repository name"),
  state: z
    .enum(["open", "closed", "all"])
    .optional()
    .describe("Filter by issue state (default: open)"),
  per_page: z
    .number()
    .int()
    .min(1)
    .max(100)
    .optional()
    .describe("Number of issues per page (default: 30, max: 100)"),
  page: z
    .number()
    .int()
    .min(1)
    .optional()
    .describe("Page number for pagination (default: 1)"),
});

type GitHubListIssuesInput = z.infer<typeof GitHubListIssuesInputSchema>;

// Define the output schema
const GitHubListIssuesOutputSchema = z.object({
  issues: z.array(
    z.object({
      id: z.number(),
      number: z.number(),
      title: z.string(),
      state: z.string(),
      url: z.string(),
      created_at: z.string(),
      updated_at: z.string(),
    })
  ),
  total_count: z.number(),
  page: z.number(),
  per_page: z.number(),
});

// Tool definition
const github_list_issues_tool: Tool = {
  name: "github_list_issues",
  description:
    "List issues for a GitHub repository with support for filtering by state and pagination",
  inputSchema: {
    type: "object" as const,
    properties: {
      owner: {
        type: "string",
        description: "The repository owner (user or organization)",
      },
      repo: {
        type: "string",
        description: "The repository name",
      },
      state: {
        type: "string",
        enum: ["open", "closed", "all"],
        description: "Filter by issue state (default: open)",
      },
      per_page: {
        type: "number",
        description: "Number of issues per page (default: 30, max: 100)",
      },
      page: {
        type: "number",
        description: "Page number for pagination (default: 1)",
      },
    },
    required: ["owner", "repo"],
  },
  annotations: {
    readOnlyHint: true,
  },
};

// Tool handler
async function handleGitHubListIssues(
  input: GitHubListIssuesInput
): Promise<TextContent & StructuredContent> {
  const { owner, repo, state = "open", per_page = 30, page = 1 } = input;

  try {
    const response = await octokit.issues.listForRepo({
      owner,
      repo,
      state,
      per_page: Math.min(per_page, 100),
      page,
    });

    const issues = response.data.map((issue) => ({
      id: issue.id,
      number: issue.number,
      title: issue.title,
      state: issue.state,
      url: issue.html_url,
      created_at: issue.created_at,
      updated_at: issue.updated_at,
    }));

    const structuredOutput = {
      issues,
      total_count: response.headers["x-total-count"]
        ? parseInt(response.headers["x-total-count"] as string, 10)
        : issues.length,
      page,
      per_page,
    };

    return {
      type: "text",
      text: `Found ${issues.length} issues in ${owner}/${repo} (page ${page}). Total: ${structuredOutput.total_count}`,
      structuredContent: {
        type: "object" as const,
        schema: GitHubListIssuesOutputSchema,
        data: structuredOutput,
      },
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    return {
      type: "text",
      text: `Error fetching issues from ${owner}/${repo}: ${errorMessage}`,
    };
  }
}

// MCP Server setup
const server = new Server({
  name: "github-mcp-server",
  version: "1.0.0",
});

// Register tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [github_list_issues_tool],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "github_list_issues") {
    const input = GitHubListIssuesInputSchema.parse(request.params.arguments);
    const result = await handleGitHubListIssues(input);
    return {
      content: [result],
    };
  }
  throw new Error(`Unknown tool: ${request.params.name}`);
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Key Features:

1. **Zod Input Schema**: The `GitHubListIssuesInputSchema` defines all parameters with type constraints and descriptions. Required fields are `owner` and `repo`; optional fields include `state`, `per_page`, and `page`.

2. **Annotations**: The tool includes `readOnlyHint: true` to signal that this operation does not modify data.

3. **Output Schema**: Defines a structured output with `GitHubListIssuesOutputSchema`, including issue details and pagination metadata.

4. **Structured Response**: The handler returns both text and `structuredContent` for compatibility with clients that parse structured data or plain text.

5. **Pagination Support**: Implements `page` and `per_page` parameters allowing clients to fetch large issue lists incrementally.

6. **Tool Naming**: Follows the convention `service_action` (e.g., `github_list_issues`).
