# ADR-011: Two-Endpoint API Architecture for Collection and Processing

**Status**: Recommended
**Date**: 2025-09-29
**Decision Makers**: System Architect, Development Team
**Supersedes**: Unified workflow approach (rejected in ADR-010)

---

## Context

Following the comprehensive assessment in ADR-010, we identified that the `unified_workflow.py` approach fundamentally violated established architectural principles (ADR-004, ADR-006, ADR-007) by conflating conversational data collection with formal loan processing.

### The Problem

The system requires two distinct capabilities:

1. **Conversational Data Collection**: Cap-ital America gathers loan application information through natural language conversation (iterative, conversational, partial data)
2. **Formal Loan Processing**: WorkflowOrchestrator executes business logic through sequential agent workflow (one-shot, analytical, complete validated data)

Attempting to unify these into a single workflow violated separation of concerns and misused the Microsoft Agent Framework's SequentialBuilder.

### Requirements

- **Phase Separation**: Clear distinction between collection and processing
- **Type Safety**: Validated data models at transition points
- **ADR Compliance**: Follow dual-layer architecture (ADR-004)
- **Framework Alignment**: Proper use of Microsoft Agent Framework patterns
- **User Experience**: Clear UI transitions between phases
- **State Management**: Single source of truth, no duplication

---

## Decision

Implement a **two-endpoint API architecture** with complete separation of concerns:

### Endpoint 1: POST /api/chat
- **Purpose**: Conversational data collection with Cap-ital America
- **Input**: User message (string) + optional session ID
- **Output**: Cap-ital America response with collected data and completion percentage
- **Pattern**: Iterative (multiple requests until complete)
- **Agent**: RileyCoordinator only
- **State**: Accumulates in `session.collected_data`

### Endpoint 2: POST /api/process
- **Purpose**: Formal loan processing through WorkflowOrchestrator
- **Input**: Session ID containing complete application data
- **Output**: Server-Sent Events (SSE) stream of workflow progress
- **Pattern**: One-shot (single request, streams to completion)
- **Agent**: WorkflowOrchestrator with sequential agents (Intake → Credit → Income → Risk)
- **State**: Creates validated LoanApplication, produces LoanDecision

### Transition Point
Validation gateway between phases using `RileyCoordinator.create_loan_application()`:
```python
# Phase 1: Collection (Dict[str, Any])
collected_data = riley.process_conversation(user_message, thread, current_data)

# Validation Gateway: Raises ValueError if invalid
application = riley.create_loan_application(collected_data)

# Phase 2: Processing (LoanApplication → LoanDecision)
decision = workflow.process_loan_application(application)
```

---

## Architecture

### Sequence Flow

```
User → Frontend → /api/chat → RileyCoordinator
                    ↓ (multiple iterations)
            collected_data (100% complete)
                    ↓
         riley.create_loan_application()
                    ↓
       LoanApplication (validated Pydantic)
                    ↓
Frontend → /api/process → WorkflowOrchestrator
                    ↓ (SSE streaming)
          Intake → Credit → Income → Risk
                    ↓
            LoanDecision (final)
                    ↓
             Frontend → User
```

### Component Separation

**Collection Layer** (Cap-ital America):
- Temperature: 0.7 (conversational)
- No MCP tools
- Iterative conversation
- Works with partial data
- Output: Dict[str, Any]

**Processing Layer** (WorkflowOrchestrator):
- Temperature: 0.1-0.2 (analytical)
- MCP tools enabled
- One-shot workflow
- Requires complete validated data
- Output: LoanDecision

### State Management

Single source of truth: `ConversationSession`

```python
class ConversationSession:
    # Collection phase state
    collected_data: Dict[str, Any]
    completion_percentage: int
    collection_status: Literal["active", "complete"]

    # Processing phase state
    processing_status: Literal["pending", "ready", "processing", "completed", "error"]
    application: LoanApplication | None
    decision: LoanDecision | None

    # Framework integration
    _agent_thread: AgentThread | None
```

**No SharedState duplication**: Session is the only state store for application data.

---

## Alternatives Considered

### Alternative 1: Single Unified Endpoint
**Rejected**: Cannot distinguish between collection and processing phases, leads to ambiguous workflow state, violates ADR-004.

### Alternative 2: Three-Endpoint Pattern (Chat, Validate, Process)
**Rejected**: Validation is implicit in LoanApplication creation, adding explicit endpoint adds unnecessary complexity.

### Alternative 3: WebSockets Instead of SSE
**Rejected**: SSE is simpler for unidirectional streaming (server→client), WebSockets are overkill.

### Alternative 4: Synchronous Processing Endpoint
**Rejected**: Workflow can take 30-60 seconds, synchronous requests would timeout. SSE provides real-time feedback.

---

## Consequences

### Positive

1. **Architectural Compliance**
   - ✅ Follows ADR-004 dual-layer architecture
   - ✅ Follows ADR-006 sequential orchestration correctly
   - ✅ Follows ADR-007 conversation state management

2. **Separation of Concerns**
   - Cap-ital America handles only conversation (Layer 2: Personality)
   - WorkflowOrchestrator handles only processing (Layer 1: Technical)
   - Clear boundaries, independent testing

3. **Type Safety**
   - Strict progression: string → Dict → LoanApplication → LoanDecision
   - Pydantic validation at transition points
   - Compilation catches type errors

4. **Framework Alignment**
   - SequentialBuilder used correctly (homogeneous technical agents)
   - Cap-ital America not forced into sequential workflow
   - Agent responsibilities clear

5. **User Experience**
   - Clear visual separation between phases
   - Progress tracking appropriate to each phase
   - User controls transition (submits when ready)

6. **Testability**
   - Each endpoint testable independently
   - Collection logic separate from processing logic
   - Mock implementations simpler

7. **Scalability**
   - Collection and processing can scale independently
   - SSE streaming handles long-running workflows
   - Session state enables horizontal scaling (with Redis)

### Negative

1. **Two Endpoints to Maintain**
   - More API surface area
   - Two sets of tests
   - Mitigation: Clear documentation, shared utilities

2. **Frontend Complexity**
   - Frontend must manage phase transitions
   - Mitigation: Clear UX patterns, state machine

3. **Session Management Required**
   - Must persist session state between endpoints
   - Mitigation: Use SessionManager, plan for Redis in production

4. **Validation Error Handling**
   - Must handle case where Cap-ital America says "ready" but validation fails
   - Mitigation: Return user to collection with specific error messages

### Risks

1. **Session Expiration During Collection**
   - Risk: Long conversation, session expires
   - Mitigation: Activity-based expiration renewal, 30-minute timeout, heartbeat endpoint

2. **Network Failure During Processing**
   - Risk: SSE connection drops mid-workflow
   - Mitigation: Session stores progress, frontend can reconnect and check status

3. **Validation Misalignment**
   - Risk: Cap-ital America's completion logic differs from Pydantic validation
   - Mitigation: Comprehensive testing, improve Cap-ital America's prompts based on validation failures

---

## Implementation

### Phase 1: API Refactoring (Week 1)

**Priority 1: Update /api/chat endpoint**
```python
@app.post("/api/chat", response_model=ConversationResponse)
async def handle_chat(request: ConversationRequest):
    session = session_manager.get_or_create_session(request.session_id)
    riley = RileyCoordinator()

    response = await riley.process_conversation(
        user_message=request.user_message,
        thread=session.get_or_create_thread(),
        current_data=session.collected_data
    )

    session.update_data(
        response.assessment.collected_data,
        response.assessment.completion_percentage
    )

    if response.assessment.action == "ready_for_processing":
        session.mark_ready_for_processing()

    return ConversationResponse(...)
```

**Priority 2: Create /api/process endpoint**
```python
@app.post("/api/process")
async def handle_processing(request: ProcessingRequest):
    async def event_generator():
        session = session_manager.get_session(request.session_id)
        # Validate session ready
        # Create LoanApplication
        # Stream WorkflowOrchestrator events
        yield f"event: agent_update\ndata: {json.dumps(...)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Priority 3: Update ConversationSession**
```python
class ConversationSession:
    collection_status: Literal["active", "complete"]
    processing_status: Literal["pending", "ready", "processing", "completed", "error"]

    @property
    def status(self) -> str:
        # Compute overall status from phase-specific states
        ...
```

### Phase 2: Frontend Updates (Week 1-2)

**Update Cap-ital America chat component**:
- Detect `action: "ready_for_processing"`
- Emit `onReadyForProcessing` callback
- Show application review and submit button

**Create processing view component**:
- SSE connection to `/api/process`
- Display agent progress in real-time
- Show final decision

**Update app state machine**:
- Phases: collection → transition → processing → complete
- Clear UI for each phase

### Phase 3: WorkflowOrchestrator Enhancement (Week 2-3)

**Expand from MVP to full workflow**:
- Add Credit agent executor
- Add Income agent executor
- Add Risk agent executor
- Build SequentialBuilder with all agents

**Add event metadata**:
- event_type: agent_update | phase_transition | final_decision | error
- step, phase, status fields
- Full decision object in final_decision event

### Phase 4: Testing (Week 3)

- Unit tests for each endpoint
- Integration tests for full flow
- SSE streaming tests
- Session state transition tests
- Validation error handling tests

---

## Compliance Verification

### ADR-004: Dual-Layer Architecture
✅ **Compliant**: Cap-ital America (Layer 2: Personality) separate from WorkflowOrchestrator (Layer 1: Technical)

### ADR-006: Sequential Workflow Orchestration
✅ **Compliant**: SequentialBuilder used only for homogeneous technical agents in WorkflowOrchestrator

### ADR-007: Conversation State with AgentThread
✅ **Compliant**: AgentThread provides conversation context, ConversationSession stores business state

### Microsoft Agent Framework Best Practices
✅ **Compliant**: Correct use of SequentialBuilder, AgentThread, and streaming patterns

---

## Success Metrics

### Technical Metrics
- [ ] /api/chat response time <2s (p95)
- [ ] /api/process workflow completion <60s (p95)
- [ ] Session state consistency 100%
- [ ] Zero SharedState usage for application data
- [ ] Test coverage ≥85% on core flows

### User Experience Metrics
- [ ] Clear phase identification 100% of users
- [ ] Validation error rate <5% (indicates Cap-ital America collection quality)
- [ ] Processing completion rate >95%
- [ ] SSE connection stability >99%

### Operational Metrics
- [ ] API uptime 99.9%
- [ ] Session cleanup working (no memory leaks)
- [ ] Logging and metrics comprehensive
- [ ] Error handling graceful

---

## Migration Plan

### Immediate Actions (Day 1)
1. ✅ Archive `unified_workflow.py` and `mock_unified_workflow.py`
2. Document rejection in ADR-010
3. Create ADR-011 (this document)

### Week 1: Core Implementation
1. Refactor /api/chat endpoint
2. Create /api/process endpoint
3. Update ConversationSession
4. Update frontend components

### Week 2: Enhancement
1. Expand WorkflowOrchestrator
2. Add comprehensive tests
3. Performance optimization

### Week 3: Documentation and Rollout
1. Update all documentation
2. Deploy to staging
3. QA testing
4. Production deployment with monitoring

---

## References

- **ADR-004**: Personality-Driven Agent Architecture
- **ADR-005**: API Architecture with Agent Framework
- **ADR-006**: Sequential Workflow Orchestration
- **ADR-007**: Conversation State with AgentThread
- **ADR-010**: Unified Workflow Architecture Assessment (rejection)
- **Full Design Document**: `/workspaces/loan-avengers/docs/architecture/correct-two-endpoint-architecture.md`

---

## Decision

**Recommendation**: **ACCEPT** this two-endpoint architecture.

**Rationale**:
- Architecturally sound
- ADR compliant
- Framework aligned
- Testable and maintainable
- Scales independently
- Clear user experience

**Implementation**: Begin Week 1 implementation following the checklist.

---

## Approval

**System Architect**: ✅ Recommended
**Development Team**: [Pending Review]
**Product Manager**: [Pending Review]

**Status**: Recommended for Implementation
**Target Start Date**: 2025-09-30

---

**End of Architecture Decision Record**