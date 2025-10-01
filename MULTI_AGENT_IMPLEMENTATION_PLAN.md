# Multi-Agent Loan Processing System - Implementation Plan

**Date**: 2025-10-01
**Epic**: #62 - Multi-Agent Loan Processing System
**Related Issues**: #64 (Credit), #65 (Income), #66 (Risk), #67 (Orchestrator)

---

## 🎯 Project Goals

1. **Complete multi-agent workflow** with Credit, Income, Risk agents + Orchestrator
2. **Comprehensive logging** for agent handoffs without performance degradation
3. **All MCP servers operational** with proper agent-to-tool assignments
4. **End-to-end integration tests** with NO mocks (real MCP servers)
5. **Comprehensive unit tests** for each agent (85%+ coverage)
6. **Documentation updates** as we proceed with ADRs for decisions
7. **Multiple commits** - one per agent for easy issue tracking

---

## 📋 Architecture Decision Summary

Based on Architecture Review (`ARCHITECTURE_REVIEW_MULTI_AGENT_IMPLEMENTATION.md`):

### ✅ Key Decisions
1. **Use IntakeAgent as canonical pattern** - All agents follow same structure
2. **Explicit Orchestration** - NOT using SequentialBuilder (need conditional routing)
3. **Progressive logging** - INFO for handoffs, DEBUG for tool calls
4. **MCP Tool Assignment**:
   - Intake: verification (8010)
   - Credit: verification (8010) + calculations (8012)
   - Income: verification (8010) + documents (8011) + calculations (8012)
   - Risk: ALL three MCP servers (comprehensive analysis)
5. **Error Handling**: Always return response, never throw unhandled exceptions
6. **Testing**: Real MCP servers via MCPTestHarness, no mocks for integration

---

## 📊 Implementation Phases

### **Phase 1: Agent Implementations (Issues #64, #65, #66)**

#### Step 1.1: Credit Agent (#64)
**Files**:
- `apps/api/loan_avengers/agents/credit_agent.py`
- `tests/unit/agents/test_credit_agent.py`

**Pattern** (following `intake_agent.py`):
```python
class CreditAgent:
    def __init__(self, chat_client, temperature=0.2, max_tokens=600):
        # Load persona from PersonaLoader
        # Create MCP tools: verification (8010) + calculations (8012)
        # Store configuration

    async def process_application(self, application, thread, previous_assessments):
        async with self.verification_tool, self.calculations_tool:
            # Create ChatAgent with response_format=CreditAssessment
            # Include previous_assessments in message context
            # Return AgentResponse[CreditAssessment]
```

**MCP Tools**:
- `application-verification` (8010): `retrieve_credit_report()`, `verify_employment()`
- `financial-calculations` (8012): `calculate_debt_to_income_ratio()`, `calculate_credit_utilization_ratio()`

**Logging Points**:
- Agent initialization (INFO)
- Processing start with previous context flag (INFO)
- Tool calls (DEBUG)
- Credit analysis completed with score/risk (INFO)
- Errors with context (ERROR)

**Unit Tests**:
- Agent initialization
- Process application with mock chat client
- Error handling scenarios
- Response parsing and validation

**Commit**: `feat: implement Credit Agent following IntakeAgent pattern (#64)`

---

#### Step 1.2: Income Agent (#65)
**Files**:
- `apps/api/loan_avengers/agents/income_agent.py`
- `tests/unit/agents/test_income_agent.py`

**Pattern** (following `intake_agent.py`):
```python
class IncomeAgent:
    def __init__(self, chat_client, temperature=0.1, max_tokens=500):
        # Load persona from PersonaLoader
        # Create MCP tools: verification (8010) + documents (8011) + calculations (8012)
        # Store configuration

    async def process_application(self, application, thread, previous_assessments):
        async with self.verification_tool, self.documents_tool, self.calculations_tool:
            # Create ChatAgent with response_format=IncomeAssessment
            # Include previous_assessments (intake + credit) in message context
            # Return AgentResponse[IncomeAssessment]
```

**MCP Tools**:
- `application-verification` (8010): `verify_employment()`, `get_bank_account_data()`, `get_tax_transcript_data()`
- `document-processing` (8011): `extract_text_from_document()`, `validate_document_format()`
- `financial-calculations` (8012): `analyze_income_stability()`, `calculate_loan_affordability()`

**Logging Points**:
- Agent initialization (INFO)
- Processing start with previous context summary (INFO)
- Tool calls for each MCP server (DEBUG)
- Income verification completed with stability assessment (INFO)
- Errors with context (ERROR)

**Unit Tests**:
- Agent initialization with 3 MCP tools
- Process application with mock chat client
- Error handling scenarios
- Response parsing and validation

**Commit**: `feat: implement Income Agent with multi-MCP tool support (#65)`

---

#### Step 1.3: Risk Agent (#66)
**Files**:
- `apps/api/loan_avengers/agents/risk_agent.py`
- `tests/unit/agents/test_risk_agent.py`

**Pattern** (following `intake_agent.py`):
```python
class RiskAgent:
    def __init__(self, chat_client, temperature=0.1, max_tokens=600):
        # Load persona from PersonaLoader
        # Create MCP tools: ALL three (verification + documents + calculations)
        # Store configuration

    async def process_application(self, application, thread, previous_assessments):
        async with self.verification_tool, self.documents_tool, self.calculations_tool:
            # Create ChatAgent with response_format=RiskAssessment
            # Include ALL previous_assessments (intake + credit + income) in context
            # Return AgentResponse[RiskAssessment]
```

**MCP Tools**:
- ALL three MCP servers for comprehensive risk synthesis

**Logging Points**:
- Agent initialization (INFO)
- Processing start with full assessment summary (INFO)
- Tool calls for comprehensive analysis (DEBUG)
- Risk assessment completed with overall risk level (INFO)
- Errors with context (ERROR)

**Unit Tests**:
- Agent initialization with 3 MCP tools
- Process application with mock chat client
- Synthesizing multiple previous assessments
- Error handling scenarios
- Response parsing and validation

**Commit**: `feat: implement Risk Agent with comprehensive synthesis (#66)`

---

### **Phase 2: Orchestrator Implementation (Issue #67)**

#### Step 2.1: LoanProcessingOrchestrator
**Files**:
- `apps/api/loan_avengers/orchestrator.py`
- `tests/unit/test_orchestrator.py`

**Architecture** (Explicit Orchestration Pattern):
```python
class LoanProcessingOrchestrator:
    """
    Explicit workflow orchestrator with conditional routing and handoff logging.
    """

    def __init__(self, chat_client=None):
        # Initialize all agents
        self.intake_agent = IntakeAgent(chat_client)
        self.credit_agent = CreditAgent(chat_client)
        self.income_agent = IncomeAgent(chat_client)
        self.risk_agent = RiskAgent(chat_client)

    async def process_application(
        self,
        application: LoanApplication,
        thread: AgentThread | None = None
    ) -> AgentResponse[LoanDecision]:
        """Process application through multi-agent workflow with logging."""

        # Phase 1: Intake validation
        intake_result = await self._process_intake(application, thread)

        # Phase 2: Conditional routing based on intake decision
        if intake_result.assessment.routing_decision == "FAST_TRACK":
            return await self._process_fast_track(application, thread, intake_result)
        else:
            return await self._process_standard(application, thread, intake_result)

    async def _process_standard(self, application, thread, intake_result):
        """Standard workflow: Credit → Income → Risk → Decision"""

        # Step 1: Credit analysis with handoff logging
        credit_result = await self._process_credit(
            application, thread, [intake_result]
        )

        # Step 2: Income verification with handoff logging
        income_result = await self._process_income(
            application, thread, [intake_result, credit_result]
        )

        # Step 3: Risk assessment with handoff logging
        risk_result = await self._process_risk(
            application, thread, [intake_result, credit_result, income_result]
        )

        # Step 4: Synthesize final decision
        return self._synthesize_decision(
            application, [intake_result, credit_result, income_result, risk_result]
        )

    async def _process_fast_track(self, application, thread, intake_result):
        """Fast-track workflow: Credit → Risk → Decision (skip income)"""

        # Step 1: Credit analysis
        credit_result = await self._process_credit(
            application, thread, [intake_result]
        )

        # Step 2: Risk assessment (no income agent)
        risk_result = await self._process_risk(
            application, thread, [intake_result, credit_result]
        )

        # Step 3: Synthesize final decision
        return self._synthesize_decision(
            application, [intake_result, credit_result, risk_result]
        )

    async def _process_intake(self, application, thread):
        """Process intake with logging."""
        logger.info("Starting intake processing", extra={
            "application_id": mask_id(application.application_id),
            "workflow_phase": "intake"
        })

        result = await self.intake_agent.process_application(application, thread)

        logger.info("Agent handoff", extra={
            "from_agent": "START",
            "to_agent": "intake",
            "routing_decision": result.assessment.routing_decision,
            "confidence": result.assessment.confidence_score
        })

        return result

    async def _process_credit(self, application, thread, previous_assessments):
        """Process credit with handoff logging."""
        logger.info("Agent handoff", extra={
            "from_agent": "intake",
            "to_agent": "credit",
            "application_id": mask_id(application.application_id),
            "previous_count": len(previous_assessments)
        })

        result = await self.credit_agent.process_application(
            application, thread, previous_assessments
        )

        logger.info("Credit processing completed", extra={
            "application_id": mask_id(application.application_id),
            "risk_level": result.assessment.risk_level,
            "next_agent": result.assessment.next_agent
        })

        return result

    async def _process_income(self, application, thread, previous_assessments):
        """Process income with handoff logging."""
        logger.info("Agent handoff", extra={
            "from_agent": "credit",
            "to_agent": "income",
            "application_id": mask_id(application.application_id),
            "previous_count": len(previous_assessments)
        })

        result = await self.income_agent.process_application(
            application, thread, previous_assessments
        )

        logger.info("Income processing completed", extra={
            "application_id": mask_id(application.application_id),
            "income_stability": result.assessment.income_stability,
            "next_agent": result.assessment.next_agent
        })

        return result

    async def _process_risk(self, application, thread, previous_assessments):
        """Process risk with handoff logging."""
        logger.info("Agent handoff", extra={
            "from_agent": "income" if len(previous_assessments) > 2 else "credit",
            "to_agent": "risk",
            "application_id": mask_id(application.application_id),
            "previous_count": len(previous_assessments)
        })

        result = await self.risk_agent.process_application(
            application, thread, previous_assessments
        )

        logger.info("Risk processing completed", extra={
            "application_id": mask_id(application.application_id),
            "overall_risk": result.assessment.overall_risk,
            "recommendation": result.assessment.loan_recommendation
        })

        return result

    def _synthesize_decision(
        self,
        application: LoanApplication,
        all_assessments: list[AgentResponse]
    ) -> AgentResponse[LoanDecision]:
        """Synthesize final decision from all agent assessments."""
        logger.info("Synthesizing final decision", extra={
            "application_id": mask_id(application.application_id),
            "assessment_count": len(all_assessments)
        })

        # Extract final recommendation from risk agent
        risk_result = all_assessments[-1]
        recommendation = risk_result.assessment.loan_recommendation

        # Map recommendation to decision
        decision_map = {
            "APPROVE": "APPROVED",
            "CONDITIONAL": "CONDITIONALLY_APPROVED",
            "DECLINE": "DECLINED",
            "MANUAL_REVIEW": "MANUAL_REVIEW"
        }

        decision = LoanDecision(
            decision=decision_map.get(recommendation, "MANUAL_REVIEW"),
            approved_amount=application.loan_amount if recommendation == "APPROVE" else None,
            interest_rate=self._calculate_interest_rate(all_assessments),
            loan_term_months=application.loan_term_months if recommendation == "APPROVE" else None,
            conditions=self._extract_conditions(all_assessments),
            decline_reasons=self._extract_decline_reasons(all_assessments),
            processing_summary=self._build_summary(all_assessments),
            confidence_score=self._calculate_confidence(all_assessments)
        )

        return AgentResponse(
            assessment=decision,
            usage_stats=self._aggregate_usage_stats(all_assessments),
            response_id=None,
            created_at=None,
            agent_name="orchestrator",
            application_id=application.application_id
        )
```

**Logging Strategy**:
- Workflow start (INFO)
- Each agent handoff with routing info (INFO)
- Each agent completion with key metrics (INFO)
- Decision synthesis (INFO)
- Errors at any step (ERROR with full context)

**Unit Tests**:
- Orchestrator initialization
- Standard workflow path
- Fast-track workflow path
- Decision synthesis logic
- Error handling at each stage
- Partial results handling

**Commit**: `feat: implement LoanProcessingOrchestrator with explicit workflow (#67)`

---

### **Phase 3: Testing Infrastructure**

#### Step 3.1: MCPTestHarness
**Files**:
- `tests/integration/test_harness.py`

**Purpose**: Start all 3 MCP servers for integration tests (NO MOCKS!)

```python
class MCPTestHarness:
    """
    Test harness for running integration tests with real MCP servers.

    Starts all 3 MCP servers on their designated ports:
    - application_verification: 8010
    - document_processing: 8011
    - financial_calculations: 8012
    """

    async def __aenter__(self):
        """Start all MCP servers."""
        self.servers = []
        self.servers.append(await self._start_server("application_verification", 8010))
        self.servers.append(await self._start_server("document_processing", 8011))
        self.servers.append(await self._start_server("financial_calculations", 8012))

        # Wait for health checks
        await self._wait_for_health()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop all MCP servers."""
        for server in self.servers:
            server.terminate()

    async def _start_server(self, name, port):
        """Start individual MCP server process."""
        # Implementation to start server as subprocess
        pass

    async def _wait_for_health(self):
        """Wait for all servers to be healthy."""
        # Poll health check endpoints
        pass
```

**Commit**: `test: create MCPTestHarness for integration testing`

---

#### Step 3.2: Integration Tests
**Files**:
- `tests/integration/test_multi_agent_workflow.py`
- `tests/integration/test_credit_agent_integration.py`
- `tests/integration/test_income_agent_integration.py`
- `tests/integration/test_risk_agent_integration.py`

**Coverage**:
- End-to-end workflow (intake → credit → income → risk → decision)
- Fast-track routing (intake → credit → risk → decision)
- Each agent with real MCP servers
- Error scenarios (MCP server down, timeout, tool failure)
- Performance tests (<3 minute SLA)

**Example Test**:
```python
@pytest.mark.asyncio
async def test_end_to_end_workflow_with_real_mcp_servers():
    """Test complete workflow with all real MCP servers."""

    async with MCPTestHarness():
        # Create test application
        application = create_test_application()

        # Run through orchestrator
        orchestrator = LoanProcessingOrchestrator()
        result = await orchestrator.process_application(application)

        # Verify decision structure
        assert result.assessment.decision in ["APPROVED", "DECLINED", "CONDITIONALLY_APPROVED"]
        assert result.assessment.confidence_score > 0.0
        assert len(result.assessment.processing_summary) > 0

        # Verify all agents were invoked
        # (check logs or response metadata)
```

**Commit**: `test: add comprehensive integration tests with real MCP servers`

---

### **Phase 4: Documentation & ADRs**

#### ADRs to Create:
1. **ADR-018: Explicit Orchestration Pattern for Multi-Agent Workflow**
   - Why NOT SequentialBuilder
   - Conditional routing requirements
   - Error handling needs
   - Observability requirements

2. **ADR-019: MCP Tool Assignment Strategy**
   - Which agent uses which MCP servers
   - Tool selection rationale
   - Performance considerations
   - Autonomous tool selection by agents

3. **ADR-020: Progressive Logging Strategy for Agent Handoffs**
   - INFO vs DEBUG level decisions
   - Handoff metadata structure
   - Performance impact mitigation
   - PII masking patterns

4. **ADR-021: Integration Testing with Real MCP Servers**
   - NO mocks philosophy
   - MCPTestHarness architecture
   - Coverage requirements (85%+)
   - Performance SLA validation

**Commit**: `docs: add ADRs for multi-agent architectural decisions`

---

## 🎯 Success Criteria

### Functionality
- ✅ All 4 agents implemented following IntakeAgent pattern
- ✅ Orchestrator with conditional routing (FAST_TRACK vs STANDARD)
- ✅ All MCP servers properly assigned and operational
- ✅ End-to-end workflow produces valid LoanDecision
- ✅ Comprehensive logging at agent handoffs

### Testing
- ✅ 85%+ unit test coverage on all agents
- ✅ Integration tests with real MCP servers (NO mocks)
- ✅ End-to-end workflow tests (both standard and fast-track)
- ✅ Error scenario coverage (MCP failures, timeouts, partial results)
- ✅ Performance tests validate <3 minute SLA

### Documentation
- ✅ 4 new ADRs documenting architectural decisions
- ✅ Updated API documentation
- ✅ Integration test README
- ✅ MCP server assignment matrix

### Code Quality
- ✅ All code follows IntakeAgent pattern
- ✅ Comprehensive error handling (always return response)
- ✅ Structured logging with PII masking
- ✅ Type hints and Pydantic models throughout

---

## 📅 Timeline Estimate

**Phase 1**: Agent Implementations (3-4 days)
- Credit Agent: 1 day
- Income Agent: 1-1.5 days (3 MCP tools)
- Risk Agent: 1 day
- Unit tests: 0.5 day

**Phase 2**: Orchestrator (2 days)
- Orchestrator implementation: 1 day
- Decision synthesis logic: 0.5 day
- Unit tests: 0.5 day

**Phase 3**: Testing Infrastructure (2 days)
- MCPTestHarness: 0.5 day
- Integration tests: 1 day
- Performance tests: 0.5 day

**Phase 4**: Documentation (1 day)
- ADRs: 0.5 day
- API docs: 0.25 day
- README updates: 0.25 day

**Total**: 8-9 days (1.5-2 weeks)

---

## 🔄 Commit Strategy

Each major component gets its own commit with issue references:

1. `feat: implement Credit Agent following IntakeAgent pattern (#64)`
2. `test: add unit tests for Credit Agent (#64)`
3. `feat: implement Income Agent with multi-MCP tool support (#65)`
4. `test: add unit tests for Income Agent (#65)`
5. `feat: implement Risk Agent with comprehensive synthesis (#66)`
6. `test: add unit tests for Risk Agent (#66)`
7. `feat: implement LoanProcessingOrchestrator with explicit workflow (#67)`
8. `test: add unit tests for LoanProcessingOrchestrator (#67)`
9. `test: create MCPTestHarness for integration testing`
10. `test: add comprehensive integration tests with real MCP servers`
11. `docs: add ADRs for multi-agent architectural decisions`
12. `docs: update API documentation and README`

**Final PR**: Closes #62, #64, #65, #66, #67

---

## 🚨 Risk Mitigation

### Risk 1: MCP Server Integration Complexity
**Mitigation**: Test each agent individually with MCP servers before orchestrator integration

### Risk 2: Performance Degradation from Logging
**Mitigation**: Use DEBUG level for detailed logs, INFO only for handoffs and milestones

### Risk 3: Integration Test Flakiness
**Mitigation**: MCPTestHarness with proper health checks and retry logic

### Risk 4: Unclear Agent Handoff Requirements
**Mitigation**: Architecture review completed, patterns documented in ADRs

---

## 📞 Questions & Clarifications

Before proceeding, confirm:
1. ✅ Architecture review approved (explicit orchestration pattern)
2. ✅ MCP tool assignments approved
3. ✅ Logging strategy approved (INFO for handoffs, DEBUG for tools)
4. ✅ Testing approach approved (real MCP servers, no mocks)
5. ✅ One agent per commit for traceability

**Ready to implement? Please confirm plan approval before proceeding.**
