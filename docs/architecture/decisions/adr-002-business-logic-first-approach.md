# ADR-002: Business Logic First Approach

## Status
Accepted

## Context
The original repository contained complex orchestration engines, provider abstractions, and framework-specific implementations totaling 6,680+ lines. This complexity made framework migration difficult and obscured the core business value. We needed to decide between maintaining complex abstractions or simplifying to business essentials.

## Decision
**Implement a "Business Logic First" approach** that strips away framework complexity and preserves only essential business components.

## Rationale

### Framework Lock-in Problem
The original approach created tight coupling between business logic and OpenAI Agent SDK:
- Provider abstraction layers obscured simple operations
- Orchestration engines encoded workflow logic in code
- Complex agent creation patterns made framework switching difficult

### Business Value Clarity
The valuable components were being obscured by framework complexity:
- **Data Models**: Comprehensive loan processing models with validation
- **Business Rules**: Domain expertise in credit, income, and risk assessment
- **Tool Integration**: MCP servers for external data access
- **Agent Expertise**: Specialized instruction sets for loan processing

### Framework Agnostic Design
By focusing on business logic, we enable any framework integration:
- Microsoft Agent Framework can load personas directly
- OpenAI Assistants can use the same instruction files
- LangChain can integrate with business models seamlessly
- Custom implementations can access clean business APIs

## Implementation

### What We Kept (Essential Business Logic)
```
loan_processing/
├── models/                  # Business data models with validation
├── agents/agent-persona/    # Domain expertise as instruction files
├── tools/mcp_servers/      # External tool integration
├── tools/services/         # Business service interfaces
├── config/                 # Simple configuration files
└── utils/                  # Framework-agnostic utilities
```

### What We Removed (Framework Complexity)
- Orchestration engines and pattern execution (1,000+ lines)
- Provider abstraction layers and agent factories
- Complex configuration systems with validation
- Framework-specific agent creation code
- Observability infrastructure and correlation tracking

### Configuration Simplification
**Before**: Complex multi-provider configuration with validation
```yaml
providers:
  openai:
    provider_class: "loan_processing.providers.openai.provider.OpenAIAgentProvider"
    # ... 50+ lines of configuration
```

**After**: Simple agent-to-tool mappings
```yaml
agent_personas:
  credit:
    file: "credit-agent-persona.md"
    mcp_servers: ["application_verification", "financial_calculations"]
```

## Benefits

### Immediate Benefits
1. **Framework Independence**: Can integrate with any agent system
2. **Clarity**: Business logic is immediately visible and understandable
3. **Maintainability**: Changes focus on business rules, not framework plumbing
4. **Testing**: Business logic can be tested independently
5. **Documentation**: Agent personas are self-documenting

### Long-term Benefits
1. **Future-Proof**: Will work with frameworks that don't exist yet
2. **Specialization**: Teams can focus on business expertise vs framework details
3. **Compliance**: Business rules are explicit and auditable
4. **Evolution**: Framework changes don't require business logic rewrites

## Migration Strategy

### Phase 1: Simplification ✅
- Remove complex orchestration and provider abstractions
- Preserve all business models and validation
- Convert agent definitions to persona files
- Simplify configuration to essential mappings

### Phase 2: Framework Integration (Next)
- Implement Microsoft Agent Framework integration
- Load personas into ChatClientAgent instances
- Connect MCP servers as framework tools
- Implement framework-specific orchestration

### Phase 3: Enhancement (Future)
- Add advanced capabilities using framework strengths
- Implement sophisticated workflows
- Integrate machine learning components

## Validation

### Business Logic Preservation Test
All core business capabilities remain functional:
```python
from loan_processing.models import LoanApplication
from loan_processing.agents import get_persona_path

# Business models work immediately
app = LoanApplication(...)
print(f"DTI: {app.debt_to_income_ratio}")

# Agent personas load cleanly
credit_instructions = get_persona_path("credit")
```

### Framework Integration Test
Any framework can use the foundation:
```python
# Microsoft Agent Framework
agent = ChatClientAgent(instructions=load_persona("credit"))

# OpenAI Assistants
assistant = openai.beta.assistants.create(instructions=load_persona("credit"))

# LangChain
agent = ConversationalAgent(system_message=load_persona("credit"))
```

## Consequences

### Positive
- ✅ **Clean Foundation**: 27 Python files vs 49+ before
- ✅ **Framework Agnostic**: Works with any agent system
- ✅ **Business Focused**: All complexity serves business needs
- ✅ **Easy Integration**: Simple APIs and clear documentation
- ✅ **Maintainable**: Changes are business-driven, not framework-driven

### Negative
- ❌ **Framework Work Required**: Need to implement orchestration in chosen framework
- ❌ **Initial Setup**: Requires more framework-specific code initially
- ❌ **Documentation Gap**: Need to create framework integration guides

### Risk Mitigation
- **Framework Choice**: Can switch frameworks without losing business logic
- **Integration Complexity**: Business logic simplicity compensates for framework work
- **Learning Curve**: Clear separation makes both business and framework concerns easier to understand

## Related Decisions
- ADR-001: Multi-Agent Strategic Foundation
- ADR-003: Configuration Separation

**Decision Date**: 2024-09-24
**Decision Authors**: Development Team
**Impact**: Repository restructured, 75% reduction in complexity while preserving 100% of business value