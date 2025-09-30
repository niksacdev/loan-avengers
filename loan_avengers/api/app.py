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
    from agent_framework import AgentThread, SharedState

    from loan_avengers.agents.sequential_workflow import SequentialLoanWorkflow

    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    # Use mock implementation when agent_framework is not available
    from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow as SequentialLoanWorkflow
    from loan_avengers.agents.mock_sequential_workflow import MockSharedState as SharedState

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
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5175"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize unified workflow
sequential_workflow = SequentialLoanWorkflow()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        services={
            "sequential_workflow": "available",
            "session_manager": "available",
            "agent_framework": "available" if AGENT_FRAMEWORK_AVAILABLE else "mock",
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/api/chat", response_model=ConversationResponse)
async def handle_unified_chat(request: ConversationRequest):
    """
    Handle unified chat workflow with AgentThread and SharedState.

    This endpoint manages the entire loan application journey through
    a single continuous workflow using Microsoft Agent Framework:
    1. Gets or creates session with AgentThread
    2. Uses SharedState for application data sharing
    3. Processes through unified workflow (collection → processing → decision)
    4. Returns streaming workflow responses
    """
    try:
        # Get or create conversation session
        session = session_manager.get_or_create_session(request.session_id)

        # Get AgentThread for conversation continuity
        agent_thread = session.get_or_create_thread()

        # Create SharedState for workflow data sharing with existing collected data
        shared_state = SharedState()
        await shared_state.set("application_data", session.collected_data)

        logger.info(
            "Processing unified chat request",
            extra={
                "session_id": session.session_id[:8] + "***",
                "user_message_length": len(request.user_message),
                "workflow_phase": getattr(session, "workflow_phase", "collecting"),
                "existing_data_fields": len(session.collected_data),
            },
        )

        # Process through unified workflow
        # This handles both collection and processing in one continuous flow
        workflow_responses = []
        async for workflow_response in sequential_workflow.process_conversation(
            user_message=request.user_message, thread=agent_thread, shared_state=shared_state
        ):
            workflow_responses.append(workflow_response)

        # Get the latest response for the API response
        if workflow_responses:
            latest_response = workflow_responses[-1]

            # Update session with workflow data
            session.update_data(latest_response.collected_data, latest_response.completion_percentage)

            # Update workflow phase tracking
            session.workflow_phase = latest_response.phase

            # Check if workflow is completed
            if latest_response.action == "completed":
                session.mark_completed()

            logger.info(
                "Unified chat processed successfully",
                extra={
                    "session_id": session.session_id[:8] + "***",
                    "phase": latest_response.phase,
                    "completion_percentage": latest_response.completion_percentage,
                    "agent": latest_response.agent_name,
                },
            )

            return ConversationResponse(
                agent_name=latest_response.agent_name,
                message=latest_response.message,
                action=latest_response.action,
                collected_data=latest_response.collected_data,
                next_step=f"Continue in {latest_response.phase} phase",
                completion_percentage=latest_response.completion_percentage,
                session_id=session.session_id,
            )
        else:
            # No responses - return default
            return ConversationResponse(
                agent_name="System",
                message="I'm processing your request. Please wait a moment.",
                action="processing",
                collected_data={},
                next_step="Continuing workflow",
                completion_percentage=0,
                session_id=session.session_id,
            )

    except Exception as e:
        logger.error(
            "Unified chat processing failed",
            extra={
                "session_id": request.session_id[:8] + "***" if request.session_id else "new",
                "error": str(e),
            },
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process chat: {str(e)}"
        )


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
