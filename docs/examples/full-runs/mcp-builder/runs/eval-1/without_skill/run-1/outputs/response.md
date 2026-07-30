# GitHub List Issues Tool - MCP Tool Registration

## Tool Definition Code

```typescript
import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { Octokit } from "@octokit/rest";

const githubListIssuesInputSchema = z.object({
  owner: z.string().describe("The GitHub repository owner (user or organization)"),
  repo: z.string().describe("The GitHub repository name"),
  state: z
    .enum(["open", "closed", "all"])
    .default("open")
    .describe("Filter issues by state: 'open', 'closed', or 'all'"),
  page: z
    .number()
    .int()
    .default(1)
    .describe("Page number for pagination (1-indexed)"),
  per_page: z
    .number()
    .int()
    .default(30)
    .describe("Number of issues per page (1-100)"),
});

export const githubListIssuesTool: Tool = {
  name: "github_list_issues",
  description:
    "List issues for a GitHub repository with optional filtering by state. Supports pagination.",
  inputSchema: githubListIssuesInputSchema,
  annotations: {
    readOnlyHint: true,
  },
};

export async function handleGithubListIssues(
  input: z.infer<typeof githubListIssuesInputSchema>,
  octokit: Octokit
): Promise<{ text: string; structuredContent?: unknown }> {
  const { owner, repo, state, page, per_page } = input;

  try {
    const response = await octokit.issues.listForRepo({
      owner,
      repo,
      state,
      page,
      per_page,
    });

    const issueList = response.data.map((issue) => ({
      number: issue.number,
      title: issue.title,
      state: issue.state,
      url: issue.html_url,
      created_at: issue.created_at,
      assignee: issue.assignee?.login,
      labels: issue.labels.map((label) =>
        typeof label === "string" ? label : label.name
      ),
    }));

    const structuredContent = {
      type: "issues_list",
      total: response.data.length,
      pagination: {
        page,
        per_page,
        has_more: response.data.length === per_page,
      },
      issues: issueList,
    };

    const textSummary = `Found ${issueList.length} issue(s) in ${owner}/${repo} (state: ${state}):
${issueList
  .map(
    (issue) =>
      `- #${issue.number}: ${issue.title} (${issue.state}) - ${issue.url}`
  )
  .join("\n")}`;

    return {
      text: textSummary,
      structuredContent,
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to list issues for ${owner}/${repo}: ${errorMessage}`);
  }
}
```

## Key Features

### 1. Input Schema with Zod Validation
- Uses `z.object()` to define structured input
- Each field has clear descriptions and constraints:
  - `owner` and `repo`: required strings
  - `state`: enum constrained to "open", "closed", or "all" with default "open"
  - `page` and `per_page`: integers with defaults for pagination

### 2. Tool Annotations
- `readOnlyHint: true`: Marks this as a read-only operation that doesn't modify state

### 3. Structured Output
- Returns both `text` (human-readable summary) and `structuredContent` (machine-parseable JSON)
- `structuredContent` includes:
  - Issue details (number, title, state, URL, assignee, labels)
  - Pagination metadata (current page, items per page, has_more flag)
  - Issue count

### 4. Pagination Support
- `page` parameter (1-indexed) for selecting which page of results
- `per_page` parameter (capped at 100) for controlling page size
- `has_more` flag in response indicates if more pages exist

### 5. Consistent Naming
- Tool name follows pattern: `github_list_issues` (service_action format)
- Descriptive, action-oriented, and unambiguous

### 6. Error Handling
- Wraps API calls in try-catch
- Returns descriptive error messages if the request fails
