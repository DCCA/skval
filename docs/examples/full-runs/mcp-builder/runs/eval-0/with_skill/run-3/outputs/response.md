# Stripe MCP Server Planning & Recommendations

Based on the recommended stack and best practices for MCP server development, here are my concrete recommendations for your remotely hosted Stripe MCP server:

## Language: TypeScript

**Recommendation: Use TypeScript**

TypeScript is the recommended language for MCP server development because:
- The official MCP TypeScript SDK provides high-quality, well-maintained support
- Excellent static typing and linting tools (like ruff) help catch errors early
- Strong AI model code generation—models produce higher-quality TypeScript code due to broad usage and familiarity
- Good compatibility across many execution environments
- Superior for team collaboration with type safety ensuring fewer runtime issues

While Python is also viable (with FastMCP), TypeScript is the preferred choice for production-quality MCP servers, especially for remote hosting where reliability and maintainability are critical.

## Transport: Streamable HTTP with Stateless JSON

**Recommendation: Use Streamable HTTP for your remote server**

Since you're hosting this remotely for your team's agents:
- **Transport**: Streamable HTTP (not stdio, which is for local servers)
- **State model**: Stateless JSON responses
- **Why**: Streamable HTTP is simpler to scale and maintain compared to stateful sessions and streaming responses. Stateless design allows multiple clients to connect independently without session management overhead, making it ideal for a shared remote server where multiple agents may access it concurrently.

**Note on stdio**: Use stdio transport only for local/embedded servers running on the same machine as the client. Since your server is remote, streamable HTTP is the correct choice.

## Tool Design: Comprehensive API Coverage Over Workflow Tools

**Recommendation: Prioritize comprehensive API endpoint coverage**

When deciding between:
- **Workflow tools**: High-level, specialized tools like `refund-and-notify` that combine multiple operations
- **API endpoint coverage**: Granular tools that map directly to Stripe API endpoints

**Decision**: Prioritize comprehensive API endpoint coverage, especially when uncertain.

**Reasons**:
- Agents have maximum flexibility to compose operations in ways you may not have anticipated
- Different clients and agents have different performance characteristics; some benefit from code execution that composes basic tools, others work better with higher-level workflows
- Comprehensive coverage lets agents solve unexpected problems by combining primitives
- Once deployed, workflow tools are harder to change; comprehensive coverage is more stable

**Caveat**: Performance does vary by client. Some LLM clients with code execution capabilities may perform better with lower-level tools they can combine programmatically, while others benefit from pre-built workflows. However, when uncertain, comprehensive API coverage provides the best foundation and maximum adaptability.

---

## Summary

- **Language**: TypeScript (recommended stack, superior SDK support, better code generation)
- **Transport**: Streamable HTTP with stateless JSON (remote deployment, simpler scaling, no session management)
- **Tool Design**: Comprehensive Stripe API endpoint coverage (flexibility, future-proof, client-agnostic)
