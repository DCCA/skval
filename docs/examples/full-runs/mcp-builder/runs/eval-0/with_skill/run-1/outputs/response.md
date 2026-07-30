# MCP Server Architecture Recommendations for Stripe API

For your remotely hosted Stripe API MCP server, here are my concrete recommendations:

## Language: TypeScript (Recommended)

**Use TypeScript** over Python. While both are viable, TypeScript is the recommended stack for several reasons:

- **SDK Quality**: The official MCP TypeScript SDK has excellent support and is actively maintained
- **AI Generation**: LLMs produce higher-quality TypeScript code due to its broad usage, static typing, and excellent linting tools
- **Execution Environments**: TypeScript is more compatible with many execution environments (e.g., MCPB), which matters for a remote server shared across your team
- **Type Safety**: Strong static typing helps prevent runtime errors in a production server

## Transport: Streamable HTTP with Stateless JSON (for Remote)

**For your remote server, use Streamable HTTP with stateless JSON**, not stateful sessions or streaming responses.

This is the recommended transport for remote servers because:

- **Stateless Architecture**: JSON-based requests/responses are simpler to scale and maintain compared to stateful sessions
- **Easier Deployment**: Stateless design works well with containerized deployments and load balancers
- **Better Observability**: Each request is independent, making debugging and monitoring straightforward

**Note**: If you ever build a local-only server (not your case now), use stdio for local servers. But for remote team hosting, streamable HTTP is correct.

## Tools: Comprehensive API Endpoint Coverage (Not Workflow Tools)

**Prioritize comprehensive API endpoint coverage** rather than high-level workflow tools like "refund-and-notify".

Here's why:

- **Agent Flexibility**: When you expose the raw Stripe API endpoints, LLM agents can compose operations dynamically to solve novel problems—they're not limited to predefined workflows
- **Performance Varies by Client**: Some clients benefit from agents composing basic tools, while others work better with higher-level workflows. When uncertain, comprehensive coverage gives you the most flexibility
- **Maintenance**: Workflow tools require you to anticipate use cases. Comprehensive API coverage adapts to whatever your team needs without server changes

Start by implementing the most frequently used Stripe endpoints (create charge, list transactions, refund, update subscription, etc.), then expand from there. This gives you flexibility while staying focused on high-impact operations.

## Summary

- **Language**: TypeScript (better SDK support, AI-friendly, compatible with more execution environments)
- **Transport**: Streamable HTTP for remote hosting with stateless JSON (simpler, more scalable)
- **Tool Strategy**: Comprehensive Stripe API endpoint coverage (flexibility for agents, adapts to team needs)
