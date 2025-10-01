"""
FastAPI application for the Loan Avengers multi-agent system.

This API provides endpoints for:
- Coordinator conversation handling with AgentThread persistence
- WorkflowOrchestrator integration for loan processing
- Real-time streaming of workflow events
- Session management for conversation continuity
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

try:
    from loan_avengers.agents.conversation_orchestrator import ConversationOrchestrator
    from loan_avengers.agents.loan_processing_pipeline import LoanProcessingPipeline

    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    # Use mock implementation when agent_framework is not available
    from loan_avengers.agents.mock_sequential_workflow import LoanProcessingPipeline
    from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow as ConversationOrchestrator

    AGENT_FRAMEWORK_AVAILABLE = False
from loan_avengers.api.models import (
    ConversationRequest,
    ConversationResponse,
    HealthResponse,
    SessionInfo,
)
from loan_avengers.api.session_manager import session_manager
from loan_avengers.utils.observability import Observability

logger = Observability.get_logger("api")

# Create FastAPI application
app = FastAPI(
    title="Loan Avengers API",
    description="Multi-agent loan processing system with conversational interface",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:3000",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize conversation orchestrator and processing pipeline
conversation_orchestrator = ConversationOrchestrator()
processing_pipeline = LoanProcessingPipeline()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        services={
            "conversation_orchestrator": "available",
            "processing_pipeline": "available",
            "session_manager": "available",
            "agent_framework": "available" if AGENT_FRAMEWORK_AVAILABLE else "mock",
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/api/chat", response_model=ConversationResponse)
async def handle_unified_chat(request: ConversationRequest):
    """
    Handle conversation and processing with direct orchestrator usage.

    Pattern: Code-Based Orchestration
    1. ConversationOrchestrator handles conversation phase
    2. When complete, triggers LoanProcessingPipeline
    3. Returns structured responses

    Flow:
        User → ConversationOrchestrator → Parse/Validate → State Update
        → If complete: Create LoanApplication → LoanProcessingPipeline → Decision
    """
    try:
        # Get or create conversation session
        session = session_manager.get_or_create_session(request.session_id)

        # Get or create state machine for this session
        if session.state_machine is None:
            from loan_avengers.agents.conversation_state_machine import ConversationStateMachine

            session.state_machine = ConversationStateMachine()
            logger.info(f"Created new state machine for session {session.session_id[:8]}***")

        logger.info(
            "Processing chat request",
            extra={
                "session_id": session.session_id[:8] + "***",
                "user_message_length": len(request.user_message),
                "existing_data_fields": len(session.collected_data),
                "state_machine_state": session.state_machine.state.value if session.state_machine else "none",
            },
        )

        # Phase 1: Handle conversation through state machine directly
        conversation_responses = []

        # Use the session's state machine
        conversation_response = session.state_machine.process_input(request.user_message)
        conversation_responses.append(conversation_response)

        # Update session with conversation data
        session.update_data(conversation_response.collected_data, conversation_response.completion_percentage)

        # Phase 2: If ready for processing, trigger pipeline
        if conversation_response.action == "ready_for_processing":
            logger.info("Conversation complete, starting processing pipeline")

            # Create LoanApplication from collected data
            application = conversation_orchestrator.create_loan_application(conversation_response.collected_data)

            # Process through automated pipeline (streaming agent updates)
            async for processing_update in processing_pipeline.process_application(application):
                    # Transform processing updates to conversation responses for UI
                    agent_update_response = ConversationResponse(
                        agent_name=processing_update.agent_name,
                        message=processing_update.message,
                        action="processing",
                        collected_data=conversation_response.collected_data,
                        next_step=processing_update.phase,
                        completion_percentage=100,  # Already at 100%, now processing
                        metadata={
                            "processing_phase": processing_update.phase,
                            "agent": processing_update.agent_name,
                        },
                        session_id=session.session_id,
                    )

                    # Append to responses so UI receives all updates
                    conversation_responses.append(agent_update_response)

                    logger.info(
                        "Processing update streamed to UI",
                        extra={
                            "phase": processing_update.phase,
                            "agent": processing_update.agent_name,
                            "message_preview": processing_update.message[:100],
                        },
                    )

                    if processing_update.status == "completed":
                        session.mark_completed()

        # Get the latest response for the API response
        if conversation_responses:
            latest_response = conversation_responses[-1]

            logger.info(
                "Chat processed successfully",
                extra={
                    "session_id": session.session_id[:8] + "***",
                    "completion_percentage": latest_response.completion_percentage,
                    "agent": latest_response.agent_name,
                },
            )

            return ConversationResponse(
                agent_name=latest_response.agent_name,
                message=latest_response.message,
                action=latest_response.action,
                collected_data=latest_response.collected_data,
                next_step=latest_response.next_step,
                completion_percentage=latest_response.completion_percentage,
                quick_replies=latest_response.quick_replies if hasattr(latest_response, "quick_replies") else [],
                session_id=session.session_id,
            )
        else:
            # No responses - return default
            return ConversationResponse(
                agent_name="Cap-ital America",
                message="I'm processing your request. Please wait a moment.",
                action="collect_info",
                collected_data={},
                next_step="Continue providing information",
                completion_percentage=0,
                session_id=session.session_id,
            )

    except Exception as e:
        logger.error(
            "Chat processing failed",
            extra={
                "session_id": request.session_id[:8] + "***" if request.session_id else "new",
                "error": str(e),
            },
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process chat: {str(e)}"
        ) from e


# Old processing endpoint removed - unified workflow handles entire journey in /api/chat


@app.get("/api/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get information about a conversation session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")

    return SessionInfo(**session.to_dict())


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session."""
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")

    return {"message": "Session deleted successfully"}


@app.get("/api/sessions")
async def list_sessions():
    """List all active conversation sessions."""
    return {"sessions": session_manager.list_sessions()}


@app.post("/api/sessions/cleanup")
async def cleanup_old_sessions(max_age_hours: int = 24):
    """Clean up old conversation sessions."""
    cleaned_count = session_manager.cleanup_old_sessions(max_age_hours)
    return {"message": f"Cleaned up {cleaned_count} old sessions"}


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        extra={
            "path": str(request.url),
            "method": request.method,
            "error": str(exc),
        },
        exc_info=True,
    )

    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
