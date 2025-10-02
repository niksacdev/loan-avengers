"""
Conversation Orchestrator - Deterministic state machine with async agent streaming.

Pattern: Code-Based State Machine + Async Agent Streaming
- Uses ConversationStateMachine for deterministic conversation flow
- Handles LoanApplication creation and validation
- Streams agent updates from LoanProcessingPipeline to UI

Code Responsibilities:
- State management via ConversationStateMachine
- LoanApplication creation from collected data
- Async streaming of processing updates
- Error handling and recovery
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import ConversationResponse
from loan_avengers.orchestrators.conversation_state_machine import ConversationStateMachine
from loan_avengers.utils.observability import Observability

logger = Observability.get_logger("conversation_orchestrator")


class ConversationOrchestrator:
    """
    Code-based orchestrator using deterministic state machine.

    Orchestrator Scope:
    ✅ Manage conversation state via ConversationStateMachine
    ✅ Validate data completeness
    ✅ Create LoanApplication objects
    ✅ Trigger handoffs to processing pipeline
    ✅ Stream agent updates back to UI

    ❌ LLM calls for conversation (deterministic state machine)
    ❌ Natural language processing (only needed in processing agents)

    Attributes:
        state_machine: Deterministic conversation state machine

    Pattern Flow:
        User message → ConversationStateMachine → Deterministic Response
        → If complete: Create LoanApplication → LoanProcessingPipeline
        → Stream agent updates → Display in UI
    """

    def __init__(self):
        """Initialize the conversation orchestrator with state machine."""
        self.state_machine = ConversationStateMachine()
        logger.info("ConversationOrchestrator initialized with state machine")

    async def handle_conversation(
        self, user_message: str, session_state: dict[str, Any] | None = None
    ) -> AsyncGenerator[ConversationResponse, None]:
        """
        Handle conversation turn using deterministic state machine.

        Flow:
        1. State Machine: Process input → deterministic response
        2. Code: Return ConversationResponse
        3. Code: If ready_for_processing, trigger LoanProcessingPipeline

        Args:
            user_message: User's input (quick reply value or form data)
            session_state: Optional session state to restore state machine

        Yields:
            ConversationResponse: Structured response with:
                - agent_name: "Cap-ital America"
                - message: Pre-scripted engaging response
                - action: "collect_info" | "ready_for_processing"
                - collected_data: Dict of gathered loan info
                - completion_percentage: 0-100
                - quick_replies: List of quick reply options
                - next_step: What happens next
        """
        try:
            logger.info(
                "Processing conversation input",
                extra={
                    "user_message_length": len(user_message),
                    "current_state": self.state_machine.state.value,
                },
            )

            # Restore state if provided (for session continuity)
            if session_state:
                self.state_machine.collected_data = session_state.get("collected_data", {})
                # State will be inferred from completion percentage

            # Process input through state machine (deterministic, no LLM)
            response = self.state_machine.process_input(user_message)

            logger.info(
                "State machine response generated",
                extra={
                    "action": response.action,
                    "completion": response.completion_percentage,
                    "next_state": self.state_machine.state.value,
                },
            )

            # Yield the conversation response
            yield response

        except Exception as e:
            logger.error("Conversation orchestration failed", extra={"error": str(e)}, exc_info=True)

            # Return error response with Cap-ital America personality
            yield ConversationResponse(
                agent_name="Cap-ital America",
                message=(
                    "🦸‍♂️ Whoa there! I'm experiencing some technical difficulties on my end. "
                    "Let's regroup and try that again, soldier! 💪"
                ),
                action="error",
                collected_data=self.state_machine.collected_data,
                next_step="Please try sending your message again",
                completion_percentage=0,
                metadata={"error": str(e)},
            )

    def has_all_required_fields(self, collected_data: dict[str, Any]) -> bool:
        """
        Validate data completeness (deterministic business rule).

        Required fields:
        - applicant_name
        - email
        - loan_amount
        - annual_income
        - down_payment

        Args:
            collected_data: Dictionary of gathered user data

        Returns:
            bool: True if all required fields present and non-empty
        """
        required_fields = [
            "applicant_name",
            "email",
            "loan_amount",
            "annual_income",
            "down_payment",
        ]

        has_all = all(field in collected_data and collected_data[field] for field in required_fields)

        logger.info(
            "Checking field completeness",
            extra={
                "has_all_fields": has_all,
                "collected_fields": list(collected_data.keys()),
                "required_fields": required_fields,
            },
        )

        return has_all

    def create_loan_application(self, collected_data: dict[str, Any]) -> LoanApplication:
        """
        Create validated LoanApplication from conversation data.

        Deterministic transformations:
        - Generate UUID for applicant_id
        - Generate LN-prefixed application_id
        - Apply default values for optional fields
        - Validate via Pydantic model

        Args:
            collected_data: Dict from state machine with user data

        Returns:
            LoanApplication: Validated Pydantic model ready for processing

        Raises:
            ValueError: If data fails Pydantic validation
        """
        try:
            # Generate proper UUID for applicant_id
            applicant_id = str(uuid.uuid4())

            # Generate application_id in format LN + 10 digits
            app_id_num = abs(uuid.uuid4().int) % 10000000000
            application_id = f"LN{app_id_num:010d}"

            # Provide defaults for fields not collected in simplified flow
            application_data = {
                "application_id": application_id,
                "applicant_name": collected_data.get("applicant_name"),
                "applicant_id": applicant_id,
                "email": collected_data.get("email"),
                "phone": collected_data.get("phone", "5555551234"),
                "date_of_birth": collected_data.get("date_of_birth", datetime(1990, 1, 1)),
                "loan_amount": collected_data.get("loan_amount"),
                "loan_purpose": collected_data.get("loan_purpose", "home_purchase"),
                "loan_term_months": collected_data.get("loan_term_months", 360),
                "annual_income": collected_data.get("annual_income"),
                "employment_status": collected_data.get("employment_status", "employed"),
                "employer_name": collected_data.get("employer_name", "Not Provided"),
                "months_employed": collected_data.get("months_employed", 12),
                "down_payment": collected_data.get("down_payment"),
            }

            application = LoanApplication(**application_data)

            logger.info(
                "LoanApplication created from state machine data",
                extra={
                    "application_id": application.application_id,
                    "applicant_name": application.applicant_name,
                },
            )

            return application

        except Exception as e:
            logger.error(
                "Failed to create LoanApplication from state machine data",
                extra={"collected_data": collected_data},
                exc_info=True,
            )
            raise ValueError(f"Invalid conversation data for loan application: {str(e)}") from e

    def reset(self) -> None:
        """Reset orchestrator state machine to initial state.

        Clears all conversation state and collected data, allowing
        the orchestrator to be reused for a new conversation.
        """
        self.state_machine.reset()
        logger.info("Orchestrator reset to initial state")


__all__ = ["ConversationOrchestrator"]
