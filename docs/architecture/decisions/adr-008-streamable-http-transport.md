# ADR-008: Streamable HTTP Transport (MCP-Aligned)

**Status**: Accepted
**Date**: 2025-09-28

**Decision**: Use Streamable HTTP transport for real-time workflow events, aligned with Model Context Protocol (MCP) specification.

**Context**:
MCP servers use Streamable HTTP transport (single POST endpoint with optional SSE streaming). Align API with same pattern for consistency.

**Decision**:
- Single POST endpoint: `/api/v1/applications/{id}/stream`
- Accept: text/event-stream for SSE streaming
- Accept: application/json for single responses
- JSON-RPC 2.0 event format

**Consequences**:
*Positive*: Consistent with MCP pattern, simpler than WebSocket, auto-reconnect
*Negative*: One-way communication (use separate chat endpoint for bidirectional)

**Related**: ADR-005
