"""
Integration tests for ConversationStateMachine.

Tests the full conversation flow from initial state through data collection
to processing state, simulating real user interactions.
"""

from loan_avengers.agents.conversation_state_machine import (
    ConversationState,
    ConversationStateMachine,
)


class TestConversationFlowIntegration:
    """Test complete conversation flows."""

    def test_complete_loan_application_flow(self):
        """Test a complete happy path from start to processing."""
        machine = ConversationStateMachine()

        # Step 1: Initial greeting
        assert machine.state == ConversationState.INITIAL
        response1 = machine.process_input("")  # Empty triggers initial message
        assert response1.agent_name == "Cap-ital America"
        assert response1.completion_percentage == 0
        assert len(response1.quick_replies) > 0  # Should have home price options

        # Step 2: Select home price
        response2 = machine.process_input("500000")  # $500k home
        assert machine.state == ConversationState.DOWN_PAYMENT
        assert response2.completion_percentage == 25
        assert "home_price" in machine.collected_data or "loan_amount" in machine.collected_data

        # Step 3: Select down payment
        response3 = machine.process_input("20")  # 20% down
        assert machine.state == ConversationState.INCOME
        assert response3.completion_percentage == 50
        assert "down_payment_percentage" in machine.collected_data or "down_payment" in machine.collected_data

        # Step 4: Select income range
        response4 = machine.process_input("100000")  # $100k income
        assert machine.state == ConversationState.PERSONAL_INFO
        assert response4.completion_percentage == 75
        assert "annual_income" in machine.collected_data

        # Step 5: Provide personal info (this would be form data)
        personal_info = '{"name": "John Doe", "email": "john@example.com", "phone": "555-1234"}'
        response5 = machine.process_input(personal_info)
        assert machine.state == ConversationState.PROCESSING
        assert response5.completion_percentage == 100
        assert response5.action == "ready_for_processing"

    def test_state_transitions_are_deterministic(self):
        """Test that same inputs produce same state transitions."""
        machine1 = ConversationStateMachine()
        machine2 = ConversationStateMachine()

        # Apply same sequence to both
        inputs = ["", "400000", "15", "85000"]

        for user_input in inputs:
            r1 = machine1.process_input(user_input)
            r2 = machine2.process_input(user_input)

            assert machine1.state == machine2.state
            assert r1.completion_percentage == r2.completion_percentage

    def test_data_accumulation_across_states(self):
        """Test that data accumulates as user progresses."""
        machine = ConversationStateMachine()

        machine.process_input("")  # Initial
        assert len(machine.collected_data) == 0

        machine.process_input("350000")  # Home price
        data_after_step1 = len(machine.collected_data)
        assert data_after_step1 >= 1

        machine.process_input("10")  # Down payment
        data_after_step2 = len(machine.collected_data)
        assert data_after_step2 >= data_after_step1

        machine.process_input("75000")  # Income
        data_after_step3 = len(machine.collected_data)
        assert data_after_step3 >= data_after_step2


class TestQuickRepliesIntegration:
    """Test quick reply generation throughout conversation."""

    def test_initial_state_provides_home_price_options(self):
        """Test that initial state provides home price quick replies."""
        machine = ConversationStateMachine()
        response = machine.process_input("")

        assert len(response.quick_replies) > 0
        # Should have multiple price options
        assert any("$" in reply or "price" in reply.lower() for reply in response.quick_replies)

    def test_down_payment_state_provides_percentage_options(self):
        """Test down payment state provides percentage quick replies."""
        machine = ConversationStateMachine()
        machine.process_input("")  # Initial
        response = machine.process_input("400000")  # Home price

        assert len(response.quick_replies) > 0
        # Should have percentage options
        assert any("%" in reply or "down" in reply.lower() for reply in response.quick_replies)

    def test_income_state_provides_income_ranges(self):
        """Test income state provides income range quick replies."""
        machine = ConversationStateMachine()
        machine.process_input("")  # Initial
        machine.process_input("400000")  # Home price
        response = machine.process_input("20")  # Down payment

        assert len(response.quick_replies) > 0
        # Should have income ranges
        assert any("income" in reply.lower() or "$" in reply for reply in response.quick_replies)


class TestErrorHandlingIntegration:
    """Test error handling and edge cases in full flow."""

    def test_invalid_home_price_handling(self):
        """Test handling of invalid home price input."""
        machine = ConversationStateMachine()
        machine.process_input("")  # Initial

        # Try invalid input
        response = machine.process_input("invalid")
        # Should handle gracefully, might re-prompt or use default

        assert isinstance(response.message, str)
        assert response.agent_name == "Cap-ital America"

    def test_reset_during_conversation(self):
        """Test resetting state machine mid-conversation."""
        machine = ConversationStateMachine()
        machine.process_input("")  # Initial
        machine.process_input("400000")  # Home price
        machine.process_input("15")  # Down payment

        # Now reset
        machine.reset()

        assert machine.state == ConversationState.INITIAL
        assert len(machine.collected_data) == 0

        # Should be able to start again
        response = machine.process_input("")
        assert response.completion_percentage == 0


class TestPersonalInfoFormIntegration:
    """Test personal information form submission."""

    def test_personal_info_json_parsing(self):
        """Test parsing of personal info JSON from form."""
        machine = ConversationStateMachine()

        # Get to personal info state
        machine.process_input("")  # Initial
        machine.process_input("450000")  # Home price
        machine.process_input("20")  # Down payment
        machine.process_input("95000")  # Income

        # Submit personal info as JSON
        personal_info = '{"name": "Jane Smith", "email": "jane@example.com", "phone": "555-9876"}'
        machine.process_input(personal_info)

        # Should parse and store personal info
        assert "applicant_name" in machine.collected_data or "name" in machine.collected_data
        assert "email" in machine.collected_data
        assert "phone" in machine.collected_data

    def test_personal_info_completes_application(self):
        """Test that personal info submission triggers processing."""
        machine = ConversationStateMachine()

        # Complete all steps
        machine.process_input("")
        machine.process_input("500000")
        machine.process_input("25")
        machine.process_input("120000")

        response = machine.process_input('{"name": "Test User", "email": "test@example.com", "phone": "555-0000"}')

        assert response.action == "ready_for_processing"
        assert response.completion_percentage == 100
        assert machine.state == ConversationState.PROCESSING


class TestCompletionPercentageIntegration:
    """Test completion percentage tracking throughout flow."""

    def test_completion_percentage_progression(self):
        """Test that completion percentage increases correctly."""
        machine = ConversationStateMachine()

        # Track progression
        percentages = []

        r1 = machine.process_input("")  # Initial: 0%
        percentages.append(r1.completion_percentage)

        r2 = machine.process_input("400000")  # Home price: 25%
        percentages.append(r2.completion_percentage)

        r3 = machine.process_input("15")  # Down payment: 50%
        percentages.append(r3.completion_percentage)

        r4 = machine.process_input("80000")  # Income: 75%
        percentages.append(r4.completion_percentage)

        r5 = machine.process_input('{"name": "Test", "email": "test@example.com", "phone": "555"}')  # Complete: 100%
        percentages.append(r5.completion_percentage)

        # Should be monotonically increasing
        assert percentages == [0, 25, 50, 75, 100]

    def test_completion_percentage_matches_state(self):
        """Test that completion percentage corresponds to current state."""
        machine = ConversationStateMachine()

        machine.process_input("")  # INITIAL
        r1 = machine.process_input("300000")  # DOWN_PAYMENT state
        assert r1.completion_percentage == 25

        r2 = machine.process_input("10")  # INCOME state
        assert r2.completion_percentage == 50

        r3 = machine.process_input("70000")  # PERSONAL_INFO state
        assert r3.completion_percentage == 75


class TestResponseStructureIntegration:
    """Test that responses maintain consistent structure throughout flow."""

    def test_all_responses_have_required_fields(self):
        """Test that all responses contain required fields."""
        machine = ConversationStateMachine()

        responses = [
            machine.process_input(""),  # Initial
            machine.process_input("400000"),  # Home price
            machine.process_input("15"),  # Down payment
            machine.process_input("85000"),  # Income
        ]

        for response in responses:
            assert hasattr(response, "agent_name")
            assert hasattr(response, "message")
            assert hasattr(response, "action")
            assert hasattr(response, "collected_data")
            assert hasattr(response, "completion_percentage")
            assert hasattr(response, "quick_replies")

            assert response.agent_name == "Cap-ital America"
            assert isinstance(response.message, str)
            assert len(response.message) > 0

    def test_collected_data_always_dict(self):
        """Test that collected_data is always a dictionary."""
        machine = ConversationStateMachine()

        responses = [
            machine.process_input(""),
            machine.process_input("400000"),
            machine.process_input("15"),
        ]

        for response in responses:
            assert isinstance(response.collected_data, dict)


class TestAvengersPersonalityIntegration:
    """Test that Cap-ital America personality shines through responses."""

    def test_responses_have_personality(self):
        """Test that messages have engaging personality."""
        machine = ConversationStateMachine()
        response = machine.process_input("")

        message = response.message.lower()
        # Should have enthusiastic or personality-driven language
        personality_markers = ["🦸", "🛡️", "avenger", "assemble", "soldier", "mission"]
        assert any(marker in message for marker in personality_markers)

    def test_processing_state_has_avengers_theme(self):
        """Test that processing state message has Avengers theme."""
        machine = ConversationStateMachine()

        # Get to processing state
        machine.process_input("")
        machine.process_input("500000")
        machine.process_input("20")
        machine.process_input("100000")
        response = machine.process_input('{"name": "Test", "email": "test@example.com", "phone": "555"}')

        message = response.message.lower()
        # Should reference team assembly
        assert "avenger" in message or "assemble" in message or "team" in message
