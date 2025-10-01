# ADR-001: Multi-Agent Strategic Foundation

## Status
Accepted

## Context
During the migration from OpenAI Agent SDK to Microsoft Agent Framework, we evaluated whether to maintain the multi-agent architecture or simplify to a single orchestrator approach. The question was whether multi-agent complexity was justified for the current business requirements.

## Decision
**Maintain the multi-agent strategic foundation** while simplifying implementation to business logic only.

## Rationale

### Strategic Investment
The multi-agent architecture represents a strategic investment in progressive autonomy. While current implementations may be simple, the foundation supports future intelligence growth as:
- MCP servers expand from current 3 to planned 20+
- Agent capabilities become more sophisticated
- Business requirements demand specialized expertise

### Preserved Business Value
Each agent represents distinct domain expertise:
- **Intake Agent**: Data validation and routing logic
- **Credit Agent**: Credit assessment and risk evaluation expertise
- **Income Agent**: Employment and income verification knowledge
- **Risk Agent**: Decision synthesis and policy application
- **Orchestrator Agent**: Workflow coordination patterns

### Framework Independence
By preserving agent personas as markdown files, any agent framework can:
- Load specialized instructions directly
- Understand domain-specific responsibilities
- Access appropriate MCP tool sets
- Maintain business logic separation

## Implementation

### Simplified Approach
Instead of complex orchestration engines, we preserve:
- Agent persona definitions (markdown files)
- MCP server tool configurations
- Business data models with validation
- Service interface abstractions

### Framework Integration
Any agent framework can use this foundation by:
1. Loading agent personas from `agents/agent-persona/*.md`
2. Connecting to MCP servers using `config/mcp_servers.yaml`
3. Using business models from `models/*.py`
4. Implementing framework-specific orchestration

## Consequences

### Positive
- Business logic preserved and framework-agnostic
- Agent expertise clearly defined and reusable
- Progressive enhancement path without refactoring
- Clear upgrade path as capabilities mature
- Regulatory compliance through specialized agents

### Negative
- Requires framework to implement multi-agent coordination
- More complex than single-agent approach initially
- Need to maintain agent persona consistency

## Future Evolution

### Phase 1 (Current): Business Logic Foundation
- Agent personas as instruction files
- MCP servers for tool integration
- Business models with validation
- Framework-agnostic utilities

### Phase 2: Framework Integration
- Microsoft Agent Framework ChatClientAgent implementation
- Agent coordination patterns
- Real-time decision workflows

### Phase 3: Progressive Autonomy
- Agent-to-agent communication
- Dynamic tool selection
- Adaptive workflow patterns
- Machine learning integration

## Related Decisions
- ADR-002: Business Logic First Approach
- ADR-003: Configuration Separation

**Decision Date**: 2024-09-24
**Decision Authors**: Development Team
**Status**: Foundation implemented, framework integration pending