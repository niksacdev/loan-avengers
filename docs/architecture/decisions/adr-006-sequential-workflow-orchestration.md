# ADR-006: Sequential Workflow Orchestration with SequentialBuilder

**Status**: Accepted
**Date**: 2025-09-28

**Decision**: Use Microsoft Agent Framework's SequentialBuilder for orchestrating loan processing agents in sequential workflow.

**Context**:
User asked to review Agent Framework capabilities rather than implementing custom Azure Service Bus orchestration. Agent Framework provides SequentialBuilder for sequential agent workflows with shared conversation context.

**Decision**:
Use SequentialBuilder to wire agents: Intake → Credit → Income → Risk → Decision

```python
workflow = SequentialBuilder().participants([
    intake_agent, credit_agent, income_agent, risk_agent
]).build()
```

**Consequences**:
*Positive*: Built-in orchestration, type-safe, automatic message passing
*Negative*: Sequential only (no parallel processing)

**Related**: ADR-005, ADR-007
