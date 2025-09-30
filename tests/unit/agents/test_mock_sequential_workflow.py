"""Smoke tests for MockSequentialLoanWorkflow used when agent_framework unavailable."""

import pytest

from loan_avengers.agents.mock_sequential_workflow import (
    MockAgentThread,
    MockSequentialLoanWorkflow,
    MockSharedState,
    WorkflowResponse,
)


class TestMockAgentThread:
    """Test MockAgentThread behavior."""

    def test_init_generates_thread_id(self):
        """Test thread generates thread_id on initialization."""
        thread = MockAgentThread()
        assert thread.thread_id is not None
        assert isinstance(thread.thread_id, str)
        assert thread.thread_id.startswith("thread_")

    def test_conversation_history_initialized(self):
        """Test conversation history starts empty."""
        thread = MockAgentThread()
        assert thread.conversation_history == []

    def test_add_message(self):
        """Test adding messages to conversation history."""
        thread = MockAgentThread()
        thread.add_message("user", "Hello")
        thread.add_message("assistant", "Hi there!")

        assert len(thread.conversation_history) == 2
        assert thread.conversation_history[0]["role"] == "user"
        assert thread.conversation_history[0]["content"] == "Hello"
        assert thread.conversation_history[1]["role"] == "assistant"
        assert "timestamp" in thread.conversation_history[0]


class TestMockSharedState:
    """Test MockSharedState behavior."""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test setting and getting values."""
        state = MockSharedState()
        await state.set("key1", "value1")
        result = await state.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_empty_dict(self):
        """Test getting non-existent key returns empty dict."""
        state = MockSharedState()
        result = await state.get("nonexistent")
        assert result == {}  # Mock implementation returns {} not None

    @pytest.mark.asyncio
    async def test_overwrite_value(self):
        """Test overwriting existing value."""
        state = MockSharedState()
        await state.set("key1", "value1")
        await state.set("key1", "value2")
        result = await state.get("key1")
        assert result == "value2"

    @pytest.mark.asyncio
    async def test_multiple_keys(self):
        """Test storing multiple independent keys."""
        state = MockSharedState()
        await state.set("key1", "value1")
        await state.set("key2", "value2")
        await state.set("key3", "value3")

        assert await state.get("key1") == "value1"
        assert await state.get("key2") == "value2"
        assert await state.get("key3") == "value3"


class TestWorkflowResponse:
    """Test WorkflowResponse model."""

    def test_minimal_response(self):
        """Test creating response with minimal fields."""
        response = WorkflowResponse(
            agent_name="TestAgent",
            message="Test message",
            phase="testing",
            completion_percentage=50,
        )
        assert response.agent_name == "TestAgent"
        assert response.message == "Test message"
        assert response.phase == "testing"
        assert response.completion_percentage == 50
        assert response.collected_data == {}
        assert response.action == "processing"
        assert response.metadata == {}

    def test_full_response(self):
        """Test creating response with all fields."""
        response = WorkflowResponse(
            agent_name="Coordinator",
            message="Please provide your income",
            phase="collecting",
            completion_percentage=60,
            collected_data={"applicant_name": "Alice", "email": "alice@example.com"},
            action="collect_info",
            metadata={"step": 3, "total_steps": 5},
        )
        assert response.agent_name == "Coordinator"
        assert response.collected_data["applicant_name"] == "Alice"
        assert response.action == "collect_info"
        assert response.metadata["step"] == 3


class TestMockSequentialLoanWorkflow:
    """Smoke tests for MockSequentialLoanWorkflow."""

    def test_init(self):
        """Test workflow initialization."""
        workflow = MockSequentialLoanWorkflow()
        assert workflow is not None

    @pytest.mark.asyncio
    async def test_process_conversation_returns_generator(self):
        """Test that process_conversation returns an async generator."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        result = workflow.process_conversation("Hi", thread, shared_state)
        # Should be an async generator
        assert hasattr(result, "__aiter__")

    @pytest.mark.asyncio
    async def test_process_conversation_yields_responses(self):
        """Test that process_conversation yields WorkflowResponse objects."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        responses = []
        async for response in workflow.process_conversation("Hello", thread, shared_state):
            responses.append(response)
            assert isinstance(response, WorkflowResponse)
            assert hasattr(response, "agent_name")
            assert hasattr(response, "message")
            assert hasattr(response, "phase")
            assert hasattr(response, "completion_percentage")

        # Should get at least one response
        assert len(responses) > 0

    @pytest.mark.asyncio
    async def test_workflow_updates_shared_state(self):
        """Test that workflow can interact with shared state."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        # Set some initial data
        await shared_state.set("test_key", "test_value")

        async for _ in workflow.process_conversation("Test message", thread, shared_state):
            pass

        # Shared state should still be accessible
        result = await shared_state.get("test_key")
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_workflow_phases(self):
        """Test that workflow progresses through phases."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        phases_seen = set()
        async for response in workflow.process_conversation("Process application", thread, shared_state):
            phases_seen.add(response.phase)

        # Should see at least one phase
        assert len(phases_seen) > 0
        # Common phases include: collecting, validating, assessing, deciding
        expected_phases = ["collecting", "validating", "assessing_credit", "verifying_income", "deciding"]
        assert any(phase in phases_seen for phase in expected_phases)
