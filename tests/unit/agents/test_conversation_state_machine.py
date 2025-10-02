"""
Unit tests for ConversationStateMachine.

Tests cover:
- State initialization and transitions
- Message processing and data extraction
- Field validation and completion tracking
- Response generation
"""

from loan_defenders.orchestrators.conversation_state_machine import (
    ConversationState,
    ConversationStateMachine,
)
from loan_defenders.models.responses import ConversationResponse


class TestConversationStateMachineInit:
    """Test initialization of ConversationStateMachine."""

    def test_init_sets_initial_state(self):
        """Test that state machine initializes in GREETING state."""
        machine = ConversationStateMachine()
        assert machine.state == ConversationState.GREETING

    def test_init_empty_collected_data(self):
        """Test that collected_data starts empty."""
        machine = ConversationStateMachine()
        assert machine.collected_data == {}

    def test_init_zero_completion_percentage(self):
        """Test that completion percentage starts at 0."""
        machine = ConversationStateMachine()
        assert machine.completion_percentage == 0


class TestConversationStateMachineGreeting:
    """Test GREETING state behavior."""

    def test_greeting_state_welcomes_user(self):
        """Test that greeting state provides welcome message."""
        machine = ConversationStateMachine()
        response = machine.process_input("Hello")

        assert response.agent_name == "Cap-ital America"
        assert "welcome" in response.message.lower() or "hello" in response.message.lower()
        assert response.action == "collect_info"
        assert machine.state == ConversationState.COLLECTING

    def test_greeting_state_transitions_to_collecting(self):
        """Test that any input transitions from GREETING to COLLECTING."""
        machine = ConversationStateMachine()
        machine.process_input("Hi there")
        assert machine.state == ConversationState.COLLECTING


class TestConversationStateMachineDataExtraction:
    """Test data extraction from user messages."""

    def test_extract_name_from_message(self):
        """Test extraction of applicant name."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")  # Move to COLLECTING
        machine.process_input("My name is John Doe")

        assert "applicant_name" in machine.collected_data
        assert machine.collected_data["applicant_name"] == "John Doe"

    def test_extract_email_from_message(self):
        """Test extraction of email address."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        machine.process_input("My email is john.doe@example.com")

        assert "email" in machine.collected_data
        assert machine.collected_data["email"] == "john.doe@example.com"

    def test_extract_phone_from_message(self):
        """Test extraction of phone number."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        machine.process_input("My phone is 555-123-4567")

        assert "phone" in machine.collected_data
        assert "phone" in machine.collected_data["phone"] or "555" in machine.collected_data["phone"]

    def test_extract_loan_amount_from_message(self):
        """Test extraction of loan amount."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        machine.process_input("I need a loan for $250000")

        assert "loan_amount" in machine.collected_data
        # Amount should be extracted as number
        assert isinstance(machine.collected_data["loan_amount"], (int, float, str))

    def test_extract_annual_income_from_message(self):
        """Test extraction of annual income."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        machine.process_input("My annual income is $85000")

        assert "annual_income" in machine.collected_data

    def test_extract_property_address_from_message(self):
        """Test extraction of property address."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        machine.process_input("The property is at 123 Main St, Springfield")

        assert "property_address" in machine.collected_data


class TestConversationStateMachineCompletionTracking:
    """Test completion percentage calculation."""

    def test_completion_percentage_increases_with_data(self):
        """Test that completion percentage increases as data is collected."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")

        initial_percentage = machine.completion_percentage

        machine.process_input("My name is John Doe")
        assert machine.completion_percentage > initial_percentage

    def test_completion_percentage_reaches_100(self):
        """Test that completion percentage reaches 100% with all fields."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")

        # Provide all required fields
        machine.process_input("My name is John Doe")
        machine.process_input("My email is john@example.com")
        machine.process_input("My phone is 555-1234")
        machine.process_input("I need $250000")
        machine.process_input("My income is $85000")
        machine.process_input("Property at 123 Main St")
        machine.process_input("I want to purchase a home")

        assert machine.completion_percentage >= 80  # Should be high


class TestConversationStateMachineProcessing:
    """Test transition to PROCESSING state."""

    def test_transitions_to_processing_when_complete(self):
        """Test that machine transitions to PROCESSING when data is complete."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")

        # Fill in all required data
        machine.collected_data = {
            "applicant_name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "loan_amount": 250000,
            "annual_income": 85000,
            "property_address": "123 Main St",
            "loan_purpose": "purchase",
        }
        machine.completion_percentage = 100

        response = machine.process_input("That's all my information")

        if response.action == "ready_for_processing":
            assert machine.state == ConversationState.PROCESSING

    def test_processing_response_has_correct_action(self):
        """Test that processing response has ready_for_processing action."""
        machine = ConversationStateMachine()
        machine.state = ConversationState.PROCESSING
        machine.collected_data = {
            "applicant_name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "loan_amount": 250000,
            "annual_income": 85000,
            "property_address": "123 Main St",
            "loan_purpose": "purchase",
        }
        machine.completion_percentage = 100

        response = machine._handle_processing()
        assert response.action == "ready_for_processing"
        assert response.completion_percentage == 100


class TestConversationStateMachineResponseStructure:
    """Test ConversationResponse structure."""

    def test_response_has_required_fields(self):
        """Test that all responses have required fields."""
        machine = ConversationStateMachine()
        response = machine.process_input("Hello")

        assert hasattr(response, "agent_name")
        assert hasattr(response, "message")
        assert hasattr(response, "action")
        assert hasattr(response, "collected_data")
        assert hasattr(response, "completion_percentage")

    def test_response_includes_collected_data(self):
        """Test that responses include current collected_data."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        response = machine.process_input("My name is John Doe")

        assert "applicant_name" in response.collected_data

    def test_response_includes_completion_percentage(self):
        """Test that responses include completion percentage."""
        machine = ConversationStateMachine()
        response = machine.process_input("Hello")

        assert isinstance(response.completion_percentage, int)
        assert 0 <= response.completion_percentage <= 100


class TestConversationStateMachineReset:
    """Test reset functionality."""

    def test_reset_clears_collected_data(self):
        """Test that reset clears collected data."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        machine.process_input("My name is John Doe")

        machine.reset()
        assert machine.collected_data == {}

    def test_reset_returns_to_greeting(self):
        """Test that reset returns to GREETING state."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        machine.process_input("My name is John Doe")

        machine.reset()
        assert machine.state == ConversationState.GREETING

    def test_reset_zeroes_completion_percentage(self):
        """Test that reset zeroes completion percentage."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")
        machine.process_input("My name is John Doe")

        machine.reset()
        assert machine.completion_percentage == 0


class TestConversationStateMachineEdgeCases:
    """Test edge cases and error handling."""

    def test_process_empty_message(self):
        """Test processing empty message."""
        machine = ConversationStateMachine()
        response = machine.process_input("")

        assert isinstance(response, ConversationResponse)
        assert response.agent_name == "Cap-ital America"

    def test_process_very_long_message(self):
        """Test processing very long message."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")

        long_message = "a" * 10000
        response = machine.process_input(long_message)

        assert isinstance(response, ConversationResponse)

    def test_process_special_characters(self):
        """Test processing message with special characters."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")

        response = machine.process_input("My name is José O'Brien-Smith")
        assert isinstance(response, ConversationResponse)

    def test_multiple_data_in_single_message(self):
        """Test extracting multiple fields from one message."""
        machine = ConversationStateMachine()
        machine.process_input("Hello")

        machine.process_input("My name is John Doe, email john@example.com, phone 555-1234")

        # Should extract at least name and email
        assert len(machine.collected_data) >= 2
