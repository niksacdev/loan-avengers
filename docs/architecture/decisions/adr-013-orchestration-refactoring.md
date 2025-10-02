# ADR-013: Orchestration Pattern Refactoring

**Status**: Accepted
**Date**: 2025-09-30
**Decision Maker(s)**: Development Team
**Tags**: architecture, multi-agent, orchestration, code-quality

## Context

The loan application system initially implemented a single `CoordinatorService` that mixed:
- Conversational AI (natural language interaction)
- Orchestration logic (parsing, validation, routing)
- State management (tracking collected data)
- Business logic (LoanApplication creation)

This violated the **single responsibility principle** and created an antipattern: using an AI agent for deterministic tasks that should be handled by code.

### Research Findings

Pattern research revealed industry best practices:
- **Agent-as-Tool Pattern**: Agents handle only open-ended problems (conversation)
- **Code-Based Orchestration**: Deterministic tasks (parsing, routing) belong in code
- **Sequential Orchestration**: Predefined agent pipelines for structured workflows

### Antipattern Identified

**Over-agentification**: Using ChatAgent for tasks like:
- JSON parsing and validation
- State tracking and management
- Workflow routing decisions
- Business object creation

These are deterministic operations that don't require AI intelligence.

## Decision

### Refactoring Plan

**Split CoordinatorService into two components:**

1. **ConversationAgent** (Pure AI Agent)
   - Pattern: Agent-as-Tool
   - Handles: Natural language conversation only
   - Returns: Raw JSON string (unparsed)
   - Location: `loan_defenders/agents/conversation_agent.py`

2. **ConversationOrchestrator** (Code-Based)
   - Pattern: Code-Based Orchestration
   - Handles: Parsing, validation, state management, business logic
   - Wraps: ConversationAgent
   - Location: `loan_defenders/agents/conversation_orchestrator.py`

**Rename and clarify processing components:**

3. **ProcessingWorkflow → LoanProcessingPipeline**
   - Pattern: Sequential Orchestration
   - Clearer naming for loan-specific processing
   - Location: `loan_defenders/agents/loan_processing_pipeline.py`

**Remove unnecessary abstraction:**

4. **Delete SequentialLoanWorkflow Facade**
   - Was redundant wrapper around orchestrator + pipeline
   - API now uses ConversationOrchestrator and LoanProcessingPipeline directly

### Architecture Flow

```
User Message
    ↓
ConversationOrchestrator.handle_conversation()
    ↓
ConversationAgent.chat() → Raw JSON
    ↓
Parse JSON (code) → Extract fields (code)
    ↓
Validate completeness (code) → Track state (code)
    ↓
If complete: Create LoanApplication (code)
    ↓
LoanProcessingPipeline.process_application()
    ↓
Sequential: Intake → Credit → Income → Risk
    ↓
Final Decision
```

## Consequences

### Positive

✅ **Clear separation of concerns**: Agent handles conversation, code handles logic
✅ **Easier to test**: Deterministic code logic can be unit tested
✅ **Better maintainability**: Changes to business logic don't require agent retraining
✅ **Improved performance**: Code executes faster than LLM for deterministic tasks
✅ **LLM-ready annotations**: Docstrings optimized for agent/LLM consumption
✅ **Clearer naming**: LoanProcessingPipeline vs vague "ProcessingWorkflow"
✅ **Simpler architecture**: Removed unnecessary facade layer

### Neutral

⚪ **More files**: Went from 2 files to 3 (but clearer responsibilities)
⚪ **Pattern names**: Added "Pattern: X" annotations to help LLMs understand architecture

### Negative

⚠️ **Migration effort**: Need to update tests referencing old components
⚠️ **Documentation updates**: Need to update diagrams and architecture docs
⚠️ **Mock updates**: Mock implementations need corresponding refactoring

## Implementation

### Files Created/Modified

**Created:**
- `loan_defenders/agents/conversation_agent.py` - Pure agent wrapper
- `loan_defenders/agents/conversation_orchestrator.py` - Code-based orchestration

**Renamed:**
- `loan_defenders/agents/processing_workflow.py` → `loan_defenders/agents/loan_processing_pipeline.py`

**Modified:**
- `loan_defenders/api/app.py` - Updated to use new components directly
- All imports updated to use `ConversationOrchestrator` and `LoanProcessingPipeline`

**Deleted:**
- `loan_defenders/agents/sequential_workflow.py` - Redundant facade removed
- `loan_defenders/agents/coordinator_service.py` - Replaced by Agent + Orchestrator split

### API Changes

**Before:**
```python
sequential_workflow = SequentialLoanWorkflow()
await sequential_workflow.process_conversation(...)
```

**After:**
```python
conversation_orchestrator = ConversationOrchestrator()
processing_pipeline = LoanProcessingPipeline()

# Conversation phase
async for response in conversation_orchestrator.handle_conversation(...):
    if response.action == "ready_for_processing":
        application = conversation_orchestrator.create_loan_application(...)
        # Processing phase
        async for update in processing_pipeline.process_application(application):
            ...
```

### Docstring Enhancements

All components now include:
- **Pattern annotations**: `Pattern: Code-Based Orchestration`
- **Clear scope markers**: ✅ (handles) vs ❌ (does not handle)
- **Flow diagrams**: Step-by-step execution flow
- **Type annotations**: Full typing for LLM/agent understanding
- **Concise descriptions**: Removed verbose best practices references

## Testing Strategy

1. **Unit tests** for ConversationOrchestrator (parsing, validation, creation)
2. **Integration tests** for full conversation → processing flow
3. **Mock updates** for environments without agent framework
4. **End-to-end tests** with sample loan applications

## Alternatives Considered

### Alternative 1: Keep Single CoordinatorService
**Rejected**: Violates single responsibility, mixes AI and code logic

### Alternative 2: More Agent Layers
**Rejected**: Over-agentification - deterministic tasks don't need AI

### Alternative 3: Keep Facade Pattern
**Rejected**: Unnecessary abstraction, API can directly use orchestrator + pipeline

## References

- Orchestrator-Worker Pattern (multi-agent systems)
- Agent-as-Tool Pattern (OpenAI)
- Code-Based Orchestration (deterministic tasks)
- Sequential Orchestration (predefined pipelines)

## Related ADRs

- ADR-001: Agent architecture foundations
- ADR-002: Conversation state management
- ADR-004: Multi-agent workflow design

## Notes

This refactoring addresses the antipattern of "over-agentification" by establishing clear boundaries:
- **Use agents** for open-ended problems (conversation, context, ambiguity)
- **Use code** for deterministic tasks (parsing, validation, routing, business logic)

The result is a more maintainable, testable, and performant system that correctly applies AI where it adds value.
