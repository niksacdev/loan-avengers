"""
End-to-end API tests for the complete loan processing workflow.

Tests the full stack from HTTP API → ConversationOrchestrator → SequentialPipeline → Agents
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from loan_defenders.api.app import app
from tests.fixtures.mcp_test_harness import MCPTestHarness


@pytest.fixture
def client():
    """Provide FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mcp_harness():
    """Provide MCP test harness for E2E tests."""
    harness = MCPTestHarness()
    yield harness
    harness.reset_all()


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test that health endpoint returns correct status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "services" in data
        assert data["services"]["conversation_orchestrator"] == "available"
        assert data["services"]["sequential_pipeline"] == "available"
        assert data["services"]["session_manager"] == "available"
        assert data["services"]["agent_framework"] == "available"


class TestConversationFlow:
    """Test conversation flow through state machine."""

    def test_initial_greeting(self, client):
        """Test initial conversation greeting."""
        response = client.post(
            "/api/chat",
            json={
                "user_message": "",  # Empty message triggers initial state
                "session_id": None,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["agent_name"] == "Cap-ital America"
        assert "session_id" in data
        assert data["completion_percentage"] == 0
        assert data["action"] == "collect_info"
        assert len(data["quick_replies"]) > 0

    def test_home_price_selection(self, client):
        """Test home price selection step."""
        response = client.post(
            "/api/chat",
            json={
                "user_message": "300000",  # Select $200K-$400K range
                "session_id": None,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["completion_percentage"] == 25
        assert "down payment" in data["message"].lower()
        assert len(data["quick_replies"]) > 0  # Down payment options

    def test_down_payment_selection(self, client):
        """Test down payment selection step."""
        # First, set home price
        response1 = client.post(
            "/api/chat",
            json={"user_message": "300000", "session_id": None},
        )
        session_id = response1.json()["session_id"]

        # Then, set down payment
        response2 = client.post(
            "/api/chat",
            json={
                "user_message": "20",  # 20% down
                "session_id": session_id,
            },
        )

        assert response2.status_code == 200
        data = response2.json()

        assert data["completion_percentage"] == 50
        assert "income" in data["message"].lower()

    def test_income_selection(self, client):
        """Test income selection step."""
        # Step through previous selections
        r1 = client.post("/api/chat", json={"user_message": "300000", "session_id": None})
        session_id = r1.json()["session_id"]

        client.post("/api/chat", json={"user_message": "20", "session_id": session_id})

        # Select income
        response = client.post(
            "/api/chat",
            json={
                "user_message": "175000",  # $100K-$250K range
                "session_id": session_id,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["completion_percentage"] == 75
        assert "personal" in data["message"].lower()

    def test_personal_info_submission(self, client):
        """Test personal info form submission."""
        import json as json_module

        # Step through all previous selections
        r1 = client.post("/api/chat", json={"user_message": "300000", "session_id": None})
        session_id = r1.json()["session_id"]

        client.post("/api/chat", json={"user_message": "20", "session_id": session_id})
        client.post("/api/chat", json={"user_message": "175000", "session_id": session_id})

        # Submit personal info
        personal_info = {"name": "Tony Stark", "email": "tony@starkindustries.com", "idLast4": "1234"}

        response = client.post(
            "/api/chat",
            json={
                "user_message": json_module.dumps(personal_info),
                "session_id": session_id,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["completion_percentage"] == 100
        assert data["action"] == "ready_for_processing"
        assert "DEFENDERS" in data["message"]


class TestSessionManagement:
    """Test session management endpoints."""

    def test_session_creation_and_retrieval(self, client):
        """Test that sessions are created and can be retrieved."""
        # Create session via chat
        response = client.post(
            "/api/chat",
            json={"user_message": "300000", "session_id": None},
        )

        session_id = response.json()["session_id"]
        assert session_id is not None

        # Retrieve session
        session_response = client.get(f"/api/sessions/{session_id}")
        assert session_response.status_code == 200

        session_data = session_response.json()
        assert session_data["session_id"] == session_id
        assert session_data["completion_percentage"] == 25

    def test_session_deletion(self, client):
        """Test session deletion."""
        # Create session
        response = client.post(
            "/api/chat",
            json={"user_message": "300000", "session_id": None},
        )

        session_id = response.json()["session_id"]

        # Delete session
        delete_response = client.delete(f"/api/sessions/{session_id}")
        assert delete_response.status_code == 200

        # Verify session is gone
        get_response = client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_list_sessions(self, client):
        """Test listing all sessions."""
        # Create multiple sessions
        client.post("/api/chat", json={"user_message": "300000", "session_id": None})
        client.post("/api/chat", json={"user_message": "500000", "session_id": None})

        # List sessions
        response = client.get("/api/sessions")
        assert response.status_code == 200

        data = response.json()
        assert "sessions" in data
        assert len(data["sessions"]) >= 2


@pytest.mark.asyncio
@patch("loan_defenders.orchestrators.sequential_pipeline.SequentialPipeline")
class TestEndToEndWorkflow:
    """Test complete end-to-end workflow from UI to agent processing."""

    async def test_complete_approval_workflow(self, mock_pipeline_class, client, mcp_harness):
        """Test complete workflow from conversation to approval."""
        # Configure approval scenario
        mcp_harness.configure_approval_scenario()

        # Mock pipeline to return approval updates
        mock_pipeline = Mock()

        async def mock_process(application):
            # Simulate agent processing updates
            from loan_defenders.models.responses import ProcessingUpdate

            yield ProcessingUpdate(
                agent_name="Intake_Agent",
                message="Validating application",
                phase="validating",
                completion_percentage=25,
                status="in_progress",
                assessment_data={},
                metadata={},
            )

            yield ProcessingUpdate(
                agent_name="Credit_Assessor",
                message="Assessing credit",
                phase="assessing_credit",
                completion_percentage=50,
                status="in_progress",
                assessment_data={},
                metadata={},
            )

            yield ProcessingUpdate(
                agent_name="Income_Verifier",
                message="Verifying income",
                phase="verifying_income",
                completion_percentage=75,
                status="in_progress",
                assessment_data={},
                metadata={},
            )

            yield ProcessingUpdate(
                agent_name="Risk_Analyzer",
                message="Decision complete",
                phase="completed",
                completion_percentage=100,
                status="completed",
                assessment_data={"decision": "approved"},
                metadata={},
            )

        mock_pipeline.process_application = mock_process
        mock_pipeline_class.return_value = mock_pipeline

        # Complete conversation flow
        import json as json_module

        r1 = client.post("/api/chat", json={"user_message": "300000", "session_id": None})
        session_id = r1.json()["session_id"]

        client.post("/api/chat", json={"user_message": "20", "session_id": session_id})
        client.post("/api/chat", json={"user_message": "175000", "session_id": session_id})

        personal_info = {"name": "Tony Stark", "email": "tony@starkindustries.com", "idLast4": "1234"}

        response = client.post(
            "/api/chat",
            json={"user_message": json_module.dumps(personal_info), "session_id": session_id},
        )

        # Verify final response indicates processing
        assert response.status_code == 200
        data = response.json()
        assert data["completion_percentage"] == 100


class TestErrorHandling:
    """Test error handling in the API."""

    def test_invalid_session_id(self, client):
        """Test handling of invalid session ID."""
        response = client.get("/api/sessions/invalid-session-id")
        assert response.status_code == 404

    def test_malformed_request(self, client):
        """Test handling of malformed request."""
        response = client.post(
            "/api/chat",
            json={"invalid": "data"},  # Missing required fields
        )

        # Should return validation error
        assert response.status_code == 422  # Unprocessable Entity
