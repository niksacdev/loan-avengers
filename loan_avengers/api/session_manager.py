"""
Session manager for AgentThread persistence and conversation continuity.

This module handles conversation session state management, AgentThread
persistence, and coordination between coordinator conversations and WorkflowOrchestrator.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from agent_framework import AgentThread
except ImportError:
    from loan_avengers.agents.mock_sequential_workflow import MockAgentThread as AgentThread

from loan_avengers.utils.observability import Observability

logger = Observability.get_logger("session_manager")


class ConversationSession:
    """
    Manages conversation session state for coordinator interactions.

    This class handles:
    - AgentThread persistence across conversation turns
    - Application data accumulation
    - Session lifecycle management
    """

    def __init__(self, session_id: str | None = None):
        """
        Initialize conversation session.

        Args:
            session_id: Optional existing session ID, generates new if None

        Raises:
            ValueError: If provided session_id is not a valid UUID format
        """
        if session_id is not None:
            # Validate session_id is a valid UUID to prevent injection attacks
            try:
                uuid.UUID(session_id)
            except ValueError as e:
                logger.error(
                    "Invalid session_id format provided",
                    extra={"session_id": session_id, "error": str(e)},
                )
                raise ValueError("Invalid session_id format: must be a valid UUID") from e

        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.completion_percentage = 0
        self.collected_data: dict[str, Any] = {}
        self.status = "active"  # active|completed|processing|error
        self.workflow_phase = "collecting"  # collecting|validating|assessing|deciding

        # AgentThread for conversation continuity
        self.agent_thread: AgentThread | None = None

        # State machine for deterministic conversation flow
        self.state_machine: Any = None  # Will be set by orchestrator

        logger.info(
            "ConversationSession created",
            extra={
                "session_id": self.session_id[:8] + "***",
                "created_at": self.created_at.isoformat(),
            },
        )

    def get_or_create_thread(self) -> AgentThread:
        """
        Get existing AgentThread or create new one for conversation continuity.

        Returns:
            AgentThread instance for this session
        """
        if not self.agent_thread:
            self.agent_thread = AgentThread()
            logger.debug(
                "New AgentThread created for session",
                extra={
                    "session_id": self.session_id[:8] + "***",
                    "thread_id": getattr(self.agent_thread, "thread_id", "unknown"),
                },
            )

        return self.agent_thread

    def update_data(self, new_data: dict[str, Any], completion_percentage: int) -> None:
        """
        Update collected application data and completion percentage.

        Args:
            new_data: Updated application data from coordinator
            completion_percentage: Updated completion percentage
        """
        self.collected_data.update(new_data)
        self.completion_percentage = completion_percentage
        self.last_activity = datetime.now(timezone.utc)

        logger.debug(
            "Session data updated",
            extra={
                "session_id": self.session_id[:8] + "***",
                "completion_percentage": completion_percentage,
                "data_keys": list(new_data.keys()),
            },
        )

    def mark_ready_for_processing(self) -> None:
        """Mark session as ready for workflow processing."""
        self.status = "ready_for_processing"
        self.last_activity = datetime.now(timezone.utc)

        logger.info(
            "Session marked ready for processing",
            extra={
                "session_id": self.session_id[:8] + "***",
                "completion_percentage": self.completion_percentage,
            },
        )

    def mark_processing(self) -> None:
        """Mark session as currently being processed by WorkflowOrchestrator."""
        self.status = "processing"
        self.last_activity = datetime.now(timezone.utc)

        logger.info("Session marked as processing", extra={"session_id": self.session_id[:8] + "***"})

    def mark_completed(self) -> None:
        """Mark session as completed."""
        self.status = "completed"
        self.last_activity = datetime.now(timezone.utc)

        logger.info("Session marked as completed", extra={"session_id": self.session_id[:8] + "***"})

    def mark_error(self, error_details: str | None = None) -> None:
        """Mark session as errored."""
        self.status = "error"
        self.last_activity = datetime.now(timezone.utc)

        logger.error(
            "Session marked as error",
            extra={
                "session_id": self.session_id[:8] + "***",
                "error_details": error_details,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary for API responses."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "completion_percentage": self.completion_percentage,
            "collected_data": self.collected_data,
            "status": self.status,
            "workflow_phase": self.workflow_phase,
        }


class SessionManager:
    """
    Global session manager for handling multiple conversation sessions.

    This is a simple in-memory implementation. In production, this would
    use a persistent store like Redis or a database.
    """

    def __init__(self):
        """Initialize session manager."""
        self._sessions: dict[str, ConversationSession] = {}
        logger.info("SessionManager initialized")

    def create_session(self, session_id: str | None = None) -> ConversationSession:
        """
        Create new conversation session.

        Args:
            session_id: Optional session ID, generates new if None

        Returns:
            New ConversationSession instance
        """
        session = ConversationSession(session_id)
        self._sessions[session.session_id] = session

        logger.info(
            "New session created",
            extra={
                "session_id": session.session_id[:8] + "***",
                "total_sessions": len(self._sessions),
            },
        )

        return session

    def get_session(self, session_id: str) -> ConversationSession | None:
        """
        Get existing session by ID.

        Args:
            session_id: Session identifier

        Returns:
            ConversationSession if found, None otherwise
        """
        session = self._sessions.get(session_id)

        if session:
            logger.debug("Session retrieved", extra={"session_id": session_id[:8] + "***"})
        else:
            logger.warning("Session not found", extra={"session_id": session_id[:8] + "***"})

        return session

    def get_or_create_session(self, session_id: str | None = None) -> ConversationSession:
        """
        Get existing session or create new one.

        Args:
            session_id: Optional session ID

        Returns:
            ConversationSession instance
        """
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]

        return self.create_session(session_id)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session by ID.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(
                "Session deleted",
                extra={
                    "session_id": session_id[:8] + "***",
                    "remaining_sessions": len(self._sessions),
                },
            )
            return True

        return False

    def list_sessions(self) -> list[dict[str, Any]]:
        """
        List all active sessions.

        Returns:
            List of session dictionaries
        """
        return [session.to_dict() for session in self._sessions.values()]

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up sessions older than specified age.

        Args:
            max_age_hours: Maximum session age in hours

        Returns:
            Number of sessions cleaned up
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        old_sessions = [
            session_id for session_id, session in self._sessions.items() if session.last_activity < cutoff_time
        ]

        for session_id in old_sessions:
            del self._sessions[session_id]

        logger.info(
            "Session cleanup completed",
            extra={
                "cleaned_sessions": len(old_sessions),
                "remaining_sessions": len(self._sessions),
                "max_age_hours": max_age_hours,
            },
        )

        return len(old_sessions)


# Global session manager instance
session_manager = SessionManager()
