"""
Mock unified workflow for testing API integration without agent_framework.

This module provides the same interface as the unified_workflow but uses
mock implementations so we can test the API endpoints and UI integration.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from loan_avengers.utils.observability import Observability

logger = Observability.get_logger("mock_unified_workflow")


class MockAgentThread:
    """Mock AgentThread for testing."""

    def __init__(self):
        self.thread_id = f"thread_{datetime.now().strftime('%H%M%S')}"
        self.conversation_history = []

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})


class MockSharedState:
    """Mock SharedState for testing."""

    def __init__(self):
        self._state = {}

    async def set(self, key: str, value: Any):
        self._state[key] = value

    async def get(self, key: str):
        return self._state.get(key, {})


class WorkflowResponse:
    """Response model for unified workflow streaming events."""

    def __init__(
        self,
        agent_name: str,
        message: str,
        phase: str,
        completion_percentage: int,
        collected_data: dict[str, Any] = None,
        action: str = "processing",
        metadata: dict[str, Any] = None,
    ):
        self.agent_name = agent_name
        self.message = message
        self.phase = phase
        self.completion_percentage = completion_percentage
        self.collected_data = collected_data or {}
        self.action = action
        self.metadata = metadata or {}


class MockSequentialLoanWorkflow:
    """Mock unified workflow that simulates the real implementation."""

    def __init__(self, chat_client=None):
        """Initialize mock workflow."""
        logger.info("MockUnifiedLoanWorkflow initialized")

    async def process_conversation(
        self, user_message: str, thread: MockAgentThread, shared_state: MockSharedState = None
    ) -> AsyncGenerator[WorkflowResponse, None]:
        """Mock conversation processing through workflow phases."""

        if not shared_state:
            shared_state = MockSharedState()

        # Add user message to thread
        thread.add_message("user", user_message)

        # Simulate collecting application data from conversation
        collected_data = await self._extract_application_data(user_message, shared_state)

        # Check if we have enough data to proceed
        required_fields = ["loan_amount", "applicant_name", "annual_income"]
        has_all_data = all(field in collected_data for field in required_fields)

        # Determine which phase we're in
        if not has_all_data:
            # Stay in collecting phase
            phases_to_process = [("collecting", "Coordinator_Collector", "Hi! I'm your Loan Coordinator! 😊 ")]
        else:
            # Process through all phases
            phases_to_process = [
                (
                    "validating",
                    "Intake_Validator",
                    "Intake Agent here. I'm reviewing your application details carefully. ",
                ),
                (
                    "assessing_credit",
                    "Credit_Assessor",
                    "Analyzing your creditworthiness based on the information provided. ",
                ),
                ("verifying_income", "Income_Verifier", "Verifying your income and employment details. "),
                ("deciding", "Risk_Analyzer", "Final risk analysis complete. Making loan decision. "),
            ]

        # Process through current phases
        for _i, (phase, agent_name, base_response) in enumerate(phases_to_process):
            # Customize response based on user message and phase
            if phase == "collecting":
                # Build a conversational response based on what's missing
                missing_fields = []
                if "loan_amount" not in collected_data:
                    missing_fields.append("loan amount")
                if "applicant_name" not in collected_data:
                    missing_fields.append("your name")
                if "annual_income" not in collected_data:
                    missing_fields.append("annual income")

                # Acknowledge what was just shared
                previous_data = await shared_state.get("previous_data") or {}
                if "loan_amount" in collected_data and "loan_amount" not in previous_data:
                    message = f"{base_response}Got it! ${collected_data['loan_amount']:,.0f} for your loan. "
                elif "applicant_name" in collected_data:
                    message = f"{base_response}Nice to meet you, {collected_data['applicant_name']}! "
                elif "annual_income" in collected_data:
                    message = f"{base_response}Thanks for sharing your income information! "
                else:
                    message = f"{base_response}I can see you're interested in a loan. "

                # Ask for next missing piece
                if missing_fields:
                    if "your name" in missing_fields:
                        message += "What's your full name?"
                    elif "loan amount" in missing_fields:
                        message += "How much would you like to borrow?"
                    elif "annual income" in missing_fields:
                        message += "What's your annual income?"
                else:
                    message += "Great! I have all the basic information. Let me process your application now!"

                # Store current data for next comparison
                await shared_state.set("previous_data", collected_data.copy())

            elif phase == "deciding":
                # Mock decision based on collected data
                loan_amount = collected_data.get("loan_amount", 0)
                income = collected_data.get("annual_income", 0)

                if loan_amount and income and loan_amount <= income * 5:
                    decision = "APPROVED"
                    message = f"{base_response}Based on your financial profile, "
                    message += "your loan application has been APPROVED! 🎉"
                else:
                    decision = "NEEDS_MORE_INFO"
                    message = f"{base_response}We need additional information to complete your application review."

                await shared_state.set("final_decision", decision)
            else:
                message = f"{base_response}Processing your application information."

            # Add agent response to thread
            thread.add_message("assistant", message)

            # Calculate completion percentage based on phase and data collected
            if phase == "collecting":
                # In collecting phase, base completion on data gathered
                data_progress = (len(collected_data) / 3) * 40  # 0-40% for collecting
                completion = int(data_progress)
            elif phase == "validating":
                completion = 50
            elif phase == "assessing_credit":
                completion = 70
            elif phase == "verifying_income":
                completion = 85
            else:  # deciding
                completion = 100

            # Determine action
            action = "completed" if phase == "deciding" else "processing"
            if phase == "collecting":
                action = "collect_info" if len(collected_data) < 3 else "processing"

            # Create and yield response
            response = WorkflowResponse(
                agent_name=agent_name,
                message=message,
                phase=phase,
                completion_percentage=completion,
                collected_data=collected_data,
                action=action,
                metadata={"phase": phase, "agent": agent_name},
            )

            yield response

            # Simulate processing delay
            await asyncio.sleep(0.1)

    async def _extract_application_data(self, user_message: str, shared_state: MockSharedState) -> dict[str, Any]:
        """Extract application data from user message."""
        data = await shared_state.get("application_data") or {}
        import re

        message_lower = user_message.lower()

        # Extract loan amount - look for numbers with currency indicators
        # Only extract if we don't already have it, or if context suggests it's the loan amount
        if "loan_amount" not in data:
            if "$" in user_message or "dollar" in message_lower or "k" in message_lower:
                amounts = re.findall(r"\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*k?", user_message.replace(",", ""))
                if amounts:
                    try:
                        amount = float(amounts[0])
                        # If it ends with 'k', multiply by 1000
                        if "k" in user_message.lower():
                            amount *= 1000
                        data["loan_amount"] = amount
                    except ValueError:
                        pass
            # Also check if message is just a number (direct answer to "how much")
            # Only if we have a name but no loan amount yet
            elif "applicant_name" in data and re.match(
                r"^\d+(?:,\d+)*(?:\.\d+)?$", user_message.strip().replace(",", "")
            ):
                try:
                    data["loan_amount"] = float(user_message.strip().replace(",", ""))
                except ValueError:
                    pass

        # Extract name - multiple patterns
        name_extracted = False

        # Pattern 1: "my name is...", "i'm...", "i am..."
        if "my name is" in message_lower or "i'm" in message_lower or "i am" in message_lower:
            name_match = re.search(r"(?:my name is|i\'m|i am)\s+([a-zA-Z\s]+?)(?:\.|$|,|\s+and\s+)", message_lower)
            if name_match:
                data["applicant_name"] = name_match.group(1).strip().title()
                name_extracted = True

        # Pattern 2: If message looks like just a name (2-4 capitalized words, no numbers)
        if not name_extracted and not any(char.isdigit() for char in user_message):
            # Check if it looks like a name (1-4 words, reasonable length)
            words = user_message.strip().split()
            if 1 <= len(words) <= 4 and all(2 <= len(w) <= 20 for w in words):
                # Make sure it doesn't contain common non-name words or greetings
                excluded_words = {
                    "loan",
                    "need",
                    "want",
                    "help",
                    "house",
                    "car",
                    "mortgage",
                    "money",
                    "dollars",
                    "income",
                    "year",
                    "hi",
                    "hello",
                    "hey",
                    "yes",
                    "no",
                    "okay",
                    "thanks",
                    "please",
                    "sure",
                }
                # Also require at least 2 words for a name, or 1 word that's at least 4 chars
                is_valid_name = (len(words) >= 2) or (len(words) == 1 and len(words[0]) >= 4)
                if is_valid_name and not any(word.lower() in excluded_words for word in words):
                    data["applicant_name"] = user_message.strip().title()
                    name_extracted = True

        # Extract income
        income_extracted = False

        # Pattern 1: Look for income keywords with numbers
        if any(word in message_lower for word in ["make", "earn", "income", "salary"]):
            income_amounts = re.findall(r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|per year|annually)?", message_lower)
            for amount in income_amounts:
                try:
                    income = float(amount.replace(",", ""))
                    if income < 1000:  # Assume it's in thousands if < 1000
                        income *= 1000
                    data["annual_income"] = income
                    income_extracted = True
                    break
                except ValueError:
                    pass

        # Pattern 2: If just a plain number and we're asking about income, assume it's salary
        # Only do this if we already have name and loan amount (context clue we're asking about income)
        if not income_extracted and "applicant_name" in data and "loan_amount" in data:
            if re.match(r"^\$?\d+(?:,\d+)*(?:\.\d+)?\s*k?$", user_message.strip()):
                try:
                    income = float(re.sub(r"[^\d.]", "", user_message))
                    if "k" in message_lower and income < 1000:
                        income *= 1000
                    elif income < 1000:  # Assume thousands if small number
                        income *= 1000
                    data["annual_income"] = income
                    income_extracted = True
                except ValueError:
                    pass

        # Extract email
        import re

        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", user_message)
        if email_match:
            data["email"] = email_match.group(0)

        # Extract phone
        phone_match = re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", user_message)
        if phone_match:
            data["phone"] = phone_match.group(0)

        # Store updated data
        await shared_state.set("application_data", data)

        return data


# Create the workflow instance alias that the API expects
UnifiedLoanWorkflow = MockUnifiedLoanWorkflow  # noqa: F811


__all__ = ["MockUnifiedLoanWorkflow", "UnifiedLoanWorkflow", "WorkflowResponse", "MockAgentThread", "MockSharedState"]
