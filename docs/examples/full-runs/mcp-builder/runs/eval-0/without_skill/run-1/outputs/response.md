# MCP Server Architecture for Stripe API

## Language Recommendation: TypeScript

For your remotely hosted Stripe MCP server, **TypeScript is the recommended choice**. Here's why:

- **Type Safety**: Stripe's API is complex with many object types and optional fields. TypeScript's static typing catches schema mismatches at compile time, preventing runtime errors when tools interface with the API.
- **Ecosystem**: The MCP TypeScript SDK has mature support for tool definitions, streaming, and error handling. Libraries like `stripe-sdk` offer complete TypeScript support with full type definitions.
- **LLM Integration**: Most modern LLM frameworks (including the Python MCP implementations) expect well-typed tool schemas and structured outputs, which TypeScript enforces naturally.
- **Maintainability**: Team adoption is higher for TypeScript than Python in API integration contexts.

Python is acceptable but requires more careful schema validation and error handling boilerplate.

## Transport Choice: HTTP (Remote) vs. stdio (Local)

**For a remote, team-hosted server: Use HTTP with stateless JSON.**

Why this matters:
- **Remote deployment** requires HTTP as the transport layer—it's the only option for servers running on a remote host that multiple agents access over a network.
- **Stateless JSON** means each request carries all needed context; the server maintains no session state. This ensures:
  - Horizontal scalability (you can run multiple instances behind a load balancer)
  - Stateless request processing—no side effects on the server
  - Clear client-server contract via request/response bodies

**For local development**: Use stdio (standard input/output). The server and client run in the same process or on the same machine, making stdio efficient and simple.

The key distinction: **Remote = HTTP with stateless JSON; Local = stdio.**

## Tool Design: Comprehensive Endpoint Coverage vs. Workflow Tools

**Recommendation: Prioritize comprehensive API endpoint coverage over high-level workflow tools.**

Rationale:
- **Composability**: Low-level tools (e.g., `stripe_create_refund`, `stripe_list_customers`, `stripe_retrieve_invoice`) can be composed by agents into higher-level workflows. A workflow tool like `refund_and_notify` bakes in business logic that may not fit every use case.
- **Flexibility**: When uncertain what workflows your team needs, exposing raw endpoints gives them maximum flexibility. Teams can define their own workflows as needed.
- **Maintenance**: Workflow tools require ongoing updates as business logic evolves. Raw endpoint tools are stable as long as the Stripe API is stable.
- **Discoverability**: Agents can inspect endpoint tools and understand which operations are available; they can discover and compose workflows dynamically.

**Performance note**: If you find that agents frequently compose the same multi-step operations, you can add workflow tools later as optimizations. Start with endpoints.

## Summary

- **Language**: TypeScript (for type safety and ecosystem support)
- **Transport**: HTTP + stateless JSON for remote hosting
- **Tools**: Comprehensive Stripe API endpoint coverage, starting broad and adding domain-specific workflows only when patterns emerge
