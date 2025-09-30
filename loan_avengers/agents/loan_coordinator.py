"""
Loan Coordinator Agent using Microsoft Agent Framework.

Coordinates the entire loan application experience through natural conversation,
collecting application details and managing handoffs to the specialist team.
"""

from __future__ import annotations

import json
from typing import Any

from agent_framework import AgentRunResponse, AgentThread, ChatAgent
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential
from pydantic import BaseModel, Field

from loan_avengers.models.application import EmploymentStatus, LoanApplication, LoanPurpose
from loan_avengers.models.responses import AgentResponse, UsageStats
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("coordinator")


class CoordinatorResponse(BaseModel):
    """Structured response from loan coordinator agent."""

    agent_name: str = Field(default="Coordinator")
    message: str = Field(description="Coordinator's conversational response")
    action: str = Field(description="Current action: collect_info|ready_for_processing|need_clarification")
    collected_data: dict[str, Any] = Field(default_factory=dict, description="Application data collected so far")
    next_step: str = Field(description="Brief description of what happens next")
    completion_percentage: int = Field(ge=0, le=100, description="Percentage of application completion")


class LoanCoordinator:
    """
    Loan Coordinator for conversational application collection.

    Responsibilities:
    - Natural conversation-based information gathering
    - Application data collection and validation
    - Team coordination and workflow handoffs
    - User experience orchestration throughout the loan process

    Architecture:
    - Uses Azure AI Foundry with DefaultAzureCredential (Entra ID)
    - No MCP tools needed - focused on conversation and coordination
    - Structured JSON responses for UI integration
    - AgentThread-based conversation context management
    """

    def __init__(
        self,
        chat_client: FoundryChatClient | None = None,
        temperature: float = 0.7,  # Higher for more conversational responses
        max_tokens: int = 800,  # Longer for detailed explanations
    ):
        """
        Initialize Loan Coordinator.

        Args:
            chat_client: Azure AI Foundry chat client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for more natural conversation
            max_tokens: Maximum tokens for response (longer for explanations)
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = FoundryChatClient(async_credential=DefaultAzureCredential())

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("coordinator")

        # Store agent configuration
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info("LoanCoordinator initialized", extra={"agent": "coordinator"})

    async def process_conversation(
        self, user_message: str, thread: AgentThread | None = None, current_data: dict[str, Any] | None = None
    ) -> AgentResponse[CoordinatorResponse]:
        """
        Process user conversation and collect loan application data.

        Args:
            user_message: The user's message in the conversation
            thread: Optional conversation thread for context
            current_data: Currently collected application data

        Returns:
            AgentResponse containing coordinator's structured response with:
            - Conversational message
            - Updated collected data
            - Action status and next steps
            - Completion percentage
        """
        try:
            # Create ChatAgent instance
            agent = ChatAgent(
                chat_client=self.chat_client,
                instructions=self.instructions,
                name="Loan Orchestrator",
                description="Coordinator for conversational loan applications",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=CoordinatorResponse,  # Structured JSON response
            )

            # Build context message with conversation and current state
            current_data = current_data or {}
            context_message = f"""User message: "{user_message}"

Current application data collected:
{json.dumps(current_data, indent=2)}

Please respond with your next conversational message and update the collected data based on the user's input. Follow your persona guidelines for natural conversation flow."""

            logger.info(
                "Processing coordinator conversation",
                extra={
                    "agent": "coordinator",
                    "user_message_length": len(user_message),
                    "current_completion": len([v for v in current_data.values() if v is not None]),
                },
            )

            # Process with Microsoft Agent Framework
            response: AgentRunResponse = await agent.run(context_message, thread=thread)

            # Agent Framework automatically parses response into CoordinatorResponse
            coordinator_response = response.value

            if coordinator_response is None:
                # Fallback if parsing failed
                last_message = response.messages[-1] if response.messages else None
                content = (
                    last_message.text if last_message else "I'm having trouble processing that. Could you try again?"
                )

                logger.warning(
                    "Coordinator structured response parsing failed",
                    extra={
                        "response_preview": content[:200],
                    },
                )

                # Create fallback response
                coordinator_response = CoordinatorResponse(
                    agent_name="Coordinator",
                    message="I'm sorry, I had a small technical hiccup there! Could you please repeat what you said? I'm here to help you with your loan application. 😊",
                    action="need_clarification",
                    collected_data=current_data,
                    next_step="Waiting for user to repeat their message",
                    completion_percentage=self._calculate_completion(current_data),
                )

            # Build usage stats
            usage = UsageStats(
                input_tokens=response.usage_details.input_token_count if response.usage_details else None,
                output_tokens=response.usage_details.output_token_count if response.usage_details else None,
                total_tokens=response.usage_details.total_token_count if response.usage_details else None,
            )

            # Create agent response
            result = AgentResponse(
                assessment=coordinator_response,
                usage_stats=usage,
                response_id=response.response_id,
                created_at=response.created_at,
                agent_name="coordinator",
                application_id=None,  # No specific application ID yet
            )

            logger.info(
                "Coordinator conversation processed",
                extra={
                    "agent": "coordinator",
                    "action": coordinator_response.action,
                    "completion_percentage": coordinator_response.completion_percentage,
                    "tokens_used": usage.total_tokens,
                },
            )

            return result

        except Exception:
            logger.error(
                "Coordinator conversation processing failed",
                extra={"agent": "coordinator"},
                exc_info=True,
            )

            # Create error response
            error_response = CoordinatorResponse(
                agent_name="Coordinator",
                message="Oops! I encountered a technical issue, but don't worry - I'm back and ready to help! What can I assist you with for your loan application today? 🌟",
                action="need_clarification",
                collected_data=current_data or {},
                next_step="Waiting for user input to continue",
                completion_percentage=self._calculate_completion(current_data or {}),
            )

            return AgentResponse(
                assessment=error_response,
                usage_stats=UsageStats(input_tokens=None, output_tokens=None, total_tokens=None),
                response_id=None,
                created_at=None,
                agent_name="riley",
                application_id=None,
            )

    def _calculate_completion(self, data: dict[str, Any]) -> int:
        """Calculate completion percentage based on collected data."""
        required_fields = [
            "applicant_name",
            "email",
            "phone",
            "date_of_birth",
            "loan_amount",
            "loan_purpose",
            "annual_income",
            "employment_status",
        ]

        filled_fields = sum(1 for field in required_fields if data.get(field) is not None)
        return min(100, (filled_fields * 100) // len(required_fields))

    def create_loan_application(self, collected_data: dict[str, Any]) -> LoanApplication:
        """
        Convert collected data into a validated LoanApplication object.

        Args:
            collected_data: Dictionary of collected application data

        Returns:
            Validated LoanApplication instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            # Map collected data to LoanApplication fields
            application_data = {
                "application_id": f"LN{hash(collected_data.get('email', 'unknown'))}"[-10:],
                "applicant_name": collected_data.get("applicant_name"),
                "applicant_id": str(hash(collected_data.get("email", "unknown"))),  # Generate UUID-like ID
                "email": collected_data.get("email"),
                "phone": collected_data.get("phone"),
                "date_of_birth": collected_data.get("date_of_birth"),
                "loan_amount": collected_data.get("loan_amount"),
                "loan_purpose": LoanPurpose(collected_data.get("loan_purpose"))
                if collected_data.get("loan_purpose")
                else None,
                "loan_term_months": collected_data.get("loan_term_months", 360),  # Default 30-year
                "annual_income": collected_data.get("annual_income"),
                "employment_status": EmploymentStatus(collected_data.get("employment_status"))
                if collected_data.get("employment_status")
                else None,
                "employer_name": collected_data.get("employer_name"),
                "months_employed": collected_data.get("months_employed"),
            }

            # Create and validate LoanApplication
            application = LoanApplication(**application_data)

            logger.info(
                "LoanApplication created from coordinator data",
                extra={
                    "application_id": application.application_id,
                    "loan_amount": float(application.loan_amount),
                    "applicant_name": application.applicant_name,
                },
            )

            return application

        except Exception as e:
            logger.error(
                "Failed to create LoanApplication from collected data",
                extra={"collected_data": collected_data},
                exc_info=True,
            )
            raise ValueError(f"Invalid application data: {str(e)}")


__all__ = ["LoanCoordinator", "CoordinatorResponse"]
