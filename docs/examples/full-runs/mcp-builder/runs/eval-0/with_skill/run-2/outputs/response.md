# MCP Server Technology Recommendations for Stripe API

## Language: TypeScript

Use **TypeScript** for your Stripe MCP server. TypeScript is the recommended language in the MCP development stack because:

- **SDK Support**: The official MCP TypeScript SDK has high-quality support and excellent compatibility across execution environments
- **AI-Friendly**: LLMs generate TypeScript code effectively, benefiting from its broad usage, static typing, and strong linting tooling
- **Type Safety**: Static typing helps catch errors early and makes the codebase more maintainable as it grows

While Python is an option, TypeScript provides superior tooling and SDK support for MCP server development.

## Transport: Streamable HTTP with Stateless JSON

For your **remotely hosted server**, use **Streamable HTTP** as the transport mechanism with **stateless JSON** responses.

**Why streamable HTTP for remote servers:**
- Simpler to scale and maintain compared to stateful sessions
- Stateless JSON avoids complexities of streaming responses
- Better suited for remote deployment where you may have multiple instances

**For local servers** (if you were hosting locally instead), use **stdio** as the transport.

The distinction matters: remote hosting benefits from the statelessness and scalability of HTTP, while local development can leverage stdio's direct process communication.

## Tool Strategy: Prioritize Comprehensive API Coverage

When deciding between workflow tools and raw API endpoint coverage, **prioritize comprehensive API endpoint coverage** over high-level workflow tools (like 'refund-and-notify').

**Why:**
- **Flexibility for Agents**: Comprehensive API coverage gives LLM agents the flexibility to compose operations according to their specific needs
- **Adaptability**: Agents can handle workflows that don't fit your predefined tools
- **When Uncertain**: The MCP design guidance explicitly states—when uncertain between the two approaches, prioritize comprehensive API coverage

Note: Performance varies by client. Some clients with code execution can efficiently combine basic tools to achieve workflows, while others may benefit differently. But the consistent recommendation is comprehensive endpoint coverage as your foundation.

**Approach for Stripe API:**
List and implement endpoints for core operations (create charges, list customers, manage subscriptions, handle refunds, etc.) rather than bundling them into high-level workflow tools. Agents will compose these tools to solve specific problems.

---

## Summary

- **Language**: TypeScript
- **Transport**: Streamable HTTP (stateless JSON) for remote, stdio for local
- **Tool Strategy**: Comprehensive API endpoint coverage over workflow tools
