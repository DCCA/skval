# MCP Server Architecture for Stripe API

## Language Choice: TypeScript

I recommend **TypeScript** for your remote Stripe MCP server. Here's why:

- **Type safety**: TypeScript catches schema mismatches at compile time, which is critical when mapping Stripe's API to MCP tool definitions. This prevents runtime errors when your agents make calls.
- **MCP SDK quality**: The official MCP TypeScript SDK is well-documented and actively maintained, with excellent support for defining tools, inputs, outputs, and annotations.
- **Ecosystem**: Most production MCP implementations and integrations are built in TypeScript, giving you access to better tooling, examples, and community support.
- **JSON compatibility**: TypeScript/Node.js has first-class JSON handling, which is essential for the stateless request/response model you'll use.

Python is also viable, but TypeScript is the recommended choice for most production deployments.

## Transport: Streamable HTTP with Stateless JSON

For a remotely hosted server serving your team's agents, I recommend **streamable HTTP with stateless JSON**:

- **Stateless JSON**: Each request contains all necessary context (authentication, parameters), and each response is a complete JSON document. No session state is maintained on the server.
- **Why HTTP over stdio**: stdio works only for local, single-machine scenarios. Since your server is remote and serves multiple agents, HTTP allows each agent to make independent network requests to a shared endpoint.
- **Streaming for efficiency**: Use HTTP streaming to support long-running operations (e.g., fetching hundreds of transactions from Stripe) without timing out the client or loading everything into memory at once.
- **Scalability**: HTTP endpoints can be load-balanced and scaled horizontally, crucial for team deployments.

For comparison: stdio is appropriate only for local development or single-client scenarios where the server and client run on the same machine.

## Tool Structure: Comprehensive API Endpoint Coverage

When deciding between high-level workflow tools (like "refund-and-notify") and covering the raw API endpoints, I recommend **prioritizing comprehensive API endpoint coverage**, especially when uncertain:

**Reasons**:
- **Flexibility**: Agents can compose lower-level endpoints into custom workflows. You can't do the reverse—high-level tools are inflexible once built.
- **Discoverability**: Agents (and users) can understand what's available by inspecting your tool list. Workflow tools hide the underlying API shape.
- **Maintenance**: Stripe's API evolves. Exposing endpoints directly means you're just wrapping the API; custom workflows require ongoing updates as Stripe adds features.
- **Performance varies by client**: Some agents may prefer high-level workflows; others need fine-grained control. Endpoints let each choose.

You can still provide a few high-level workflows as convenience tools once your endpoint coverage is comprehensive, but start with raw API endpoints.
