"""Tests for session manager matching actual implementation."""

from datetime import datetime, timedelta, timezone

import pytest

from loan_avengers.api.session_manager import ConversationSession, SessionManager


class TestConversationSessionReal:
    """Test actual ConversationSession implementation."""

    def test_session_init_generates_id(self):
        """Test session generates ID if none provided."""
        session = ConversationSession()

        assert session.session_id is not None
        assert isinstance(session.session_id, str)
        assert len(session.session_id) > 0

    def test_session_init_with_provided_id(self):
        """Test session uses provided ID."""
        import uuid

        valid_uuid = str(uuid.uuid4())
        session = ConversationSession(session_id=valid_uuid)

        assert session.session_id == valid_uuid

    def test_session_has_timestamps(self):
        """Test session has created_at and last_activity."""
        session = ConversationSession()

        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_activity, datetime)
        assert session.created_at <= session.last_activity

    def test_session_initial_state(self):
        """Test session initial state."""
        session = ConversationSession()

        assert session.completion_percentage == 0
        assert session.collected_data == {}
        assert session.status == "active"
        assert session.workflow_phase == "collecting"

    def test_session_get_or_create_thread(self):
        """Test getting or creating agent thread."""
        session = ConversationSession()

        # First call creates thread
        thread1 = session.get_or_create_thread()
        assert thread1 is not None

        # Second call returns same thread
        thread2 = session.get_or_create_thread()
        assert thread2 is thread1

    def test_session_update_data(self):
        """Test updating session data."""
        session = ConversationSession()

        new_data = {"applicant_name": "John Doe", "email": "john@example.com"}
        session.update_data(new_data, 50)

        assert session.collected_data == new_data
        assert session.completion_percentage == 50

    def test_session_update_data_merges(self):
        """Test update_data merges with existing data."""
        session = ConversationSession()

        # First update
        session.update_data({"name": "Alice"}, 25)

        # Second update
        session.update_data({"email": "alice@example.com"}, 50)

        # Should have both fields
        assert "name" in session.collected_data
        assert "email" in session.collected_data

    def test_session_mark_ready_for_processing(self):
        """Test marking session ready for processing."""
        session = ConversationSession()

        session.mark_ready_for_processing()

        assert session.status == "ready_for_processing"

    def test_session_mark_processing(self):
        """Test marking session as processing."""
        session = ConversationSession()

        session.mark_processing()

        assert session.status == "processing"

    def test_session_mark_completed(self):
        """Test marking session as completed."""
        session = ConversationSession()

        session.mark_completed()

        assert session.status == "completed"

    def test_session_mark_error(self):
        """Test marking session with error."""
        session = ConversationSession()

        error_msg = "Test error"
        session.mark_error(error_msg)

        assert session.status == "error"


class TestSessionManagerReal:
    """Test actual SessionManager implementation."""

    def test_manager_get_or_create_new_session(self):
        """Test creating new session when ID is None."""
        manager = SessionManager()

        session = manager.get_or_create_session(None)

        assert session is not None
        assert isinstance(session.session_id, str)

    def test_manager_get_existing_session(self):
        """Test getting existing session."""
        manager = SessionManager()

        # Create session
        session1 = manager.get_or_create_session(None)
        session_id = session1.session_id

        # Get same session
        session2 = manager.get_or_create_session(session_id)

        assert session2.session_id == session_id

    def test_manager_creates_new_session_for_nonexistent_id(self):
        """Test creates new session if ID doesn't exist."""
        import uuid

        manager = SessionManager()

        nonexistent_uuid = str(uuid.uuid4())
        session = manager.get_or_create_session(nonexistent_uuid)

        # Should create new session with the provided ID
        assert session is not None
        assert session.session_id == nonexistent_uuid

    def test_manager_list_sessions(self):
        """Test listing all sessions."""
        manager = SessionManager()

        # Create some sessions
        manager.get_or_create_session(None)
        manager.get_or_create_session(None)

        sessions = manager.list_sessions()

        assert len(sessions) >= 2
        # list_sessions returns dicts not objects
        assert isinstance(sessions, list)

    def test_manager_get_session_by_id(self):
        """Test getting session by ID."""
        manager = SessionManager()

        # Create session
        created_session = manager.get_or_create_session(None)

        # Get by ID
        retrieved_session = manager.get_session(created_session.session_id)

        assert retrieved_session is not None
        assert retrieved_session.session_id == created_session.session_id

    def test_manager_get_nonexistent_session_returns_none(self):
        """Test getting nonexistent session returns None."""
        manager = SessionManager()

        session = manager.get_session("definitely-does-not-exist")

        assert session is None

    def test_manager_delete_session(self):
        """Test deleting session."""
        manager = SessionManager()

        # Create session
        session = manager.get_or_create_session(None)
        session_id = session.session_id

        # Delete it
        manager.delete_session(session_id)

        # Should no longer exist
        retrieved = manager.get_session(session_id)
        assert retrieved is None

    def test_manager_delete_nonexistent_session_no_error(self):
        """Test deleting nonexistent session doesn't error."""
        manager = SessionManager()

        # Should not raise
        manager.delete_session("nonexistent-delete-123")

    def test_manager_cleanup_old_sessions(self):
        """Test cleanup removes old sessions."""
        manager = SessionManager()

        # Create session
        session = manager.get_or_create_session(None)
        session_id = session.session_id

        # Manually make it old
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        session.last_activity = old_time

        # Cleanup with 24 hour max age
        removed_count = manager.cleanup_old_sessions(max_age_hours=24)

        # Should have removed at least one
        assert removed_count >= 1

        # Session should be gone
        retrieved = manager.get_session(session_id)
        assert retrieved is None

    def test_manager_cleanup_preserves_recent_sessions(self):
        """Test cleanup doesn't remove recent sessions."""
        manager = SessionManager()

        # Create recent session
        session = manager.get_or_create_session(None)
        session_id = session.session_id

        # Cleanup
        manager.cleanup_old_sessions(max_age_hours=24)

        # Session should still exist
        retrieved = manager.get_session(session_id)
        assert retrieved is not None

    def test_manager_update_session_last_activity(self):
        """Test that operations update last_activity."""
        manager = SessionManager()

        session = manager.get_or_create_session(None)
        original_time = session.last_activity

        import time

        time.sleep(0.01)

        # Update data
        session.update_data({"test": "data"}, 10)

        # last_activity should be updated
        assert session.last_activity > original_time

    def test_manager_multiple_sessions_independent(self):
        """Test multiple sessions are independent."""
        manager = SessionManager()

        session1 = manager.get_or_create_session(None)
        session2 = manager.get_or_create_session(None)

        # Update one
        session1.update_data({"name": "Alice"}, 50)

        # Other should be unaffected
        assert session2.collected_data == {}
        assert session2.completion_percentage == 0

    def test_manager_session_workflow_phases(self):
        """Test session workflow phase tracking."""
        manager = SessionManager()

        session = manager.get_or_create_session(None)

        # Start in collecting
        assert session.workflow_phase == "collecting"

        # Update phase
        session.workflow_phase = "validating"
        assert session.workflow_phase == "validating"

        session.workflow_phase = "processing"
        assert session.workflow_phase == "processing"


class TestConversationSessionSecurity:
    """Test security validation in ConversationSession."""

    def test_invalid_session_id_raises_error(self):
        """Test that invalid session_id format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid session_id format"):
            ConversationSession(session_id="not-a-valid-uuid")

    def test_injection_attempt_blocked(self):
        """Test that injection attempts are blocked."""
        malicious_ids = [
            "'; DROP TABLE sessions; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "malicious-id-123",
        ]

        for bad_id in malicious_ids:
            with pytest.raises(ValueError, match="Invalid session_id format"):
                ConversationSession(session_id=bad_id)

    def test_valid_uuid_accepted(self):
        """Test that valid UUID format is accepted."""
        import uuid

        valid_uuid = str(uuid.uuid4())
        session = ConversationSession(session_id=valid_uuid)

        assert session.session_id == valid_uuid

    def test_none_session_id_generates_uuid(self):
        """Test that None session_id generates valid UUID."""
        session = ConversationSession(session_id=None)

        # Should be a valid UUID
        import uuid

        uuid.UUID(session.session_id)  # Raises ValueError if invalid
