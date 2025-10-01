# ADR-017: Agent Orchestration with Microsoft Agent Framework's SequentialBuilder

**Status**: Accepted (REVISED - 2025-10-01)

**Date**: 2025-10-01
**Revision**: Complete rewrite based on implemented architecture

## Context

We're building a multi-agent loan processing system using Microsoft Agent Framework. We needed to decide how to orchestrate multiple specialized agents (Intake, Credit, Income, Risk) that work together sequentially to process loan applications.

**Key Requirements**:
1. Clear separation between agents (domain logic) and orchestration (workflow management)
2. Agents must be autonomous and handle their own MCP tool connections
3. Framework should manage workflow execution and state
4. Real-time progress updates for UI
5. Type-safe structured responses from each agent
6. Testable architecture with mockable dependencies

**Prior State**: Original ADR-017 (now superseded) rejected SequentialBuilder in favor of custom orchestration with explicit `process_application()` methods and manual context passing.

## Decision

**ADOPT Microsoft Agent Framework's SequentialBuilder** for workflow orchestration with a clean agent architecture.

**Final Architecture Pattern**:
```python
# Agents: Own construction, provide ChatAgent for framework
class CreditAgent:
    def __init__(self, chat_client=None, temperature=0.2, max_tokens=600):
        self.chat_client = chat_client or AzureAIAgentClient(...)
        self.instructions = PersonaLoader.load_persona("credit")

        # Agents own their MCP tools
        self.verification_tool = MCPStreamableHTTPTool(...)
        self.calculations_tool = MCPStreamableHTTPTool(...)

        self.temperature = temperature
        self.max_tokens = max_tokens

    def create_agent(self) -> ChatAgent:
        """Create ChatAgent for SequentialBuilder with tools pre-configured."""
        return self.chat_client.create_agent(
            name="Credit_Assessor",
            instructions=self.instructions,
            model_config={"temperature": self.temperature, "max_tokens": self.max_tokens},
            response_format=CreditAssessment,
            tools=[self.verification_tool, self.calculations_tool]
        )

# Orchestrator: Uses SequentialBuilder for workflow
class SequentialPipeline:
    def __init__(self, chat_client=None):
        self.chat_client = chat_client or AzureAIAgentClient(...)

        # Instantiate agent classes
        self.intake_agent = IntakeAgent(chat_client=self.chat_client)
        self.credit_agent = CreditAgent(chat_client=self.chat_client)
        self.income_agent = IncomeAgent(chat_client=self.chat_client)
        self.risk_agent = RiskAgent(chat_client=self.chat_client)

    async def process_application(self, application):
        # Get ChatAgent instances from agent classes
        intake_chat = self.intake_agent.create_agent()
        credit_chat = self.credit_agent.create_agent()
        income_chat = self.income_agent.create_agent()
        risk_chat = self.risk_agent.create_agent()

        # Build sequential workflow
        workflow = (
            SequentialBuilder()
            .participants([intake_chat, credit_chat, income_chat, risk_chat])
            .build()
        )

        # Stream workflow events
        async for event in workflow.run_stream(application_input):
            yield self._convert_to_processing_update(event)
```

## Rationale

### Why SequentialBuilder NOW (vs. Original Rejection)?

**Original Concerns** (from superseded ADR-017):
- ❌ "Loses structured responses" → **SOLVED**: Agents use `response_format=AssessmentType`
- ❌ "Upfront MCP tool connection" → **SOLVED**: Framework manages tool lifecycle automatically
- ❌ "Violates encapsulation" → **SOLVED**: `create_agent()` is clean interface, not leaking internals
- ❌ "Loses audit trail" → **SOLVED**: Framework maintains shared conversation context
- ❌ "Harder to debug" → **SOLVED**: Framework provides excellent observability

**What Changed Our Mind**:
1. **Framework Maturity**: Better understanding of how agent_framework manages tools
2. **Clean Pattern**: `create_agent()` method provides clean separation without leaking internals
3. **Less Code**: 60% reduction in agent code by removing custom orchestration
4. **Framework Benefits**: Get event streaming, state management, error handling for free
5. **Architectural Alignment**: Agents construct, SequentialBuilder orchestrates - clean separation

### Separation of Concerns (Achieved)

**Agents (Domain Layer)**:
- ✅ Own their construction (`__init__`)
- ✅ Own their MCP tools (created in constructor)
- ✅ Own their personas (loaded from markdown)
- ✅ Own their response formats (Pydantic models)
- ✅ Own their configuration (temperature, max_tokens)
- ✅ Provide ChatAgent via `create_agent()` for orchestration

**SequentialPipeline (Orchestration Layer)**:
- ✅ Instantiates agent classes
- ✅ Calls `create_agent()` on each
- ✅ Builds workflow with SequentialBuilder
- ✅ Streams events from framework
- ✅ Converts events to UI-friendly format

**Clear Boundary**: Agents know nothing about SequentialBuilder. Pipeline knows nothing about MCP tools.

### Agent Autonomy

Each agent is **fully autonomous**:
- Decides which MCP tools it needs (1-3 tools)
- Configures tools at initialization
- Framework automatically manages tool connections when agent executes
- No shared state or dependencies between agents

**Example - Different Tool Configurations**:
```python
IntakeAgent:  1 tool  (verification)
CreditAgent:  2 tools (verification, calculations)
IncomeAgent:  3 tools (verification, documents, calculations)
RiskAgent:    3 tools (verification, documents, calculations)
```

Agents can evolve independently without affecting orchestration.

### Tool Lifecycle Management

**Framework Pattern** (Auto-managed):
```python
def create_agent(self):
    return self.chat_client.create_agent(
        tools=[self.verification_tool, self.calculations_tool]
    )
    # Framework handles: __aenter__(), execution, __aexit__()
```

**Benefits**:
- ✅ Framework manages connection/cleanup automatically
- ✅ Tools connected only when agent executes
- ✅ Proper error handling and resource cleanup
- ✅ No manual async context management

**Previous Pattern** (Manual management):
```python
async def process_application(self, application):
    async with self.tool1, self.tool2:  # Manual lifecycle
        agent = ChatAgent(...)
        return await agent.run(...)
```

Framework approach is cleaner and less error-prone.

### Structured Responses

**Achieved via Pydantic Response Formats**:
```python
# Agent configuration
response_format=CreditAssessment  # Pydantic v2 model

# Agent output is typed
class CreditAssessment(BaseModel):
    credit_score: int
    risk_level: str
    recommendation: str
    ...
```

Framework ensures all responses match the specified format. Type safety maintained end-to-end.

### Real-time Progress Updates

**Framework Streaming**:
```python
async for event in workflow.run_stream(application_input):
    if hasattr(event, "executor_id"):
        # Convert WorkflowEvent to ProcessingUpdate for UI
        yield ProcessingUpdate(
            agent_name=event.executor_id,
            phase=self._map_phase(event.executor_id),
            completion_percentage=self._calculate_completion(event.executor_id)
        )
```

Framework provides real-time events. We convert them to UI-friendly format.

## Alternatives Considered

### 1. SequentialBuilder (ACCEPTED)

**Current Implementation** - Agents construct, framework orchestrates.

**Pros**:
- ✅ 60% code reduction per agent (280-330 lines → 110-150 lines)
- ✅ Framework manages tool lifecycle, threading, state
- ✅ Real-time event streaming built-in
- ✅ Clean separation of concerns
- ✅ Type-safe with `response_format`
- ✅ Agents remain autonomous and testable
- ✅ Less manual orchestration code
- ✅ Better error handling (framework-provided)

**Cons**:
- ❌ Tied to Microsoft Agent Framework (acceptable trade-off)
- ❌ Learning curve for framework patterns

### 2. Custom Orchestration with process_application() (REJECTED)

**Previous Pattern** - Each agent had `process_application()` method with manual orchestration.

**Pros**:
- ✅ Full control over execution
- ✅ Framework-agnostic

**Cons**:
- ❌ 60% more code per agent
- ❌ Manual tool lifecycle management (error-prone)
- ❌ Manual context passing between agents
- ❌ Must implement custom progress events
- ❌ More surface area for bugs
- ❌ Violates "use the framework" principle

### 3. Other Orchestration Frameworks (REJECTED)

Considered: LangGraph, CrewAI, AutoGen

**Cons**:
- ❌ Would require switching entire agent framework
- ❌ Additional dependencies
- ❌ Microsoft Agent Framework already provides SequentialBuilder

## Implementation

### Agent Structure (Simplified)

**Before** (Custom Orchestration):
```python
class CreditAgent:
    def __init__(self, chat_client=None, temperature=0.2, max_tokens=600):
        # ... setup ...
        self.verification_tool = MCPStreamableHTTPTool(...)
        self.calculations_tool = MCPStreamableHTTPTool(...)

    async def process_application(self, application, thread, previous_assessments):
        # 170+ lines of manual orchestration
        async with self.verification_tool, self.calculations_tool:
            agent = ChatAgent(...)
            response = await agent.run(...)
            # Build AgentResponse with usage stats, context, etc.
            return AgentResponse(...)
```

**After** (SequentialBuilder):
```python
class CreditAgent:
    def __init__(self, chat_client=None, temperature=0.2, max_tokens=600):
        self.chat_client = chat_client or AzureAIAgentClient(...)
        self.instructions = PersonaLoader.load_persona("credit")

        # Validate environment variables
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        if not verification_url:
            raise ValueError("MCP_APPLICATION_VERIFICATION_URL not set")

        self.verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Credit report and identity verification",
            load_tools=True,
            load_prompts=False,
        )

        calculations_url = os.getenv("MCP_FINANCIAL_CALCULATIONS_URL")
        if not calculations_url:
            raise ValueError("MCP_FINANCIAL_CALCULATIONS_URL not set")

        self.calculations_tool = MCPStreamableHTTPTool(
            name="financial-calculations",
            url=calculations_url,
            description="Financial calculations for credit analysis",
            load_tools=True,
            load_prompts=False,
        )

        self.temperature = temperature
        self.max_tokens = max_tokens

    def create_agent(self) -> ChatAgent:
        """Create ChatAgent for SequentialBuilder."""
        return self.chat_client.create_agent(
            name="Credit_Assessor",
            instructions=self.instructions,
            model_config={"temperature": self.temperature, "max_tokens": self.max_tokens},
            response_format=CreditAssessment,
            tools=[self.verification_tool, self.calculations_tool]
        )
```

**Reduction**: 310 lines → 125 lines (60% reduction)

### Orchestrator Structure

```python
class SequentialPipeline:
    def __init__(self, chat_client=None):
        self.chat_client = chat_client or AzureAIAgentClient(...)

        # Instantiate agent classes
        self.intake_agent = IntakeAgent(chat_client=self.chat_client)
        self.credit_agent = CreditAgent(chat_client=self.chat_client)
        self.income_agent = IncomeAgent(chat_client=self.chat_client)
        self.risk_agent = RiskAgent(chat_client=self.chat_client)

    async def process_application(self, application):
        # Create ChatAgents from agent classes
        intake_chat = self.intake_agent.create_agent()
        credit_chat = self.credit_agent.create_agent()
        income_chat = self.income_agent.create_agent()
        risk_chat = self.risk_agent.create_agent()

        # Build sequential workflow
        workflow = (
            SequentialBuilder()
            .participants([intake_chat, credit_chat, income_chat, risk_chat])
            .build()
        )

        # Format input
        application_input = f"""Process this loan application:
Application ID: {application.application_id}
Applicant: {application.applicant_name}
Loan Amount: ${application.loan_amount:,.2f}
Annual Income: ${application.annual_income:,.2f}
..."""

        # Stream workflow events
        async for event in workflow.run_stream(application_input):
            if hasattr(event, "executor_id"):
                yield ProcessingUpdate(
                    agent_name=str(event.executor_id),
                    phase=self._map_phase(event.executor_id),
                    completion_percentage=self._calculate_completion(event.executor_id),
                    status="in_progress"
                )

        # Final completion
        yield ProcessingUpdate(
            agent_name="Risk_Analyzer",
            phase="completed",
            completion_percentage=100,
            status="completed"
        )
```

## Consequences

### Positive

1. **✅ 60% Code Reduction**: Agents streamlined from 280-330 lines to 110-150 lines
2. **✅ Framework Benefits**: Tool lifecycle, state management, error handling provided
3. **✅ Clean Architecture**: Agents construct, SequentialBuilder orchestrates
4. **✅ Agent Autonomy**: Each agent fully independent with its own tools
5. **✅ Type Safety**: Structured responses via Pydantic `response_format`
6. **✅ Real-time Events**: Framework provides `workflow.run_stream()`
7. **✅ Less Error-Prone**: No manual async context management
8. **✅ Testability**: Easy to mock `create_agent()` for testing
9. **✅ Environment Validation**: Fail fast with clear errors if MCP URLs missing
10. **✅ Single Execution Path**: No confusing dual patterns

### Negative

1. **❌ Framework Dependency**: Tied to Microsoft Agent Framework patterns
2. **❌ Learning Curve**: Developers must understand SequentialBuilder
3. **❌ Less Control**: Framework manages execution (trade-off for simplicity)

### Migration Impact

**Changes Made**:
- Removed `process_application()` from all agent classes
- Added `create_agent()` method to all agents
- Updated `SequentialPipeline` to use `SequentialBuilder`
- Added environment variable validation for MCP URLs
- Removed mock fallback (fail fast on missing config)

**Test Coverage**:
- 13 unit tests for agent instantiation
- Integration tests for SequentialPipeline
- End-to-end API tests
- All tests passing ✅

## Related ADRs

- **ADR-001**: Multi-Agent Strategic Foundation
- **ADR-002**: Business Logic First Approach
- **ADR-004**: Personality-Driven Agent Architecture
- **ADR-005**: API Architecture with FastAPI and Microsoft Agent Framework
- **ADR-007**: Conversation State with AgentThread

## Implementation Status

✅ **Fully Implemented** (2025-10-01)

All agents refactored to use SequentialBuilder pattern. Previous custom orchestration removed.

## Decision Timeline

- **2025-10-01 (Early)**: Original ADR-017 rejected SequentialBuilder
- **2025-10-01 (Revised)**: After implementation review and refactoring, **ADOPTED SequentialBuilder**
- **Rationale for Reversal**: Better understanding of framework, clean `create_agent()` pattern, significant code reduction

## Key Principle

**"Use the framework when it fits."**

SequentialBuilder is the right tool for sequential multi-agent workflows with:
- Autonomous agents that own their tools
- Structured responses via Pydantic models
- Real-time progress updates
- Clean separation between construction and orchestration

Our implementation achieves all architectural goals while leveraging framework capabilities.

---

**Supersedes**: ADR-017 (Original - dated 2025-10-01, rejected SequentialBuilder)
**Current Status**: This is the **active** ADR-017 reflecting our implemented architecture.
