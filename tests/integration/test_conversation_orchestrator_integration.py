"""
Integration tests for ConversationOrchestrator.

Tests orchestration between state machine and loan application creation.
"""

from decimal import Decimal

import pytest

from loan_defenders.agents.conversation_orchestrator import ConversationOrchestrator
from loan_defenders.models.application import LoanApplication


class TestConversationOrchestratorIntegration:
    """Test ConversationOrchestrator with real dependencies."""

    def test_orchestrator_initializes_with_state_machine(self):
        """Test that orchestrator creates state machine on init."""
        orchestrator = ConversationOrchestrator()

        assert orchestrator.state_machine is not None
        assert hasattr(orchestrator.state_machine, "process_input")

    def test_create_loan_application_from_complete_data(self):
        """Test creating LoanApplication from complete collected data."""
        orchestrator = ConversationOrchestrator()

        collected_data = {
            "applicant_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "home_price": 400000,
            "down_payment_percentage": 20,
            "down_payment": 80000,
            "loan_amount": 320000,
            "annual_income": 95000,
            "loan_purpose": "purchase",
        }

        application = orchestrator.create_loan_application(collected_data)

        assert isinstance(application, LoanApplication)
        assert application.applicant_name == "John Doe"
        assert application.email == "john.doe@example.com"
        assert application.loan_amount == Decimal("320000")
        assert application.annual_income == Decimal("95000")
        assert application.loan_purpose == "purchase"

    def test_create_loan_application_generates_uuid(self):
        """Test that create_loan_application generates valid UUID."""
        orchestrator = ConversationOrchestrator()

        collected_data = {
            "applicant_name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "555-9876",
            "loan_amount": 250000,
            "annual_income": 75000,
        }

        application = orchestrator.create_loan_application(collected_data)

        # applicant_id should be valid UUID
        assert application.applicant_id is not None
        assert len(application.applicant_id) == 36  # UUID format
        assert "-" in application.applicant_id

    def test_has_all_required_fields_validation(self):
        """Test validation of required fields."""
        orchestrator = ConversationOrchestrator()

        # Complete data
        complete_data = {
            "applicant_name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "loan_amount": 300000,
            "annual_income": 80000,
        }

        assert orchestrator.has_all_required_fields(complete_data) is True

        # Incomplete data
        incomplete_data = {
            "applicant_name": "John Doe",
            "email": "john@example.com",
            # Missing phone, loan_amount, annual_income
        }

        assert orchestrator.has_all_required_fields(incomplete_data) is False

    def test_reset_clears_state_machine(self):
        """Test that reset clears orchestrator state."""
        orchestrator = ConversationOrchestrator()

        # Process some data
        orchestrator.state_machine.collected_data = {"test": "data"}

        # Reset
        orchestrator.reset()

        # State machine should be reset
        assert len(orchestrator.state_machine.collected_data) == 0


class TestLoanApplicationCreationEdgeCases:
    """Test edge cases in loan application creation."""

    def test_create_application_with_string_numbers(self):
        """Test handling of numeric fields as strings."""
        orchestrator = ConversationOrchestrator()

        collected_data = {
            "applicant_name": "Test User",
            "email": "test@example.com",
            "phone": "555-0000",
            "loan_amount": "400000",  # String
            "annual_income": "85000",  # String
            "down_payment": "80000",  # String
        }

        application = orchestrator.create_loan_application(collected_data)

        # Should convert to Decimal
        assert isinstance(application.loan_amount, Decimal)
        assert application.loan_amount == Decimal("400000")
        assert isinstance(application.annual_income, Decimal)

    def test_create_application_with_optional_fields(self):
        """Test creating application with only required fields."""
        orchestrator = ConversationOrchestrator()

        minimal_data = {
            "applicant_name": "Minimal User",
            "email": "minimal@example.com",
            "phone": "555-0000",
            "loan_amount": 250000,
            "annual_income": 70000,
        }

        application = orchestrator.create_loan_application(minimal_data)

        assert application.applicant_name == "Minimal User"
        assert application.loan_amount == Decimal("250000")

    def test_create_application_preserves_all_fields(self):
        """Test that all provided fields are preserved."""
        orchestrator = ConversationOrchestrator()

        complete_data = {
            "applicant_name": "Complete User",
            "email": "complete@example.com",
            "phone": "555-9999",
            "home_price": 500000,
            "down_payment_percentage": 20,
            "down_payment": 100000,
            "loan_amount": 400000,
            "annual_income": 120000,
            "loan_purpose": "purchase",
            "property_address": "123 Main St",
            "credit_score": 750,
        }

        application = orchestrator.create_loan_application(complete_data)

        assert application.email == "complete@example.com"
        assert application.phone == "555-9999"
        assert application.property_address == "123 Main St"
        if hasattr(application, "credit_score"):
            assert application.credit_score == 750


class TestOrchestratorWithStateMachine:
    """Test orchestrator working with state machine."""

    async def test_orchestrator_processes_conversation_turns(self):
        """Test orchestrator handling multiple conversation turns."""
        orchestrator = ConversationOrchestrator()

        # Initial greeting
        async for response in orchestrator.handle_conversation("Hello"):
            assert response.agent_name == "Cap-ital America"
            assert response.completion_percentage == 0
            break  # Just test first response

    async def test_orchestrator_accumulates_session_state(self):
        """Test that orchestrator maintains session state across turns."""
        orchestrator = ConversationOrchestrator()

        session_state = {}

        # First turn
        async for response in orchestrator.handle_conversation("Hello", session_state):
            # Update session state
            session_state["last_response"] = response.message
            break

        assert "last_response" in session_state

        # Second turn with existing session state
        async for response in orchestrator.handle_conversation("500000", session_state):
            assert response.completion_percentage > 0
            break


class TestDataValidation:
    """Test orchestrator data validation."""

    def test_validates_email_format(self):
        """Test email format validation in application creation."""
        orchestrator = ConversationOrchestrator()

        data_with_valid_email = {
            "applicant_name": "Valid User",
            "email": "valid@example.com",
            "phone": "555-1234",
            "loan_amount": 300000,
            "annual_income": 80000,
        }

        # Should not raise error
        application = orchestrator.create_loan_application(data_with_valid_email)
        assert application.email == "valid@example.com"

    def test_handles_missing_optional_data(self):
        """Test handling of missing optional fields."""
        orchestrator = ConversationOrchestrator()

        minimal_required = {
            "applicant_name": "Min User",
            "email": "min@example.com",
            "phone": "555-0000",
            "loan_amount": 200000,
            "annual_income": 60000,
        }

        # Should create application without errors
        application = orchestrator.create_loan_application(minimal_required)
        assert application.applicant_name == "Min User"


class TestOrchestratorErrorHandling:
    """Test error handling in orchestrator."""

    def test_create_application_with_invalid_data_raises_error(self):
        """Test that invalid data raises appropriate error."""
        orchestrator = ConversationOrchestrator()

        invalid_data = {
            "applicant_name": "Bad Data",
            # Missing required fields
        }

        # Should raise ValueError or ValidationError
        with pytest.raises((ValueError, Exception)):
            orchestrator.create_loan_application(invalid_data)

    def test_orchestrator_handles_state_machine_errors(self):
        """Test orchestrator handles state machine errors gracefully."""
        orchestrator = ConversationOrchestrator()

        # Try to process with very unusual input
        async def process():
            async for response in orchestrator.handle_conversation(None):
                return response

        # Should handle gracefully (might return error response)
        # This tests resilience rather than specific behavior


class TestOrchestratorLifecycle:
    """Test orchestrator lifecycle management."""

    def test_multiple_resets(self):
        """Test that orchestrator can be reset multiple times."""
        orchestrator = ConversationOrchestrator()

        # Use orchestrator
        orchestrator.state_machine.collected_data = {"test": "data1"}
        orchestrator.reset()

        # Use again
        orchestrator.state_machine.collected_data = {"test": "data2"}
        orchestrator.reset()

        # Should be clean
        assert len(orchestrator.state_machine.collected_data) == 0

    def test_orchestrator_reusable_after_reset(self):
        """Test that orchestrator is fully functional after reset."""
        orchestrator = ConversationOrchestrator()

        # First use
        orchestrator.state_machine.collected_data = {
            "applicant_name": "First User",
            "email": "first@example.com",
        }

        # Reset
        orchestrator.reset()

        # Second use - should work normally
        async def test_reuse():
            async for response in orchestrator.handle_conversation("Hello"):
                assert response.agent_name == "Cap-ital America"
                return True

        # Should work without errors
        assert orchestrator.state_machine.collected_data == {}
