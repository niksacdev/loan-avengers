"""
FastAPI application for the Loan Avengers multi-agent system.

This API provides endpoints for:
- Coordinator conversation handling with AgentThread persistence
- WorkflowOrchestrator integration for loan processing
- Real-time streaming of workflow events
- Session management for conversation continuity
"""

from __future__ import annotations

# Load environment variables FIRST before any other imports
import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    # Load .env from project root directory
    # Path goes from app.py -> api -> loan_avengers -> apps -> api -> root
    env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"[INFO] Loaded environment variables from {env_path}")
    else:
        load_dotenv()  # Fallback to default search
        print("[INFO] Using default .env search")
except ImportError:
    print("[WARN] python-dotenv not installed - environment variables must be set manually")

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# OpenTelemetry auto-instrumentation for Azure Monitor
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    print("[WARN] OpenTelemetry packages not available - observability features limited")

from loan_avengers.api.config import settings
from loan_avengers.api.models import (
    ConversationRequest,
    ConversationResponse,
    HealthResponse,
    ProcessingRequest,
    SessionInfo,
)
from loan_avengers.api.session_manager import session_manager
from loan_avengers.orchestrators.conversation_orchestrator import ConversationOrchestrator
from loan_avengers.orchestrators.sequential_pipeline import SequentialPipeline
from loan_avengers.utils.observability import Observability

# Initialize observability FIRST (before getting logger)
# This sets up agent_framework observability + Application Insights
Observability.initialize()

logger = Observability.get_logger("api")

# Initialize OpenTelemetry with Azure Monitor (if configured)
if OTEL_AVAILABLE and os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(
        # Auto-configure from APPLICATIONINSIGHTS_CONNECTION_STRING env var
        # Also reads OTEL_SERVICE_NAME, OTEL_SERVICE_VERSION, OTEL_RESOURCE_ATTRIBUTES
    )
    logger.info("OpenTelemetry configured with Azure Monitor")
else:
    logger.info("OpenTelemetry not configured - using basic logging only")

# Create FastAPI application with configuration from settings
app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Auto-instrument FastAPI for distributed tracing (if OTEL available)
if OTEL_AVAILABLE:
    FastAPIInstrumentor.instrument_app(
        app,
        # Exclude health/docs endpoints from tracing to reduce noise
        excluded_urls="/health,/docs,/redoc,/openapi.json",
    )
    logger.info("FastAPI auto-instrumentation enabled")

# Configure CORS from environment settings
app.add_middleware(CORSMiddleware, **settings.get_cors_config())

# Initialize conversation orchestrator and sequential processing pipeline
conversation_orchestrator = ConversationOrchestrator()
sequential_pipeline = SequentialPipeline()


# Correlation ID middleware for request tracing
@app.middleware("http")
async def add_correlation_id_middleware(request: Request, call_next):
    """
    Add correlation ID to all requests for end-to-end tracing.

    Correlation IDs enable tracking requests across:
    - HTTP API calls
    - Agent executions
    - MCP server tool calls
    - UI interactions

    The correlation ID is:
    - Extracted from X-Correlation-ID header (if provided by client)
    - Generated as new UUID if not provided
    - Added to response headers
    - Automatically included in all logs via Observability.get_correlation_id()
    - Propagated through OpenTelemetry traces automatically
    """
    # Get or generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = Observability.set_correlation_id()
    else:
        Observability.set_correlation_id(correlation_id)

    logger.debug(
        "Request started",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
        },
    )

    # Process request
    response = await call_next(request)

    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = correlation_id

    # Clear correlation ID after request (prevents leakage between requests)
    Observability.clear_correlation_id()

    return response


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse: Service health status and availability
    """
    return HealthResponse(
        status="healthy",
        services={
            "conversation_orchestrator": "available",
            "sequential_pipeline": "available",
            "session_manager": "available",
            "agent_framework": "available",
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/api/chat", response_model=ConversationResponse)
async def handle_unified_chat(request: ConversationRequest) -> ConversationResponse:
    """
    Handle conversation and processing with direct orchestrator usage.

    Pattern: Code-Based Orchestration
    1. ConversationOrchestrator handles conversation phase
    2. When complete, triggers LoanProcessingPipeline
    3. Returns structured responses

    Flow:
        User → ConversationOrchestrator → Parse/Validate → State Update
        → If complete: Create LoanApplication → LoanProcessingPipeline → Decision

    Args:
        request: ConversationRequest with user message and session ID

    Returns:
        ConversationResponse: Agent response with collected data and next steps

    Raises:
        HTTPException: If processing fails
    """
    try:
        # Get or create conversation session
        session = session_manager.get_or_create_session(request.session_id)

        # Get or create state machine for this session
        if session.state_machine is None:
            from loan_avengers.orchestrators.conversation_state_machine import ConversationStateMachine

            session.state_machine = ConversationStateMachine()
            logger.info(f"Created new state machine for session {session.session_id[:8]}***")

        logger.info(
            "Processing chat request",
            extra={
                "correlation_id": Observability.get_correlation_id(),
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

        # Phase 2: If ready for processing, return to UI to trigger SSE workflow
        if conversation_response.action == "ready_for_processing":
            logger.info(
                "Conversation complete - UI will trigger workflow via SSE", extra={"session_id": session.session_id}
            )
            # Don't run workflow here - let UI call /api/workflow/stream for real-time updates

        # Get the latest response for the API response
        if conversation_responses:
            latest_response = conversation_responses[-1]

            logger.info(
                "Chat processed successfully",
                extra={
                    "correlation_id": Observability.get_correlation_id(),
                    "session_id": session.session_id[:8] + "***",
                    "completion_percentage": latest_response.completion_percentage,
                    "agent": latest_response.agent_name,
                    "collected_data_fields": (
                        list(latest_response.collected_data.keys()) if latest_response.collected_data else []
                    ),
                },
            )

            # Convert from models.responses.ConversationResponse to api.models.ConversationResponse
            # Must explicitly pass collected_data to avoid Pydantic validation issues
            return ConversationResponse(
                agent_name=latest_response.agent_name,
                message=latest_response.message,
                action=latest_response.action,
                collected_data=dict(latest_response.collected_data),  # Explicitly convert to dict
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
                "correlation_id": Observability.get_correlation_id(),
                "session_id": request.session_id[:8] + "***" if request.session_id else "new",
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process chat: {str(e)}"
        ) from e


# Old processing endpoint removed - unified workflow handles entire journey in /api/chat


@app.post("/api/workflow/stream")
async def stream_workflow_processing(request: ProcessingRequest):
    """
    Stream real-time agent updates via Server-Sent Events (SSE).

    This endpoint triggers the SequentialPipeline workflow and streams
    ProcessingUpdate events as each agent completes its assessment.

    Pattern: Server-Sent Events (SSE)
    - Client opens persistent connection
    - Server streams updates in real-time
    - Updates formatted as SSE: "data: {json}\n\n"

    Args:
        request: ProcessingRequest with application_data and session_id

    Returns:
        StreamingResponse: text/event-stream with real-time updates

    Raises:
        HTTPException: If processing fails or session not found

    Example SSE format:
        data: {"agent_name": "Intake_Agent", "message": "...", "phase": "validating", ...}

        data: {"agent_name": "Credit_Assessor", "message": "...", "phase": "assessing_credit", ...}

        data: {"agent_name": "Risk_Analyzer", "message": "...", "phase": "completed", ...}
    """
    try:
        # Get session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {request.session_id} not found")

        # Mark session as processing
        session.mark_processing()

        # Create LoanApplication from collected data using orchestrator
        # (same method as /api/chat endpoint uses)
        application = conversation_orchestrator.create_loan_application(request.application_data)

        logger.info(
            "Starting SSE workflow stream",
            extra={
                "session_id": request.session_id,
                "application_id": application.application_id,
            },
        )

        async def event_generator():
            """Generate SSE events from SequentialPipeline updates."""
            try:
                # Stream processing updates from SequentialPipeline
                async for processing_update in sequential_pipeline.process_application(application):
                    # Update session processing status
                    session.update_processing_status(
                        agent_name=processing_update.agent_name,
                        phase=processing_update.phase,
                        message=processing_update.message,
                        status=processing_update.status,
                    )

                    # Format as SSE event
                    event_data = processing_update.model_dump_json()
                    yield f"data: {event_data}\n\n"

                    logger.debug(
                        "SSE event streamed",
                        extra={
                            "agent": processing_update.agent_name,
                            "phase": processing_update.phase,
                            "status": processing_update.status,
                        },
                    )

                    # Mark session as completed if final update
                    if processing_update.status == "completed":
                        session.mark_completed()

            except Exception as e:
                logger.error(
                    "Error in SSE event generator",
                    extra={"error": str(e), "session_id": request.session_id},
                    exc_info=True,
                )
                # Send error event
                error_event = {
                    "agent_name": "System",
                    "message": f"Processing error: {str(e)}",
                    "phase": "error",
                    "completion_percentage": 0,
                    "status": "error",
                    "assessment_data": {},
                    "metadata": {"error": str(e)},
                }
                yield f"data: {error_event}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to start workflow stream",
            extra={"error": str(e), "session_id": request.session_id},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow stream: {str(e)}",
        ) from e


@app.get("/api/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str) -> SessionInfo:
    """Get information about a conversation session.

    Args:
        session_id: Unique session identifier

    Returns:
        SessionInfo: Session data including collected information and progress

    Raises:
        HTTPException: If session not found
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")

    return SessionInfo(**session.to_dict())


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    """Delete a conversation session.

    Args:
        session_id: Unique session identifier

    Returns:
        dict: Success message

    Raises:
        HTTPException: If session not found
    """
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")

    return {"message": "Session deleted successfully"}


@app.get("/api/sessions")
async def list_sessions() -> dict[str, list[dict]]:
    """List all active conversation sessions.

    Returns:
        dict: Dictionary containing list of session data
    """
    return {"sessions": session_manager.list_sessions()}


@app.post("/api/sessions/cleanup")
async def cleanup_old_sessions(max_age_hours: int = 24) -> dict[str, str]:
    """Clean up old conversation sessions.

    Args:
        max_age_hours: Maximum age in hours before cleanup (default: 24)

    Returns:
        dict: Message with count of cleaned sessions
    """
    cleaned_count = session_manager.cleanup_old_sessions(max_age_hours)
    return {"message": f"Cleaned up {cleaned_count} old sessions"}


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: any, exc: Exception) -> HTTPException:
    """Global exception handler for unhandled errors.

    Args:
        request: FastAPI request object
        exc: Exception that was raised

    Returns:
        HTTPException: 500 Internal Server Error response
    """
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
