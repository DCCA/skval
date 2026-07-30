# MCP Server Planning: Stripe API

## Language Recommendation: TypeScript

I recommend **TypeScript** for your Stripe MCP server. Here's why:

- **Type Safety**: The Stripe API has complex nested objects and union types (e.g., different charge statuses, payment method variants). TypeScript's static typing will catch schema mismatches during development rather than at runtime.
- **Mature Ecosystem**: The official MCP SDKs have the most complete implementation and best documentation in TypeScript/JavaScript.
- **Async/Await Pattern**: Stripe API calls are I/O-bound; TypeScript's async/await is clean and intuitive for chaining multiple API calls within tools.
- **Deployment Flexibility**: Node.js runs consistently across Linux/macOS/Windows environments, important for team deployments.

Python is viable but typically requires async frameworks (asyncio + aiohttp) with more boilerplate for the same result.

## Transport Recommendation: Streamable HTTP (Remote) + Stdio (Local)

**For a remotely hosted server shared by your team's agents:**
- Use **HTTP with stateless JSON** (not WebSockets or long-polling).
- Each request/response cycle is independent; there's no need to maintain session state on the server.
- HTTP makes deployment straightforward (any web host, load balancer, or containerized service).
- **JSON framing**: Encode MCP messages as JSON in request/response bodies, matching the MCP spec for HTTP transports.

**Local development alternative:**
- Use **stdio** for local testing (where the MCP server runs as a subprocess of the client). This is simpler for development because it avoids network setup.

The distinction matters: stdio is not suitable for remote, multi-client scenarios because each client needs a separate process. HTTP scales.

## Tool Design: Endpoints vs. Workflows

**Recommendation: Prioritize comprehensive API endpoint coverage.**

Reasons:
1. **Flexibility**: LLM clients don't always know in advance what task they'll need to complete. Broad endpoint coverage lets them compose workflows dynamically.
2. **Reusability**: A single "list charges" tool is reusable across many workflows; a "refund and notify" tool is tied to one use case.
3. **Debugging**: If a composed workflow fails, clients can isolate which tool caused the issue. With high-level workflows, the root cause is hidden inside the tool.
4. **Upstream API Stability**: Stripe's API evolves. Workflow tools mean you maintain two layers of abstraction; endpoint coverage means you track Stripe's API more directly.

Trade-off: This does require clients to make multiple tool calls for complex operations. However, LLM models handle multi-step reasoning well, and the flexibility gain outweighs the extra latency in most cases.

For high-traffic scenarios where performance is critical, clients can cache or batch common workflows locally, so this is not a hard blocker.
