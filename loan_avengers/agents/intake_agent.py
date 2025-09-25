"""
John "The Eagle Eye" - Application Validator using Microsoft Agent Framework.

John performs lightning-fast application validation and routing with eagle precision
and efficient humor. Part of Alisha's Dream Team for revolutionary loan processing.
"""

from __future__ import annotations

from typing import Any

from agent_framework import AgentRunResponse, AgentThread, ChatAgent
from agent_framework_azure import AzureChatClient

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import IntakeAssessment
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("intake_agent")


class IntakeAgent:
    """
    John "The Eagle Eye" - Application Validator for Alisha's Dream Team.

    Responsibilities:
    - Lightning-fast application data validation with eagle precision
    - Smart routing to optimal Dream Team specialist experience
    - Quality assurance setup for downstream specialists
    - Streaming progress updates with efficient humor
    """

    def __init__(
        self,
        chat_client: AzureChatClient | None = None,
        temperature: float = 0.1,  # Low temperature for consistent routing decisions
        max_tokens: int = 500,  # Small response for speed
    ):
        """
        Initialize the Intake Agent.

        Args:
            chat_client: Azure OpenAI chat client. If None, will be created from environment.
            temperature: Sampling temperature for the model (low for consistency)
            max_tokens: Maximum tokens for response (small for speed)
        """
        # Create chat client if not provided
        self.chat_client = chat_client or AzureChatClient()

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("intake")

        # Create the Microsoft Agent Framework ChatAgent with structured response
        self.agent = ChatAgent(
            chat_client=self.chat_client,
            instructions=self.instructions,
            name="John - The Eagle Eye",
            description="Sharp-eyed application validator with efficient humor",
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=IntakeAssessment,  # Structured response parsing
            tools=None,  # Optimize for speed - no tools needed for intake
        )

        logger.info("John 'The Eagle Eye' initialized with Microsoft Agent Framework")

    async def process_application(
        self, application: LoanApplication, thread: AgentThread | None = None
    ) -> dict[str, Any]:
        """
        Process loan application for intake validation and routing.

        Args:
            application: The loan application to process
            thread: Optional conversation thread for context (conversation history)

        Returns:
            Dictionary containing:
            - assessment: Sarah's enthusiastic routing decision and validation results
            - usage_stats: Token usage and performance metrics
            - response_id: Unique response identifier for tracing
        """
        try:
            # Convert Pydantic model to JSON string for agent processing
            application_json = application.model_dump_json(indent=2)

            # Create the message for the agent
            message = f"""Process this loan application for intake validation and routing:

{application_json}

Provide your assessment as valid JSON matching the required output format from your instructions."""

            # Process with Microsoft Agent Framework (with optional conversation context)
            logger.info(f"🦅 John's Eagle Eye scanning application {application.application_id}")

            response: AgentRunResponse = await self.agent.run(message, thread=thread)

            # Agent Framework automatically parses response into IntakeAssessment
            assessment = response.value  # Already parsed as IntakeAssessment object

            if assessment is None:
                # Fallback if parsing failed - extract from text
                last_message = response.messages[-1] if response.messages else None
                content = last_message.text if last_message else "No response"
                logger.warning(f"Failed to parse structured response, got: {content}")

                # Create fallback assessment with John's eagle-eyed efficiency
                assessment = IntakeAssessment(
                    validation_status="FAILED",
                    routing_decision="MANUAL",
                    confidence_score=0.0,
                    processing_notes=f"Eagle eye scan encountered parsing issue: {content[:200]}...",
                    data_quality_score=0.0,
                    specialist_name="John",
                    celebration_message="🦅 Eagle eyes spotted something! Let me fix this with precision!",
                    encouragement_note="Technical hiccup detected - these eagle eyes will sort it out!",
                    next_step_preview="Getting this sharpened up for the Dream Team!",
                    animation_type="pulse",
                    celebration_level="mild",
                )

            # Build comprehensive response with observability data
            result = {
                "assessment": assessment.model_dump(),  # Convert Pydantic model to dict
                "usage_stats": {
                    "input_tokens": response.usage_details.input_token_count if response.usage_details else None,
                    "output_tokens": response.usage_details.output_token_count if response.usage_details else None,
                    "total_tokens": response.usage_details.total_token_count if response.usage_details else None,
                },
                "response_id": response.response_id,
                "created_at": response.created_at,
                "agent_name": "intake",
                "application_id": application.application_id,
            }

            logger.info(
                f"Completed intake processing for {application.application_id}. "
                f"Tokens used: {result['usage_stats']['total_tokens']}"
            )

            return result

        except Exception as e:
            # Log error - the @use_agent_observability decorator handles telemetry automatically
            logger.error(f"Error processing application {application.application_id}: {e}", exc_info=True)
            # Create error assessment with John's eagle-eyed efficiency
            error_assessment = IntakeAssessment(
                validation_status="FAILED",
                routing_decision="MANUAL",
                confidence_score=0.0,
                processing_notes=f"Eagle eye processing failed: {str(e)}",
                data_quality_score=0.0,
                specialist_name="John",
                celebration_message="🦅 Eagle eyes spotted a technical issue! Let me refocus these eyes!",
                encouragement_note="Technical hiccup detected - but your data still has potential!",
                next_step_preview="Sharpening focus to get this sorted for the Dream Team!",
                animation_type="pulse",
                celebration_level="mild",
            )

            # Return error response with same structure
            return {
                "assessment": error_assessment.model_dump(),
                "usage_stats": {"input_tokens": None, "output_tokens": None, "total_tokens": None},
                "response_id": None,
                "created_at": None,
                "agent_name": "intake",
                "application_id": application.application_id,
            }


__all__ = ["IntakeAgent"]
