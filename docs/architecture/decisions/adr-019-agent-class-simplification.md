# ADR-019: Agent Class Simplification with SequentialBuilder Pattern

**Status**: Accepted
**Date**: 2025-10-02
**Deciders**: Development Team
**Context**: Agent Framework Integration
**Tags**: architecture, agents, microsoft-agent-framework, code-quality

## Context

After adopting Microsoft Agent Framework's SequentialBuilder pattern (ADR-006), our agent classes contained significant technical debt:

### Initial Implementation Problems
1. **Dual Execution Paths**: Agent classes supported both standalone execution (`process_application()`) and SequentialBuilder integration (`create_agent()`)
2. **Manual MCP Lifecycle Management**: Agents manually called `__aenter__()` to initialize MCP tools
3. **Bloated Classes**: 280-330 lines per agent with unused code paths
4. **Configuration Confusion**: Hardcoded MCP server ports in logs alongside environment variables
5. **Missing Validation**: No checks for required environment variables

### Technical Debt Impact
- **Maintenance Burden**: Two code paths to maintain for same functionality
- **Framework Misalignment**: Not following Microsoft Agent Framework best practices
- **Developer Confusion**: Unclear which execution path to use
- **Testing Complexity**: Need to test both standalone and orchestrated modes

## Problem Analysis

### Issue 1: Dual Execution Paths
**Root Cause**: Originally built agents before adopting SequentialBuilder, kept old code "just in case"

**Evidence**:
```python
class IntakeAgent:
    async def process_application(self, application: dict):
        # 170+ lines of standalone logic - UNUSED
        ...

    def create_agent(self) -> ChatAgent:
        # Used by SequentialBuilder - ACTIVE
        ...
```

**Impact**: 60% of code in each agent class was dead code

### Issue 2: Manual MCP Tool Lifecycle
**Root Cause**: Before framework integration, manually managed tool connections

**Evidence**:
```python
# Manual lifecycle (incorrect)
await self.mcp_tool.__aenter__()
result = await agent.run(...)
await self.mcp_tool.__aexit__(...)

# Framework handles this automatically
workflow = SequentialBuilder().participants([...]).build()
```

**Impact**: Fragile connection management, potential resource leaks

### Issue 3: Missing Environment Validation
**Root Cause**: Configuration was assumed to exist

**Evidence**:
```python
# Before: No validation
mcp_url = os.getenv("MCP_URL")
self.mcp_tool = MCPStreamableHTTPTool(endpoint_url=mcp_url)  # Fails silently if None
```

**Impact**: Cryptic runtime errors when environment variables missing

## Decision

### Refactoring Strategy: Single Execution Path Only

Remove all standalone execution code and keep only SequentialBuilder integration:

**Before** (280-330 lines per agent):
```python
class Agent:
    def __init__(...):
        # MCP setup without validation

    async def process_application(self, application):
        # 170 lines of standalone orchestration
        async with self.mcp_tool:
            result = await agent.run(...)
            # Manual response parsing
            # State management
            # Error handling
        return result

    def create_agent(self) -> ChatAgent:
        # SequentialBuilder integration
        return self.chat_client.create_agent(...)
```

**After** (110-150 lines per agent):
```python
class Agent:
    def __init__(self, chat_client=None, temperature=X, max_tokens=Y):
        """Initialize with optional client and create MCP tools."""
        self.chat_client = chat_client or AzureAIAgentClient(
            async_credential=DefaultAzureCredential()
        )

        # Load persona
        self.instructions = PersonaLoader.load_persona("agent_name")

        # Validate and create MCP tools
        mcp_url = os.getenv("MCP_URL")
        if not mcp_url:
            raise ValueError(
                "MCP_URL environment variable not set. "
                "Please configure in .env file."
            )
        self.mcp_tool = MCPStreamableHTTPTool(endpoint_url=mcp_url)

        # Model configuration
        self.temperature = temperature
        self.max_tokens = max_tokens

    def create_agent(self) -> ChatAgent:
        """Create ChatAgent for SequentialBuilder."""
        return self.chat_client.create_agent(
            name="Agent_Name",
            instructions=self.instructions,
            model_config={
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            },
            response_format=AssessmentType,
            tools=self.mcp_tool  # Framework manages lifecycle
        )
```

### Key Changes

#### 1. Removed Code (Per Agent)
- ❌ `process_application()` method (~170 lines)
- ❌ Manual `__aenter__()` / `__aexit__()` calls
- ❌ Unused imports: `AgentRunResponse`, `AgentThread`, `AgentResponse`, `UsageStats`
- ❌ Hardcoded MCP server ports in log messages

#### 2. Added Features
- ✅ Environment variable validation with clear error messages
- ✅ Type-safe MCP URL handling
- ✅ Comprehensive docstrings for each component
- ✅ Clean initialization pattern

#### 3. Code Reduction Metrics
| Agent Class | Before | After | Reduction |
|-------------|--------|-------|-----------|
| IntakeAgent | 281 lines | 110 lines | 61% |
| CreditAgent | 310 lines | 125 lines | 60% |
| IncomeAgent | 329 lines | 138 lines | 58% |
| RiskAgent   | 329 lines | 138 lines | 58% |
| **Average** | **312 lines** | **128 lines** | **59%** |

### SequentialPipeline Integration

The orchestrator now follows this clean pattern:

```python
class SequentialPipeline:
    def __init__(self, chat_client=None):
        self.chat_client = chat_client or AzureAIAgentClient(...)

        # Create agent instances (construct, don't execute)
        self.intake_agent = IntakeAgent(chat_client=self.chat_client)
        self.credit_agent = CreditAgent(chat_client=self.chat_client)
        self.income_agent = IncomeAgent(chat_client=self.chat_client)
        self.risk_agent = RiskAgent(chat_client=self.chat_client)

    async def process_application(self, application):
        # Get ChatAgent instances
        intake_chat = self.intake_agent.create_agent()
        credit_chat = self.credit_agent.create_agent()
        income_chat = self.income_agent.create_agent()
        risk_chat = self.risk_agent.create_agent()

        # Build and run workflow (framework handles everything)
        workflow = SequentialBuilder().participants([
            intake_chat, credit_chat, income_chat, risk_chat
        ]).build()

        # Stream events - framework provides real-time updates
        async for event in workflow.run_stream(application_input):
            # Convert WorkflowEvent to ProcessingUpdate for UI
            yield ProcessingUpdate(...)
```

## Rationale

### Why Remove Standalone Execution?
1. **Single Source of Truth**: SequentialBuilder is the production code path
2. **Framework Alignment**: Follow Microsoft Agent Framework best practices
3. **Reduced Complexity**: Less code = fewer bugs = easier maintenance
4. **Framework Benefits**: Automatic tool lifecycle, event streaming, error handling

### Why Environment Variable Validation?
1. **Fail Fast**: Detect configuration issues at startup, not during processing
2. **Clear Errors**: Developers immediately know what's missing
3. **Type Safety**: Prevents `None` from propagating to framework calls
4. **Production Safety**: Ensures all services start with valid configuration

### Architecture Pattern Benefits
- **Clean Separation**: Agents manage construction, SequentialBuilder manages orchestration
- **Framework-Managed Lifecycle**: No manual tool connection management
- **Real-Time Events**: `workflow.run_stream()` provides progress updates
- **Testability**: Simpler classes are easier to mock and test

## Consequences

### Positive ✅

1. **60% Code Reduction**: From 280-330 lines to 110-150 lines per agent
2. **Single Execution Path**: Only SequentialBuilder, eliminates confusion
3. **Framework-Managed Lifecycle**: No manual MCP connection management
4. **Better Error Messages**: Clear indication when configuration missing
5. **Type Safety**: All Pylance diagnostics resolved
6. **Easier Testing**: Simpler classes with fewer dependencies
7. **Framework Alignment**: Following official Microsoft Agent Framework patterns

### Negative ⚠️

1. **Breaking Changes**: Old standalone execution code removed
2. **Environment Dependencies**: Must configure all MCP URLs or agents fail
3. **Migration Effort**: Existing tests needed updates

### Neutral ℹ️

1. **File Count Same**: Still 4 agent files, just simpler
2. **API Unchanged**: `SequentialPipeline.process_application()` signature identical
3. **MCP Servers**: Still require 3 environment variables per deployment

## Implementation

### Files Modified

**Agent Classes** (All refactored):
1. `loan_avengers/agents/intake_agent.py` (281 → 110 lines)
2. `loan_avengers/agents/credit_agent.py` (310 → 125 lines)
3. `loan_avengers/agents/income_agent.py` (329 → 138 lines)
4. `loan_avengers/agents/risk_agent.py` (329 → 138 lines)

**Orchestrator** (Updated):
5. `loan_avengers/orchestrators/sequential_pipeline.py` - Updated to use `workflow.run_stream()`

**Tests** (Created):
6. `tests/__init__.py` (new)
7. `tests/unit/__init__.py` (new)
8. `tests/unit/agents/__init__.py` (new)
9. `tests/integration/__init__.py` (new)
10. `tests/unit/agents/test_agent_instantiation.py` (new, 271 lines, 13 tests)

### Test Coverage

Created comprehensive unit tests:

**IntakeAgent Tests** (4 tests):
- ✅ Initialization with client
- ✅ Initialization without client (creates default)
- ✅ `create_agent()` returns ChatAgent
- ✅ Custom temperature/max_tokens parameters

**CreditAgent Tests** (2 tests):
- ✅ Initialization with MCP tools (application_verification + financial_calculations)
- ✅ `create_agent()` returns ChatAgent with 2 tools

**IncomeAgent Tests** (2 tests):
- ✅ Initialization with MCP tools (application_verification + document_processing + financial_calculations)
- ✅ `create_agent()` returns ChatAgent with 3 tools

**RiskAgent Tests** (2 tests):
- ✅ Initialization with MCP tools (application_verification + document_processing + financial_calculations)
- ✅ `create_agent()` returns ChatAgent with 3 tools

**Integration Tests** (3 tests):
- ✅ All agents return ChatAgent instances
- ✅ SequentialBuilder accepts all agent instances
- ✅ Correct MCP tool count per agent

**Test Execution**:
```bash
uv run pytest tests/unit/agents/test_agent_instantiation.py -v
# Result: 13 passed in 1.49s ✅
```

### Code Quality Validation

**Linting**:
```bash
uv run ruff check loan_avengers/agents/ --fix
# Result: All checks passed! ✅
```

**Formatting**:
```bash
uv run ruff format loan_avengers/agents/
# Result: All files formatted! ✅
```

### Environment Variables Required

All agents validate these at initialization:

```bash
# Required for all agents
MCP_APPLICATION_VERIFICATION_URL=http://localhost:8010/mcp

# Required for CreditAgent, IncomeAgent, RiskAgent
MCP_FINANCIAL_CALCULATIONS_URL=http://localhost:8012/mcp

# Required for IncomeAgent, RiskAgent
MCP_DOCUMENT_PROCESSING_URL=http://localhost:8011/mcp
```

**Validation Example**:
```python
mcp_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
if not mcp_url:
    raise ValueError(
        "MCP_APPLICATION_VERIFICATION_URL environment variable not set. "
        "Please add to .env file: MCP_APPLICATION_VERIFICATION_URL=http://localhost:8010/mcp"
    )
```

## Testing Performed

### Unit Tests
- ✅ All 13 tests passing
- ✅ Agent initialization with/without client
- ✅ ChatAgent creation from all agents
- ✅ MCP tool validation

### Integration Tests
- ✅ SequentialBuilder workflow execution
- ✅ Event streaming from workflow
- ✅ MCP server connectivity

### Manual Testing
- ✅ Complete loan application processing
- ✅ All agent personas load correctly
- ✅ Progress updates stream to UI
- ✅ Final decisions generated successfully

## Related ADRs

- **ADR-006**: Sequential Workflow Orchestration - Defines the SequentialBuilder pattern
- **ADR-004**: Personality-Driven Agent Architecture - Personas loaded by these agents
- **ADR-008**: Streamable HTTP Transport - MCP server integration
- **ADR-013**: Orchestration Refactoring - Complementary orchestrator-level refactoring

## Future Considerations

### Short Term
1. **Persona Optimization**: Continue reducing persona token usage
2. **Error Handling**: Add retry logic for MCP tool initialization
3. **Configuration Management**: Centralize environment variable validation

### Medium Term
1. **Dynamic Tool Loading**: Load MCP tools based on agent capabilities config
2. **Tool Registry**: Central registry for available MCP servers
3. **Health Checks**: Validate MCP server connectivity at startup

### Long Term
1. **Plugin Architecture**: Hot-reload MCP tools without restarting
2. **Tool Discovery**: Auto-discover available MCP servers
3. **Multi-Model Support**: Different models per agent based on task complexity

## Lessons Learned

### Code Simplification
1. **Delete Dead Code Aggressively**: 60% reduction improved clarity
2. **Single Execution Path**: Framework patterns eliminate need for custom logic
3. **Validate Early**: Environment checks at startup prevent runtime errors

### Framework Adoption
1. **Trust the Framework**: Let it manage lifecycles, events, error handling
2. **Follow Patterns**: Official examples provide battle-tested patterns
3. **Minimal Abstraction**: Thin wrappers over framework components

### Testing Strategy
1. **Test Construction, Not Execution**: Verify agents create correct ChatAgent instances
2. **Mock External Dependencies**: Framework handles actual execution
3. **Integration Tests Separately**: Unit tests for classes, integration for workflows

---

**Date**: 2025-10-02
**Decision Makers**: Development Team
**Implementation**: PR #TBD - Agent Class Simplification
**Success Metrics**:
- ✅ 60% code reduction achieved
- ✅ 13 comprehensive unit tests passing
- ✅ All linting checks passed
- ✅ Type safety validated (Pylance diagnostics resolved)
- ✅ Framework alignment confirmed (Microsoft Agent Framework patterns)
