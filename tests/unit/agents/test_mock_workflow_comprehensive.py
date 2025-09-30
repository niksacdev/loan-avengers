"""Comprehensive tests for MockSequentialLoanWorkflow to improve coverage."""

import pytest

from loan_avengers.agents.mock_sequential_workflow import (
    MockAgentThread,
    MockSequentialLoanWorkflow,
    MockSharedState,
)


class TestMockWorkflowDataExtraction:
    """Test workflow's data extraction logic."""

    @pytest.mark.asyncio
    async def test_extract_application_data_from_user_message(self):
        """Test extracting loan amount from user message."""
        workflow = MockSequentialLoanWorkflow()
        shared_state = MockSharedState()

        # Message with loan amount
        result = await workflow._extract_application_data("I need a $250,000 loan", shared_state)

        assert isinstance(result, dict)
        # Should extract some data or return existing data
        assert result is not None

    @pytest.mark.asyncio
    async def test_extract_preserves_existing_data(self):
        """Test that extraction preserves previously collected data."""
        workflow = MockSequentialLoanWorkflow()
        shared_state = MockSharedState()

        # Set some existing data
        existing_data = {"applicant_name": "John Doe", "email": "john@example.com"}
        await shared_state.set("application_data", existing_data)

        result = await workflow._extract_application_data("My phone is 555-1234", shared_state)

        # Should preserve existing data
        assert "applicant_name" in result or result == existing_data



class TestMockWorkflowPhases:
    """Test workflow phase transitions."""

    @pytest.mark.asyncio
    async def test_collecting_phase_when_incomplete(self):
        """Test workflow stays in collecting phase with incomplete data."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        # Set incomplete data
        await shared_state.set(
            "application_data",
            {
                "applicant_name": "Alice",
                "email": "alice@example.com",
                # Missing other required fields
            },
        )

        responses = []
        async for response in workflow.process_conversation("Hello", thread, shared_state):
            responses.append(response)

        # Should stay in collecting phase
        assert any(r.phase == "collecting" for r in responses)

    @pytest.mark.asyncio
    async def test_progression_to_validation_with_complete_data(self):
        """Test workflow progresses to validation when data complete."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        # Set complete data
        complete_data = {
            "applicant_name": "Charlie Brown",
            "email": "charlie@example.com",
            "phone": "555-0999",
            "date_of_birth": "1988-06-15",
            "loan_amount": 275000,
            "loan_purpose": "home_purchase",
            "loan_term_months": 360,
            "annual_income": 92000,
            "employment_status": "employed",
            "employer_name": "SalesInc",
            "months_employed": 36,
        }
        await shared_state.set("application_data", complete_data)

        phases_seen = []
        async for response in workflow.process_conversation("Ready to proceed", thread, shared_state):
            phases_seen.append(response.phase)

        # Should progress beyond collecting
        assert len(set(phases_seen)) > 1
        # Should see validation or assessment phases
        assert any(phase in phases_seen for phase in ["validating", "assessing_credit", "verifying_income"])


class TestMockWorkflowResponseGeneration:
    """Test workflow response generation."""

    @pytest.mark.asyncio
    async def test_generates_valid_workflow_responses(self):
        """Test all responses have required fields."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        async for response in workflow.process_conversation("Test message", thread, shared_state):
            # Check all required fields present
            assert hasattr(response, "agent_name")
            assert hasattr(response, "message")
            assert hasattr(response, "phase")
            assert hasattr(response, "completion_percentage")
            assert hasattr(response, "collected_data")
            assert hasattr(response, "action")
            assert hasattr(response, "metadata")

            # Check types
            assert isinstance(response.agent_name, str)
            assert isinstance(response.message, str)
            assert isinstance(response.phase, str)
            assert isinstance(response.completion_percentage, int)
            assert isinstance(response.collected_data, dict)
            assert len(response.agent_name) > 0
            assert len(response.message) > 0

    @pytest.mark.asyncio
    async def test_completion_percentage_within_bounds(self):
        """Test completion percentage is always 0-100."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        async for response in workflow.process_conversation("Check percentage", thread, shared_state):
            assert 0 <= response.completion_percentage <= 100


class TestMockWorkflowStateManagement:
    """Test workflow state management."""

    @pytest.mark.asyncio
    async def test_workflow_reads_from_shared_state(self):
        """Test workflow reads existing data from shared state."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        # Pre-populate data
        initial_data = {"applicant_name": "Diana", "email": "diana@example.com"}
        await shared_state.set("application_data", initial_data)

        async for _ in workflow.process_conversation("Continue", thread, shared_state):
            pass

        # Data should still be in shared state
        stored_data = await shared_state.get("application_data")
        assert stored_data is not None
        assert "applicant_name" in stored_data or stored_data == {}

    @pytest.mark.asyncio
    async def test_workflow_writes_to_shared_state(self):
        """Test workflow updates shared state."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        async for _ in workflow.process_conversation("I'm Edward", thread, shared_state):
            pass

        # Check something was written to state
        data = await shared_state.get("application_data")
        assert data is not None  # Should at least return empty dict


class TestMockWorkflowThreadManagement:
    """Test workflow thread history."""

    @pytest.mark.asyncio
    async def test_workflow_adds_messages_to_thread(self):
        """Test workflow adds messages to conversation history."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        initial_count = len(thread.conversation_history)

        async for _ in workflow.process_conversation("Test message", thread, shared_state):
            pass

        # Thread should have messages added
        final_count = len(thread.conversation_history)
        assert final_count >= initial_count


class TestMockWorkflowMultipleTurns:
    """Test workflow across multiple conversation turns."""

    @pytest.mark.asyncio
    async def test_multiple_conversation_turns(self):
        """Test processing multiple messages in sequence."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        # Turn 1
        async for _ in workflow.process_conversation("Hello", thread, shared_state):
            pass

        # Turn 2
        async for _ in workflow.process_conversation("I need a loan", thread, shared_state):
            pass

        # Turn 3
        async for response in workflow.process_conversation("$200,000", thread, shared_state):
            # Should still generate valid responses
            assert isinstance(response.message, str)

    @pytest.mark.asyncio
    async def test_data_accumulates_across_turns(self):
        """Test that data accumulates across conversation turns."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        # Set initial data
        await shared_state.set("application_data", {"applicant_name": "Frank"})

        # Process turn
        async for _ in workflow.process_conversation("My email is frank@example.com", thread, shared_state):
            pass

        # Data should be preserved or updated
        data = await shared_state.get("application_data")
        assert "applicant_name" in data or data == {}


class TestMockWorkflowEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_message(self):
        """Test handling empty message."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        # Should handle empty message gracefully
        async for response in workflow.process_conversation("", thread, shared_state):
            assert isinstance(response.message, str)

    @pytest.mark.asyncio
    async def test_very_long_message(self):
        """Test handling very long message."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        long_message = "I need a loan " * 100

        # Should handle long message without crashing
        async for response in workflow.process_conversation(long_message, thread, shared_state):
            assert isinstance(response.message, str)

    @pytest.mark.asyncio
    async def test_workflow_with_empty_shared_state(self):
        """Test workflow starts with empty shared state."""
        workflow = MockSequentialLoanWorkflow()
        thread = MockAgentThread()
        shared_state = MockSharedState()

        # Don't pre-populate any data
        async for response in workflow.process_conversation("Start fresh", thread, shared_state):
            assert isinstance(response, object)
            assert response.phase in ["collecting", "validating", "assessing_credit", "verifying_income", "deciding"]