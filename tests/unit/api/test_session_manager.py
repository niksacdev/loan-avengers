"""Tests for session manager."""

from datetime import datetime, timedelta

from loan_avengers.api.session_manager import ConversationSession, SessionManager


class TestConversationSession:
    """Test ConversationSession model."""

    def test_session_creation(self):
        """Test creating a session."""
        session = ConversationSession(session_id="test-123")

        assert session.session_id == "test-123"
        assert session.messages == []
        assert session.application_data == {}
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_activity, datetime)

    def test_session_with_data(self):
        """Test creating session with initial data."""
        app_data = {"applicant_name": "John Doe", "loan_amount": 250000}
        messages = [{"role": "user", "content": "Hello"}]

        session = ConversationSession(
            session_id="test-456",
            application_data=app_data,
            messages=messages,
        )

        assert session.application_data == app_data
        assert session.messages == messages


class TestSessionManager:
    """Test SessionManager functionality."""

    def test_singleton_pattern(self):
        """Test that SessionManager is a singleton."""
        manager1 = SessionManager()
        manager2 = SessionManager()

        assert manager1 is manager2

    def test_create_session(self):
        """Test creating a new session."""
        manager = SessionManager()
        session_id = manager.create_session()

        assert isinstance(session_id, str)
        assert len(session_id) > 0
        assert manager.get_session(session_id) is not None

    def test_get_session(self):
        """Test retrieving an existing session."""
        manager = SessionManager()
        session_id = manager.create_session()

        session = manager.get_session(session_id)

        assert session is not None
        assert session.session_id == session_id

    def test_get_nonexistent_session(self):
        """Test retrieving a session that doesn't exist."""
        manager = SessionManager()
        session = manager.get_session("nonexistent-id")

        assert session is None

    def test_update_session(self):
        """Test updating session data."""
        manager = SessionManager()
        session_id = manager.create_session()

        # Update with new data
        new_data = {"applicant_name": "Jane Smith"}
        manager.update_session(session_id, application_data=new_data)

        session = manager.get_session(session_id)
        assert session.application_data == new_data

    def test_update_session_messages(self):
        """Test updating session messages."""
        manager = SessionManager()
        session_id = manager.create_session()

        # Add a message
        messages = [{"role": "user", "content": "Hi"}]
        manager.update_session(session_id, messages=messages)

        session = manager.get_session(session_id)
        assert len(session.messages) == 1
        assert session.messages[0]["content"] == "Hi"

    def test_update_nonexistent_session(self):
        """Test updating a session that doesn't exist does nothing."""
        manager = SessionManager()
        manager.update_session("nonexistent", application_data={"test": "data"})

        # Should not raise error, just silently fail
        session = manager.get_session("nonexistent")
        assert session is None

    def test_delete_session(self):
        """Test deleting a session."""
        manager = SessionManager()
        session_id = manager.create_session()

        # Verify it exists
        assert manager.get_session(session_id) is not None

        # Delete it
        manager.delete_session(session_id)

        # Verify it's gone
        assert manager.get_session(session_id) is None

    def test_delete_nonexistent_session(self):
        """Test deleting a session that doesn't exist."""
        manager = SessionManager()
        # Should not raise error
        manager.delete_session("nonexistent-id")

    def test_list_sessions(self):
        """Test listing all sessions."""
        manager = SessionManager()

        # Create some sessions
        id1 = manager.create_session()
        id2 = manager.create_session()
        id3 = manager.create_session()

        sessions = manager.list_sessions()

        assert len(sessions) >= 3
        session_ids = [s.session_id for s in sessions]
        assert id1 in session_ids
        assert id2 in session_ids
        assert id3 in session_ids

    def test_cleanup_old_sessions(self):
        """Test cleaning up old sessions."""
        manager = SessionManager()

        # Create a session
        session_id = manager.create_session()
        session = manager.get_session(session_id)

        # Manually set last_activity to old time
        session.last_activity = datetime.now() - timedelta(hours=25)

        # Run cleanup (should remove sessions older than 24 hours)
        manager.cleanup_old_sessions(max_age_hours=24)

        # Session should be deleted
        assert manager.get_session(session_id) is None

    def test_cleanup_preserves_recent_sessions(self):
        """Test that cleanup preserves recent sessions."""
        manager = SessionManager()

        # Create a recent session
        session_id = manager.create_session()

        # Run cleanup
        manager.cleanup_old_sessions(max_age_hours=24)

        # Session should still exist
        assert manager.get_session(session_id) is not None

    def test_session_last_activity_updates(self):
        """Test that updating session updates last_activity."""
        manager = SessionManager()
        session_id = manager.create_session()

        session = manager.get_session(session_id)
        original_activity = session.last_activity

        # Wait a tiny bit
        import time

        time.sleep(0.01)

        # Update session
        manager.update_session(session_id, application_data={"test": "data"})

        session = manager.get_session(session_id)
        # last_activity should be updated
        assert session.last_activity > original_activity
