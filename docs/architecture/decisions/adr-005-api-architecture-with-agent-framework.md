# ADR-005: API Architecture with FastAPI and Microsoft Agent Framework

**Status**: Accepted

**Date**: 2025-09-28

**Decision**: Use FastAPI for REST API with Microsoft Agent Framework's built-in workflow orchestration (SequentialBuilder), conversation state management (AgentThread), and event streaming (Workflow.run_stream).

**Context**:
- Need to expose multi-agent loan processing to UI
- Require real-time progress updates during workflow execution
- Must support conversational intake with state management
- Need cloud-native deployment on Azure

**Alternatives Considered**:
1. **Custom Service Bus orchestration** - Rejected: Agent Framework provides SequentialBuilder
2. **Custom session management with Redis** - Accepted partially: Use AgentThread with Redis-backed ChatMessageStore
3. **WebSocket for all communication** - Rejected: Streamable HTTP (MCP-aligned) is simpler
4. **Flask/Django** - Rejected: FastAPI has native async support and Pydantic integration

**Decision**:
- **FastAPI** for REST API layer with async support
- **SequentialBuilder** for workflow orchestration (Intake → Credit → Income → Risk)
- **AgentThread** for conversation state management
- **Workflow.run_stream()** for real-time event streaming
- **Streamable HTTP** transport aligned with MCP specification

**Consequences**:

*Positive*:
- Leverage Agent Framework's built-in capabilities (no custom infrastructure)
- Type-safe workflow construction with Python type hints
- Automatic Pydantic validation for requests/responses
- Built-in observability with WorkflowEvents
- Simplified architecture (fewer moving parts)

*Negative*:
- Learning curve for Agent Framework patterns
- Less flexibility than custom orchestration
- Tight coupling to Microsoft Agent Framework

**Implementation**:
- API layer: `loan_defenders/api/`
- Workflow service: Uses SequentialBuilder
- Chat service: Uses AgentThread with RedisChatMessageStore
- See: `docs/api/api-architecture.md`

**Related ADRs**:
- ADR-001: Multi-agent strategic foundation
- ADR-004: Personality-driven agent architecture
- ADR-006: Sequential Workflow Orchestration
