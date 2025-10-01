# ADR-007: Conversation State Management with AgentThread

**Status**: Accepted
**Date**: 2025-09-28

**Decision**: Use Agent Framework's AgentThread with Redis-backed ChatMessageStore for conversation state.

**Context**:
Need to manage conversation history for conversational intake. Agent Framework provides AgentThread with ChatMessageStore protocol for state management.

**Decision**:
- AgentThread for conversation state per application
- RedisChatMessageStore implements ChatMessageStore protocol
- 30-minute TTL for session state

**Consequences**:
*Positive*: Built-in state management, automatic serialization, type-safe
*Negative*: Requires Redis for persistence

**Related**: ADR-005, ADR-008
