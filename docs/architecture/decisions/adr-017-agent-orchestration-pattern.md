# ADR-017: Agent Orchestration Pattern - Standalone Agents vs SequentialBuilder

**Status**: Accepted

**Date**: 2025-10-01

**Context**:

We're building a multi-agent loan processing system with these requirements:
1. **Separation of Concerns**: Agent classes own their construction (MCP tools, personas, response formats)
2. **Structured Responses**: Each agent returns typed `AgentResponse[AssessmentType]` with full metadata
3. **Explicit Context Passing**: Agents receive `previous_assessments` for audit trail
4. **Reusability**: Agents must be callable individually, in parallel, or in conditional workflows
5. **MCP Tool Lifecycle**: Proper async context management per-agent
6. **Business Logic First (ADR-002)**: Agents encapsulate domain expertise

The question arose: Should we use Microsoft Agent Framework's `SequentialBuilder` for workflow orchestration, or continue with explicit orchestration using standalone agent classes?

**Decision**:

**Use Standalone Agent Classes with Explicit Orchestration** (current architecture).

**DO NOT adopt SequentialBuilder** as it would violate our architectural principles and provide no meaningful benefits for our use case.

**Alternatives Considered**:

### 1. Standalone Agent Classes (ACCEPTED)
```python
class CreditAgent:
    def __init__(self, chat_client=None):
        self.chat_client = chat_client or AzureAIAgentClient(...)
        self.instructions = PersonaLoader.load_persona("credit")
        self.verification_tool = MCPStreamableHTTPTool(...)
        self.calculations_tool = MCPStreamableHTTPTool(...)

    async def process_application(
        self,
        application: LoanApplication,
        thread: AgentThread | None = None,
        previous_assessments: list[AgentResponse] | None = None
    ) -> AgentResponse[CreditAssessment]:
        # Per-request MCP tool lifecycle
        async with self.verification_tool, self.calculations_tool:
            agent = ChatAgent(
                chat_client=self.chat_client,
                instructions=self.instructions,
                response_format=CreditAssessment,
                tools=[self.verification_tool, self.calculations_tool]
            )
            response = await agent.run(message, thread=thread)
            return AgentResponse(assessment=response.value, ...)

# Pipeline with explicit orchestration
class SequentialPipeline:
    async def process_application(self, application):
        thread = AgentThread()
        previous_assessments = []

        intake_result = await self.intake_agent.process_application(app, thread)
        previous_assessments.append(intake_result)

        credit_result = await self.credit_agent.process_application(
            app, thread, previous_assessments
        )
        previous_assessments.append(credit_result)
        # ... continue sequential processing
```

**Pros**:
- ✅ Complete separation of concerns (agents own construction, pipeline owns orchestration)
- ✅ Type-safe structured responses end-to-end
- ✅ Explicit context passing with full audit trail
- ✅ Per-agent MCP tool lifecycle (resource efficient, proper cleanup)
- ✅ Highly reusable (sequential, parallel, conditional workflows)
- ✅ Easy to test, debug, and monitor
- ✅ Aligns with ADR-002 (business logic first)
- ✅ Framework-agnostic agent design

**Cons**:
- ❌ Manual orchestration code (explicit agent calls)
- ❌ No built-in framework event streaming (implement custom ProcessingUpdate)

### 2. SequentialBuilder (REJECTED)
```python
# Would require exposing ChatAgent creation
class CreditAgent:
    async def get_chat_agent(self) -> ChatAgent:
        return ChatAgent(...)  # Violates encapsulation

# Pipeline would manage all MCP tool connections upfront
class SequentialPipelineWithBuilder:
    async def process_application(self, application):
        # Connect ALL tools upfront (inefficient)
        async with (
            intake_tool, credit_tool1, credit_tool2,
            income_tool1, income_tool2, income_tool3,
            risk_tool1, risk_tool2, risk_tool3
        ):
            workflow = (
                SequentialBuilder()
                .participants([intake_chat, credit_chat, income_chat, risk_chat])
                .build()
            )
            result = await workflow.run(application_input)
            # Generic output, must parse back to structured types
```

**Pros**:
- ✅ Uses framework's SequentialBuilder
- ✅ Potential framework event streaming

**Cons**:
- ❌ Loses structured responses (generic workflow output, must parse back)
- ❌ Loses explicit context passing (SharedState with string keys, no type safety)
- ❌ Upfront MCP tool connection (resource inefficient, all tools connected even if early agent fails)
- ❌ Violates encapsulation (agents must expose ChatAgent creation)
- ❌ Violates ADR-002 (agent construction logic leaks to pipeline)
- ❌ Harder to debug (framework manages execution)
- ❌ Reduces reusability (tightly coupled to sequential workflow)

### 3. Adapter Pattern (REJECTED)
Create adapter layer to wrap standalone agents for SequentialBuilder compatibility.

**Pros**:
- ✅ Could use SequentialBuilder while keeping some agent structure

**Cons**:
- ❌ Adds significant complexity with no architectural benefit
- ❌ Still suffers from all SequentialBuilder cons above
- ❌ Additional adapter maintenance burden
- ❌ Obscures agent responsibilities further

**Rationale**:

### SequentialBuilder is the Wrong Tool for Our Use Case

**SequentialBuilder is designed for**:
- Simple sequential conversation flows
- Agents that follow `AgentProtocol` with standardized signatures
- String-based messaging between agents
- Framework-managed state via SharedState

**Our System Requires**:
- ✅ Structured, typed assessments (not string messages)
- ✅ Explicit context passing with audit trails
- ✅ Per-agent resource management (MCP tools)
- ✅ Agent reusability across multiple workflow patterns
- ✅ Business logic encapsulation (ADR-002)

### Our Architecture Aligns with Enterprise Patterns

**Domain-Driven Design**:
- Agents are domain services with clear bounded contexts
- Each agent owns its tools, expertise, and response format
- Pipeline is application service orchestrating domain services

**Clean Architecture**:
- Dependency inversion: Pipeline depends on agent abstractions
- Agents don't depend on pipeline orchestration
- Business logic (agents) independent of frameworks

**Separation of Concerns**:
- Agents: Construction, domain logic, tool management, response formatting
- Pipeline: Orchestration, progress tracking, error handling
- Clear boundaries enable independent testing and evolution

### MCP Tool Lifecycle Best Practices

**Per-Request Connection (Current)**:
```python
async def process_application(self, application, thread, previous_assessments):
    async with self.tool1, self.tool2:  # Connect only when needed
        agent = ChatAgent(..., tools=[self.tool1, self.tool2])
        return await agent.run(...)  # Proper cleanup on exit
```

**Benefits**:
1. Resource efficiency: Tools only connected when agent executes
2. Error isolation: Early agent failure doesn't connect later agents' tools
3. Clear lifecycle: Tool connection/cleanup scoped to agent execution
4. Testability: Easy to mock tools per-agent

**Upfront Connection (SequentialBuilder)**:
```python
async with tool1, tool2, tool3, tool4, tool5, tool6:  # All tools connected
    workflow = SequentialBuilder().participants([...]).build()
    result = await workflow.run(...)  # If first agent fails, tools 2-6 were wasted
```

**Problems**:
1. Resource waste: All tools connected even if early agents fail
2. Blast radius: One tool connection failure affects entire workflow
3. Unclear ownership: Which agent owns which tool cleanup?

### Context Passing and Audit Trails

**Explicit Approach (Current)**:
```python
previous_assessments: list[AgentResponse] = []

intake_result = await intake_agent.process(app, thread)
previous_assessments.append(intake_result)  # Type-safe, explicit

credit_result = await credit_agent.process(app, thread, previous_assessments)
previous_assessments.append(credit_result)  # Audit trail building
```

**Benefits**:
- Type-safe: `previous_assessments: list[AgentResponse[Assessment]]`
- Explicit: Clear data flow through workflow
- Audit trail: Full history of agent decisions
- Debuggable: Easy to inspect intermediate results

**SharedState Approach (SequentialBuilder)**:
```python
await shared_state.set("intake_result", intake_output)  # String key, no type
result = await shared_state.get("credit_result")  # Could be None, wrong type
```

**Problems**:
- No type safety: Dictionary-like access with string keys
- Implicit: Data flow hidden in framework
- Error-prone: Typos in keys, missing None checks
- Audit trail unclear: Must reconstruct from SharedState

**Implementation**:

### Agent Class Structure (No Changes Needed)
```python
class CreditAgent:
    """
    Credit assessment agent following domain-driven design.

    Owns:
    - Persona/instructions (domain expertise)
    - MCP tools (dependencies)
    - Response format (domain model)
    - Configuration (temperature, max_tokens)
    """

    def __init__(self, chat_client=None, temperature=0.2, max_tokens=600):
        self.chat_client = chat_client or AzureAIAgentClient(...)
        self.instructions = PersonaLoader.load_persona("credit")
        self.verification_tool = MCPStreamableHTTPTool(...)
        self.calculations_tool = MCPStreamableHTTPTool(...)
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def process_application(
        self,
        application: LoanApplication,
        thread: AgentThread | None = None,
        previous_assessments: list[AgentResponse] | None = None
    ) -> AgentResponse[CreditAssessment]:
        """
        Process credit assessment with per-request tool lifecycle.

        Args:
            application: Loan application to assess
            thread: Conversation thread for context
            previous_assessments: Results from previous agents

        Returns:
            Structured response with typed assessment
        """
        async with self.verification_tool, self.calculations_tool:
            agent = ChatAgent(
                chat_client=self.chat_client,
                instructions=self.instructions,
                name="Credit_Assessor",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=CreditAssessment,
                tools=[self.verification_tool, self.calculations_tool]
            )

            # Build message with context
            context_info = self._build_context(previous_assessments)
            message = f"Analyze creditworthiness:\n{application.model_dump_json()}{context_info}"

            # Execute with framework
            response = await agent.run(message, thread=thread)

            # Return structured response
            return AgentResponse(
                assessment=response.value,
                usage_stats=UsageStats(...),
                response_id=response.response_id,
                agent_name="credit",
                application_id=application.application_id
            )
```

### Pipeline Orchestration (Current Pattern)
```python
class SequentialPipeline:
    """
    Sequential workflow orchestrator using standalone agent classes.

    Responsibilities:
    - Agent execution order
    - Progress updates (ProcessingUpdate events)
    - Error handling and recovery
    - Final result assembly

    Does NOT:
    - Manage agent construction (agents own this)
    - Manage MCP tools (agents own this)
    - Format agent responses (agents own this)
    """

    def __init__(self, chat_client=None):
        self.chat_client = chat_client or AzureAIAgentClient(...)
        self.intake_agent = IntakeAgent(chat_client=self.chat_client)
        self.credit_agent = CreditAgent(chat_client=self.chat_client)
        self.income_agent = IncomeAgent(chat_client=self.chat_client)
        self.risk_agent = RiskAgent(chat_client=self.chat_client)

    async def process_application(
        self,
        application: LoanApplication
    ) -> AsyncGenerator[ProcessingUpdate | FinalDecisionResponse, None]:
        """
        Execute sequential workflow with explicit orchestration.

        Pattern:
        1. Create shared thread for conversation context
        2. Execute agents sequentially
        3. Pass previous assessments explicitly
        4. Yield progress updates
        5. Return final decision with audit trail
        """
        thread = AgentThread()
        previous_assessments = []

        # Phase 1: Intake
        yield ProcessingUpdate(agent_name="Intake_Validator", phase="validating", ...)
        intake_result = await self.intake_agent.process_application(
            application, thread=thread
        )
        previous_assessments.append(intake_result)

        # Phase 2: Credit
        yield ProcessingUpdate(agent_name="Credit_Assessor", phase="assessing_credit", ...)
        credit_result = await self.credit_agent.process_application(
            application, thread=thread, previous_assessments=previous_assessments
        )
        previous_assessments.append(credit_result)

        # Phase 3: Income
        yield ProcessingUpdate(agent_name="Income_Verifier", phase="verifying_income", ...)
        income_result = await self.income_agent.process_application(
            application, thread=thread, previous_assessments=previous_assessments
        )
        previous_assessments.append(income_result)

        # Phase 4: Risk (Final Decision)
        yield ProcessingUpdate(agent_name="Risk_Analyzer", phase="deciding", ...)
        risk_result = await self.risk_agent.process_application(
            application, thread=thread, previous_assessments=previous_assessments
        )

        # Yield final decision with full audit trail
        yield FinalDecisionResponse(
            decision=risk_result.assessment,
            audit_trail=previous_assessments,
            application_id=application.application_id
        )
```

### Future Workflow Patterns (Enabled by This Architecture)

**Parallel Processing**:
```python
# Can run credit and income in parallel since agents are independent
credit_task = self.credit_agent.process_application(app, thread)
income_task = self.income_agent.process_application(app, thread)

credit_result, income_result = await asyncio.gather(credit_task, income_task)
```

**Conditional Routing**:
```python
# Can skip agents based on conditions
intake_result = await self.intake_agent.process_application(app, thread)

if intake_result.assessment.risk_level == "LOW":
    # Fast-track: Skip detailed income verification
    risk_result = await self.risk_agent.process_application(
        app, thread, [intake_result]
    )
else:
    # Full verification needed
    credit_result = await self.credit_agent.process_application(...)
    income_result = await self.income_agent.process_application(...)
    risk_result = await self.risk_agent.process_application(...)
```

**Agent Reuse**:
```python
# Use credit agent in different context
standalone_credit_check = await credit_agent.process_application(
    application=partial_app,
    thread=None,  # No conversation context
    previous_assessments=None  # Standalone assessment
)
```

**Consequences**:

### Positive
- ✅ **Separation of Concerns**: Clear boundaries between agents (domain) and pipeline (orchestration)
- ✅ **Type Safety**: Structured responses throughout workflow
- ✅ **Resource Efficiency**: Per-agent MCP tool lifecycle
- ✅ **Explicit Audit Trail**: `previous_assessments` provides full context
- ✅ **Reusability**: Agents work in sequential, parallel, conditional workflows
- ✅ **Testability**: Easy to unit test agents and pipeline separately
- ✅ **Observability**: Full control over logging, metrics, tracing
- ✅ **Maintainability**: Changes to agents don't affect pipeline, and vice versa
- ✅ **Aligns with ADR-002**: Business logic first, framework-agnostic design
- ✅ **Future-Proof**: Can adopt SequentialBuilder later if requirements change

### Negative
- ❌ **Manual Orchestration**: Must write explicit sequential code (vs framework-managed)
- ❌ **Custom Progress Events**: Must implement ProcessingUpdate (vs framework events)
- ❌ **No Framework Event Streaming**: Custom implementation needed (already done)

### Risks and Mitigation

**Risk**: Manual orchestration code becomes complex as workflows grow
**Mitigation**: Extract orchestration patterns to reusable base classes if needed

**Risk**: Not using framework features (SequentialBuilder) seems non-idiomatic
**Mitigation**: SequentialBuilder is optional, not required. Using it where it doesn't fit is worse than not using it.

**Risk**: Future framework updates might assume SequentialBuilder usage
**Mitigation**: Our agent classes can be adapted if needed. Architecture is framework-agnostic (ADR-002).

**Related ADRs**:
- ADR-001: Multi-Agent Strategic Foundation
- ADR-002: Business Logic First Approach
- ADR-004: Personality-Driven Agent Architecture
- ADR-005: API Architecture with FastAPI and Microsoft Agent Framework
- ADR-007: Conversation State with AgentThread

**Implementation Status**: ✅ Already Implemented

This is our current architecture. This ADR documents the decision to **continue using it** rather than adopting SequentialBuilder.

**Decision Date**: 2025-10-01

**Decision Rationale**: SequentialBuilder is designed for conversational workflows with string messages and framework-managed state. Our system requires structured data processing with typed responses, explicit context passing, and per-agent resource management. Forcing SequentialBuilder adoption would violate our architectural principles (ADR-002) and provide no meaningful benefits.

**Key Principle**: **Use the right tool for the job.** SequentialBuilder is powerful for certain use cases, but not ours. Our explicit orchestration pattern is architecturally superior for structured multi-agent data processing workflows.
