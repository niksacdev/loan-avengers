# Tasks: UI Integration Coordinator Agent

**Input**: Design documents from `docs/` and current codebase analysis
**Prerequisites**: API architecture (✅), data models (✅), technical specification (✅), UI foundation (✅)

## Current Feature Branch Context
Branch: `feat/ui-integration-riley-agent`

Based on analysis of the existing codebase and documentation, this feature focuses on:
1. Integrating the Cap-ital America decision coordinator agent with the UI
2. Implementing real-time streaming workflow updates
3. Creating conversational UI components for agent interactions
4. Establishing the complete UI-to-agent pipeline

## Execution Flow (main)
```
1. Load API architecture and endpoints specification
   → Streamable HTTP endpoint for real-time events
   → Chat API for conversational interactions
   → Agent workflow orchestration patterns
2. Analyze current implementation:
   → API layer: `/loan_avengers/api/` (exists)
   → UI foundation: `/loan_avengers/ui/src/` (exists)
   → Agent framework: `/loan_avengers/agents/` (exists)
   → Cap-ital America coordinator: `/loan_avengers/agents/riley_coordinator.py` (exists)
3. Generate tasks by category:
   → API Integration: Complete streaming endpoints
   → Real-time UI: WebSocket/SSE components
   → Agent Integration: Cap-ital America coordinator workflow
   → Chat Interface: Conversational components
   → Testing: End-to-end integration tests
4. Apply task rules:
   → API and UI components can run in parallel [P]
   → Sequential agent integration dependencies
   → Tests require working implementations
5. Number tasks sequentially (T001, T002...)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- All paths are absolute from repository root

## Phase 1: API Integration Foundation

- [ ] T001 [P] Complete FastAPI streaming endpoint implementation in `/workspaces/loan-avengers/loan_avengers/api/streaming.py`
- [ ] T002 [P] Implement chat message handling in `/workspaces/loan-avengers/loan_avengers/api/chat.py`
- [ ] T003 [P] Add application status endpoints in `/workspaces/loan-avengers/loan_avengers/api/applications.py`
- [ ] T004 Create unified API router in `/workspaces/loan-avengers/loan_avengers/api/main.py`

## Phase 2: Real-Time UI Components ⚠️ REQUIRES Phase 1 Complete

- [ ] T005 [P] Create WebSocket/SSE client service in `/workspaces/loan-avengers/loan_avengers/ui/src/services/streaming.ts`
- [ ] T006 [P] Implement agent progress components in `/workspaces/loan-avengers/loan_avengers/ui/src/components/agent-progress/`
- [ ] T007 [P] Create chat interface components in `/workspaces/loan-avengers/loan_avengers/ui/src/components/chat/ChatInterface.tsx`
- [ ] T008 [P] Build real-time status updates in `/workspaces/loan-avengers/loan_avengers/ui/src/components/status/LiveStatus.tsx`

## Phase 3: Cap-ital America Agent Integration

- [ ] T009 Complete Cap-ital America coordinator persona in `/workspaces/loan-avengers/loan_avengers/agents/agent-persona/riley-coordinator-persona.md`
- [ ] T010 Integrate Cap-ital America with unified workflow in `/workspaces/loan-avengers/loan_avengers/agents/unified_workflow.py`
- [ ] T011 Connect Cap-ital America to streaming API in `/workspaces/loan-avengers/loan_avengers/api/agent_handlers.py`
- [ ] T012 Add celebration and decision delivery to Cap-ital America responses

## Phase 4: Conversational UI Pipeline

- [ ] T013 Implement conversational data collection in `/workspaces/loan-avengers/loan_avengers/ui/src/pages/application/ConversationalForm.tsx`
- [ ] T014 Create agent handoff animations in `/workspaces/loan-avengers/loan_avengers/ui/src/components/animations/AgentTransitions.tsx`
- [ ] T015 Build celebration components in `/workspaces/loan-avengers/loan_avengers/ui/src/components/celebration/SuccessAnimation.tsx`
- [ ] T016 Integrate voice input handling in `/workspaces/loan-avengers/loan_avengers/ui/src/components/voice/VoiceInput.tsx`

## Phase 5: Integration & State Management

- [ ] T017 Create application state management in `/workspaces/loan-avengers/loan_avengers/ui/src/store/applicationStore.ts`
- [ ] T018 Implement agent thread persistence in `/workspaces/loan-avengers/loan_avengers/api/persistence/thread_store.py`
- [ ] T019 Add error handling and recovery in `/workspaces/loan-avengers/loan_avengers/ui/src/services/errorHandling.ts`
- [ ] T020 Connect UI routing to agent workflow states in `/workspaces/loan-avengers/loan_avengers/ui/src/routing/workflowRoutes.tsx`

## Phase 6: Testing & Polish

- [ ] T021 [P] Write API integration tests in `/workspaces/loan-avengers/tests/api/test_streaming_integration.py`
- [ ] T022 [P] Create UI component tests in `/workspaces/loan-avengers/tests/ui/components/test_chat_interface.spec.ts`
- [ ] T023 [P] Build end-to-end workflow tests in `/workspaces/loan-avengers/tests/e2e/test_riley_integration.py`
- [ ] T024 [P] Add performance tests for streaming in `/workspaces/loan-avengers/tests/performance/test_stream_latency.py`
- [ ] T025 Update API documentation in `/workspaces/loan-avengers/docs/api/api-endpoints.md`

## Dependencies

**Phase Dependencies**:
- Phase 2 (T005-T008) requires Phase 1 (T001-T004) complete
- Phase 3 (T009-T012) can run parallel with Phase 2
- Phase 4 (T013-T016) requires Phase 2 and Phase 3 complete
- Phase 5 (T017-T020) requires Phase 4 complete
- Phase 6 (T021-T025) requires working implementation

**Task Dependencies**:
- T004 requires T001, T002, T003 (API router needs endpoints)
- T010 requires T009 (unified workflow needs Cap-ital America persona)
- T011 requires T010 (API handlers need unified workflow)
- T013 requires T007 (conversational form needs chat interface)
- T017 requires T008 (state management needs status components)
- T018 requires T011 (persistence needs API handlers)

## Parallel Execution Examples

```bash
# Phase 1: API Foundation (can run together)
Task: "Complete FastAPI streaming endpoint in /workspaces/loan-avengers/loan_avengers/api/streaming.py"
Task: "Implement chat message handling in /workspaces/loan-avengers/loan_avengers/api/chat.py"
Task: "Add application status endpoints in /workspaces/loan-avengers/loan_avengers/api/applications.py"

# Phase 2: UI Components (can run together after Phase 1)
Task: "Create WebSocket/SSE client in /workspaces/loan-avengers/loan_avengers/ui/src/services/streaming.ts"
Task: "Implement agent progress components in /workspaces/loan-avengers/loan_avengers/ui/src/components/agent-progress/"
Task: "Create chat interface in /workspaces/loan-avengers/loan_avengers/ui/src/components/chat/ChatInterface.tsx"

# Phase 6: Testing (can run together after implementation)
Task: "Write API integration tests in /workspaces/loan-avengers/tests/api/test_streaming_integration.py"
Task: "Create UI component tests in /workspaces/loan-avengers/tests/ui/components/test_chat_interface.spec.ts"
Task: "Build end-to-end tests in /workspaces/loan-avengers/tests/e2e/test_riley_integration.py"
```

## Implementation Notes

### Current State Analysis
- ✅ **API Architecture**: Complete design documents
- ✅ **UI Foundation**: React/TypeScript base structure exists
- ✅ **Agent Framework**: Microsoft Agent Framework integration
- ✅ **Cap-ital America Agent**: Basic implementation exists
- 🔄 **Streaming**: Partial implementation, needs completion
- ❌ **Chat UI**: Missing conversational components
- ❌ **Real-time Updates**: Missing WebSocket/SSE integration

### Key Technology Stack
- **Backend**: FastAPI + Microsoft Agent Framework + Azure services
- **Frontend**: React + TypeScript + Framer Motion (animations)
- **Real-time**: WebSocket/Server-Sent Events
- **State**: React Context/Zustand for application state
- **Testing**: Pytest (backend) + Jest/Playwright (frontend)

### Success Criteria
- Cap-ital America agent delivers loan decisions with celebration UI
- Real-time streaming updates from all agents to UI
- Conversational form replaces traditional static forms
- Agent handoffs are smooth with visual transitions
- Voice input works for mobile-first experience
- Complete end-to-end loan application workflow

## Validation Checklist
*GATE: Checked before marking feature complete*

- [ ] All API endpoints stream real-time events
- [ ] UI components update live during agent processing
- [ ] Cap-ital America agent integration delivers final decisions
- [ ] Chat interface handles conversational data collection
- [ ] Error handling gracefully manages failures
- [ ] Performance meets latency targets (<2s agent responses)
- [ ] Mobile-first experience with voice input
- [ ] Celebrations and animations enhance user experience

## Notes

### Architecture Decision Context
This feature integrates the final piece of the "Dream Team" conversational experience:
- **Alisha (UI Concierge)**: Pure UI personality, not an agent
- **Agent Chain**: Intake Agent (Intake) → Hawk-Income (Income) → Scarlet Witch-Credit (Credit) → Doctor Strange-Risk (Risk) → **Cap-ital America (Decision)**
- **Cap-ital America's Role**: Celebratory decision delivery with maximum user engagement

### Implementation Priority
1. **Core Function**: Agent workflow must complete successfully
2. **User Experience**: Conversational interface with real-time updates
3. **Polish**: Animations, celebrations, voice input
4. **Performance**: Sub-2 second response times

### Future Extensions
- Multi-language support for agent personalities
- Advanced celebration animations based on loan amount
- Integration with additional MCP servers
- Enhanced error recovery and graceful degradation