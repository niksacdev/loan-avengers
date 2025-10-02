"""
Deterministic conversation state machine for loan application data collection.

This replaces the LLM-based ConversationAgent with a predictable state machine
that uses pre-scripted Cap-ital America messages for engaging user experience.

Pattern: Code-Based State Machine
- Deterministic state transitions (no LLM needed for conversation flow)
- Pre-scripted personality-rich messages
- Invokes LoanProcessingPipeline when data collection complete
- Streams agent updates back to UI
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from loan_defenders.models.responses import ConversationResponse
from loan_defenders.utils.observability import Observability

logger = Observability.get_logger("conversation_state_machine")


class ConversationState(Enum):
    """States in the loan application conversation flow."""

    INITIAL = "initial"
    HOME_PRICE = "home_price"
    DOWN_PAYMENT = "down_payment"
    INCOME = "income"
    PERSONAL_INFO = "personal_info"
    PROCESSING = "processing"
    COMPLETE = "complete"


class ConversationStateMachine:
    """
    Deterministic state machine for loan application conversation.

    Manages the 4-step data collection process:
    1. Home Purchase Price (0% → 25%)
    2. Down Payment Percentage (25% → 50%)
    3. Annual Income Range (50% → 75%)
    4. Personal Information Form (75% → 100%)
    5. Sequential Workflow Processing (async agent streaming)

    All Cap-ital America responses are pre-scripted but personality-rich.
    No LLM calls until processing phase (Intake, Credit, Income, Risk agents).
    """

    def __init__(self):
        """Initialize state machine with INITIAL state."""
        self.state = ConversationState.INITIAL
        self.collected_data: dict[str, Any] = {}

        logger.info("ConversationStateMachine initialized")

    def process_input(self, user_input: str) -> ConversationResponse:
        """
        Process user input and return deterministic response.

        Args:
            user_input: User's message (typically a quick reply value or form data)

        Returns:
            ConversationResponse: Next message, quick replies, and state info
        """
        logger.info(
            "Processing input",
            extra={
                "current_state": self.state.value,
                "input_length": len(user_input),
                "collected_fields": len(self.collected_data),
            },
        )

        if self.state == ConversationState.INITIAL:
            # If user provided input in INITIAL state, treat it as home price selection
            if user_input.strip() and user_input.strip().isdigit():
                self.state = ConversationState.HOME_PRICE
                return self._handle_home_price(user_input)
            else:
                return self._handle_initial()
        elif self.state == ConversationState.HOME_PRICE:
            return self._handle_home_price(user_input)
        elif self.state == ConversationState.DOWN_PAYMENT:
            return self._handle_down_payment(user_input)
        elif self.state == ConversationState.INCOME:
            return self._handle_income(user_input)
        elif self.state == ConversationState.PERSONAL_INFO:
            return self._handle_personal_info(user_input)
        else:
            # Fallback for unexpected states
            logger.warning(f"Unexpected state: {self.state}")
            return self._handle_initial()

    def _handle_initial(self) -> ConversationResponse:
        """
        Initial greeting with home price question.

        Transition: INITIAL → HOME_PRICE
        Completion: 0%
        """
        import random

        self.state = ConversationState.HOME_PRICE

        return ConversationResponse(
            agent_name="Cap-ital America",
            message=(
                "🦸‍♂️ Hi there! I'm Cap-ital America, and I can do this all day... "
                "help you buy your dream home! 🏠✨\n\n"
                "Let's make this quick and easy! Just **4 simple steps** to assemble your loan application.\n\n"
                "**Step 1 of 4**: What's your target home purchase price? "
                "(Don't worry, I've got you covered with quick options!)"
            ),
            action="collect_info",
            collected_data=self.collected_data,
            next_step="Collecting home purchase price",
            completion_percentage=0,
            quick_replies=[
                {"label": "Under $200K", "value": str(random.randint(100000, 200000)), "icon": "🏠"},
                {"label": "$200K - $400K", "value": str(random.randint(200000, 400000)), "icon": "🏡"},
                {"label": "$400K - $600K", "value": str(random.randint(400000, 600000)), "icon": "🏘️"},
                {"label": "$600K - $1M", "value": str(random.randint(600000, 1000000)), "icon": "🏰"},
                {"label": "Over $1M", "value": "1000000", "icon": "🏛️"},
            ],
        )

    def _handle_home_price(self, user_input: str) -> ConversationResponse:
        """
        Handle home price selection.

        Transition: HOME_PRICE → DOWN_PAYMENT
        Completion: 25%
        """
        try:
            # Strip currency formatting ($, commas) before converting to int
            clean_input = user_input.strip().replace("$", "").replace(",", "")
            loan_amount = int(clean_input)
            self.collected_data["loan_amount"] = loan_amount
            self.state = ConversationState.DOWN_PAYMENT

            # Dynamic message based on price range
            if loan_amount < 200000:
                price_reaction = "Smart choice, soldier! Starting strong with a solid foundation! 🏠💪"
            elif loan_amount < 400000:
                price_reaction = "Outstanding! A $200K-$400K home - that's worthy of the shield! 🏡🛡️"
            elif loan_amount < 600000:
                price_reaction = "Now THAT'S what I'm talking about! $400K-$600K - you came ready for battle! 🏘️⚡"
            elif loan_amount < 1000000:
                price_reaction = "Whoa! $600K-$1M? Someone's bringing out the big guns! 🏰💥"
            else:
                price_reaction = "Holy shield! Over $1M? You're going for the Avengers Tower! 🏛️🌟"

            return ConversationResponse(
                agent_name="Cap-ital America",
                message=(
                    f"{price_reaction}\n\n"
                    f"**Step 2 of 4**: How much can you bring to the fight as a down payment?\n\n"
                    f"Remember: The bigger the down payment, the better your loan terms! "
                    f"(Just like training harder makes you stronger! 💪)"
                ),
                action="collect_info",
                collected_data=self.collected_data,
                next_step="Collecting down payment percentage",
                completion_percentage=25,
                quick_replies=[
                    {"label": "5%", "value": "5", "icon": "💵"},
                    {"label": "10%", "value": "10", "icon": "💰"},
                    {"label": "15%", "value": "15", "icon": "💸"},
                    {"label": "20%", "value": "20", "icon": "💎"},
                    {"label": "25%+", "value": "25", "icon": "🏆"},
                ],
            )

        except ValueError:
            logger.warning(f"Invalid loan amount: {user_input}")
            return self._handle_initial()

    def _handle_down_payment(self, user_input: str) -> ConversationResponse:
        """
        Handle down payment percentage selection.

        Transition: DOWN_PAYMENT → INCOME
        Completion: 50%
        """
        try:
            down_payment_percent = int(user_input)
            self.collected_data["down_payment_percent"] = down_payment_percent

            # Calculate actual down payment amount
            loan_amount = self.collected_data["loan_amount"]
            down_payment = int((down_payment_percent / 100) * loan_amount)
            self.collected_data["down_payment"] = down_payment

            self.state = ConversationState.INCOME

            # Dynamic message based on down payment
            if down_payment_percent >= 20:
                down_reaction = (
                    f"🛡️ EXCELLENT! {down_payment_percent}% down (${down_payment:,}) - "
                    f"you came ready for battle! That's the kind of commitment I like to see! 💪"
                )
            elif down_payment_percent >= 15:
                down_reaction = (
                    f"💎 Great work! {down_payment_percent}% down (${down_payment:,}) - "
                    f"solid strategy, soldier! You're building a strong foundation!"
                )
            else:
                down_reaction = (
                    f"💰 Got it! {down_payment_percent}% down (${down_payment:,}) - "
                    f"every journey starts with a first step! Let's keep moving forward!"
                )

            import random

            return ConversationResponse(
                agent_name="Cap-ital America",
                message=(
                    f"{down_reaction}\n\n"
                    f"**Step 3 of 4**: What's your annual household income?\n\n"
                    f"Remember: With great income comes great home-buying power! 🦸‍♂️"
                ),
                action="collect_info",
                collected_data=self.collected_data,
                next_step="Collecting annual income",
                completion_percentage=50,
                quick_replies=[
                    {"label": "$50K - $100K", "value": str(random.randint(50000, 100000)), "icon": "💵"},
                    {"label": "$100K - $250K", "value": str(random.randint(100000, 250000)), "icon": "💰"},
                    {"label": "$250K - $500K", "value": str(random.randint(250000, 500000)), "icon": "💸"},
                    {"label": "> $500K", "value": str(random.randint(500000, 750000)), "icon": "💎"},
                ],
            )

        except ValueError:
            logger.warning(f"Invalid down payment: {user_input}")
            return self._handle_initial()

    def _handle_income(self, user_input: str) -> ConversationResponse:
        """
        Handle annual income selection.

        Transition: INCOME → PERSONAL_INFO
        Completion: 75% (triggers form display in UI)
        """
        try:
            # Strip currency formatting ($, commas) before converting to int
            clean_input = user_input.strip().replace("$", "").replace(",", "")
            annual_income = int(clean_input)
            self.collected_data["annual_income"] = annual_income
            self.state = ConversationState.PERSONAL_INFO

            # Dynamic message based on income
            if annual_income >= 500000:
                income_reaction = "💎 WOW! > $500K income? You're definitely Avengers-level! 🌟"
            elif annual_income >= 250000:
                income_reaction = "💸 Fantastic! $250K-$500K - you're locked and loaded! 🎯"
            elif annual_income >= 100000:
                income_reaction = "💰 Excellent! $100K-$250K - strong financial position, soldier! 🛡️"
            else:
                income_reaction = "💵 Got it! $50K-$100K - building your future starts here! 💪"

            return ConversationResponse(
                agent_name="Cap-ital America",
                message=(
                    f"{income_reaction}\n\n"
                    f"**Final step (4 of 4)**: I need your personal details to assemble your application! 🦸‍♂️\n\n"
                    f"📋 Fill in the form that just appeared below with:\n"
                    f"• Your full name\n"
                    f"• Email address\n"
                    f"• Last 4 digits of your ID\n\n"
                    f"✨ **Testing?** Use the 'Generate Dummy Data' button for instant Avengers-themed test data!"
                ),
                action="collect_info",
                collected_data=self.collected_data,
                next_step="Collecting personal information (form will appear)",
                completion_percentage=75,  # This triggers form display in UI
                # NO quick_replies - form will handle this
            )

        except ValueError:
            logger.warning(f"Invalid income: {user_input}")
            return self._handle_initial()

    def _handle_personal_info(self, user_input: str) -> ConversationResponse:
        """
        Handle personal information form submission.

        Transition: PERSONAL_INFO → PROCESSING
        Completion: 100%
        Action: ready_for_processing (triggers LoanProcessingPipeline)

        Args:
            user_input: JSON string with {name, email, idLast4}
        """
        import json

        try:
            # Parse form data
            form_data = json.loads(user_input)

            self.collected_data["applicant_name"] = form_data.get("name")
            self.collected_data["email"] = form_data.get("email")
            self.collected_data["id_last_four"] = form_data.get("idLast4")
            self.collected_data["loan_purpose"] = "home_purchase"  # Always home purchase

            self.state = ConversationState.PROCESSING

            return ConversationResponse(
                agent_name="Cap-ital America",
                message=(
                    "🦸‍♂️⚡ **DEFENDERS... ASSEMBLE!** ⚡🦸‍♂️\n\n"
                    f"{self.collected_data['applicant_name']}, your application is complete "
                    f"and ready for deployment! 🛡️\n\n"
                    f"My specialist team is suited up and standing by:\n"
                    f"• 🔍 **Intake Agent** - Application validation\n"
                    f"• 💳 **Credit Agent** - Credit assessment\n"
                    f"• 💼 **Income Agent** - Employment verification\n"
                    f"• ⚖️ **Risk Agent** - Comprehensive risk evaluation\n\n"
                    f"**I can do this all day...** and I'll have your decision back faster "
                    f"than you can say 'Wakanda Forever'! ⏱️\n\n"
                    f"Hang tight, soldier! The team is on it! 💪🌟"
                ),
                action="ready_for_processing",  # This triggers LoanProcessingPipeline
                collected_data=self.collected_data,
                next_step="Starting sequential agent processing workflow",
                completion_percentage=100,
            )

        except (json.JSONDecodeError, KeyError):
            logger.error(f"Invalid personal info data: {user_input}", exc_info=True)
            return ConversationResponse(
                agent_name="Cap-ital America",
                message=(
                    "Whoa there! Looks like some data didn't come through properly. 🦸‍♂️\n\n"
                    "Could you fill out the form again? I need your name, email, and ID to proceed!"
                ),
                action="need_clarification",
                collected_data=self.collected_data,
                next_step="Waiting for personal information",
                completion_percentage=75,
            )

    def reset(self) -> None:
        """Reset state machine to initial state.

        Clears all collected data and returns to INITIAL state,
        ready for a new conversation flow.
        """
        self.state = ConversationState.INITIAL
        self.collected_data = {}
        logger.info("State machine reset to INITIAL")


__all__ = ["ConversationStateMachine", "ConversationState"]
