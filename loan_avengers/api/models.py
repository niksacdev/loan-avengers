"""
API models for the Loan Avengers FastAPI endpoints.

These models define the request/response schemas for the unified
chat API that handles the complete loan application workflow.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ConversationRequest(BaseModel):
    """Request model for unified chat endpoint."""

    user_message: str = Field(..., description="User's message in the conversation")
    session_id: str | None = Field(None, description="Conversation session ID for continuity")
    current_data: dict[str, Any] | None = Field(
        default_factory=dict, description="Currently collected application data"
    )


class ConversationResponse(BaseModel):
    """Response model for unified chat endpoint."""

    agent_name: str = Field(default="System")
    message: str = Field(..., description="Agent's response message")
    action: str = Field(..., description="Current action: collect_info|processing|completed|error")
    collected_data: dict[str, Any] = Field(default_factory=dict, description="Updated application data")
    next_step: str = Field(..., description="Brief description of what happens next")
    completion_percentage: int = Field(..., ge=0, le=100, description="Application completion percentage")
    session_id: str = Field(..., description="Session ID for conversation continuity")


class ProcessingRequest(BaseModel):
    """Request model for starting loan processing workflow."""

    application_data: dict[str, Any] = Field(..., description="Complete application data from coordinator")
    session_id: str = Field(..., description="Session ID from conversation")


class WorkflowEvent(BaseModel):
    """Model for streaming workflow events."""

    agent_name: str = Field(..., description="Name of the agent processing")
    content: str = Field(..., description="Event content/message")
    metadata: dict[str, Any] | None = Field(None, description="Additional event metadata")
    event_type: str = Field(default="agent_update", description="Type of workflow event")


class SessionInfo(BaseModel):
    """Information about an active conversation session."""

    session_id: str = Field(..., description="Unique session identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    last_activity: str = Field(..., description="Last activity timestamp")
    completion_percentage: int = Field(..., ge=0, le=100, description="Application completion percentage")
    collected_data: dict[str, Any] = Field(default_factory=dict, description="Collected application data")
    status: str = Field(default="active", description="Session status: active|completed|processing")
    workflow_phase: str = Field(
        default="collecting", description="Current workflow phase: collecting|validating|assessing|deciding"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    details: str | None = Field(None, description="Additional error details")
    error_code: str | None = Field(None, description="Machine-readable error code")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(default="healthy")
    services: dict[str, str] = Field(default_factory=dict, description="Status of dependent services")
    timestamp: str = Field(..., description="Health check timestamp")
