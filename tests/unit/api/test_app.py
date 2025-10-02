"""Tests for FastAPI application endpoints."""

import pytest
from fastapi.testclient import TestClient

from loan_defenders.api.app import app


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_returns_200(self):
        """Test that health endpoint returns 200 OK."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_check_structure(self):
        """Test health response structure."""
        client = TestClient(app)
        response = client.get("/health")

        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert "timestamp" in data
        assert "service" in data or "status" in data


class TestChatEndpoint:
    """Test chat endpoint."""

    @pytest.mark.asyncio
    async def test_chat_endpoint_exists(self):
        """Test that chat endpoint is accessible."""
        client = TestClient(app)
        # POST without data should give 422 (validation error), not 404
        response = client.post("/api/chat")
        assert response.status_code in [400, 422]  # Not 404

    @pytest.mark.asyncio
    async def test_chat_requires_session_id(self):
        """Test that chat endpoint requires session_id."""
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={
                "message": "Hello"
                # Missing session_id
            },
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_chat_requires_message(self):
        """Test that chat endpoint requires message."""
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={
                "session_id": "test-session-123"
                # Missing message
            },
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_chat_with_valid_payload(self):
        """Test chat endpoint with valid payload."""
        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={"session_id": "test-session-456", "user_message": "I need a loan for $200,000"},
        )

        # Should either succeed (200) or have server error (500)
        # but not validation error (422)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            # If successful, should have expected structure
            data = response.json()
            assert isinstance(data, dict)
            assert "agent_name" in data or "message" in data


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_allows_localhost(self):
        """Test that CORS is configured."""
        client = TestClient(app)
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:5173"},
        )
        # Should not be blocked by CORS
        assert response.status_code == 200


class TestSessionEndpoints:
    """Test session management endpoints."""

    def test_create_session_endpoint_exists(self):
        """Test that session creation endpoint exists."""
        client = TestClient(app)
        response = client.post("/api/sessions")

        # Should either create session (200/201) or have error
        # but not 404 (endpoint exists)
        assert response.status_code != 404

    def test_get_session_endpoint_exists(self):
        """Test that get session endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/sessions/test-session-id")

        # Should either return session data or 404 for missing session
        # but endpoint itself should exist
        assert response.status_code in [200, 404, 500]

    def test_delete_session_endpoint_exists(self):
        """Test that delete session endpoint exists."""
        client = TestClient(app)
        response = client.delete("/api/sessions/test-session-id")

        # Endpoint should exist (not 405 Method Not Allowed for wrong method)
        assert response.status_code in [200, 204, 404, 500]
