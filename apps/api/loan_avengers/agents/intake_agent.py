"""
Intake Agent - Application Validator using Microsoft Agent Framework.

Performs lightning-fast application validation and routing with precision.
Personality and display name are defined in the persona file for UI flexibility.
"""

from __future__ import annotations

import os

from agent_framework import AgentRunResponse, AgentThread, ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import AgentResponse, IntakeAssessment, UsageStats
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("intake_agent")


class IntakeAgent:
    """
    Intake Agent - Application Validator for the Loan Processing System.

    Responsibilities:
    - Lightning-fast application data validation
    - Smart routing to optimal specialist workflow
    - Quality assurance setup for downstream specialists
    - MCP tool integration for verification services

    Architecture:
    - Uses Azure AI Foundry with DefaultAzureCredential (Entra ID)
    - MCP tools connected via async context manager per request
    - Structured logging with masked sensitive data (application_id[:8]***)

    Note: Personality and display names are defined in persona files for flexibility.
    """

    def __init__(
        self,
        chat_client: FoundryChatClient | None = None,
        temperature: float = 0.1,
        max_tokens: int = 500,
    ):
        """
        Initialize the Intake Agent.

        Creates MCP tool connection for application verification service.
        ChatAgent is created per-request to ensure proper MCP tool lifecycle.

        Args:
            chat_client: Azure AI Foundry chat client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for the model (low for consistency)
            max_tokens: Maximum tokens for response (small for speed)

        Environment:
            Requires FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME.
            Authentication via Azure CLI (az login) or Managed Identity.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = FoundryChatClient(async_credential=DefaultAzureCredential())

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("intake")

        # Create MCP tool for application verification server
        # Note: Tool connection is deferred until process_application is called
        mcp_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL", "http://localhost:8010/mcp")
        self.mcp_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=mcp_url,
            description="Application verification service for basic parameter validation",
            load_tools=True,
            load_prompts=False,
        )

        # Store agent configuration for later initialization
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info("IntakeAgent initialized", extra={"agent": "intake"})

    async def process_application(
        self, application: LoanApplication, thread: AgentThread | None = None
    ) -> AgentResponse[IntakeAssessment]:
        """
        Process loan application for intake validation and routing.

        Uses async context manager to connect MCP tools and create ChatAgent per request.
        This ensures proper tool discovery and lifecycle management.

        Args:
            application: The loan application to process
            thread: Optional conversation thread for context (conversation history)

        Returns:
            AgentResponse: Pydantic model containing:
            - assessment: IntakeAssessment with validation and routing
            - usage_stats: UsageStats with token metrics
            - response_id: Unique identifier
            - created_at: Timestamp
            - agent_name: "intake"
            - application_id: Application ID

        Note:
            Logs mask sensitive data - application_id logged as "[:8]***"
        """
        try:
            # Connect to MCP tool and create agent within async context
            async with self.mcp_tool:
                # Log MCP tool connection details after connection is established
                logger.debug(
                    "MCP tool connected",
                    extra={
                        "tool_count": len(self.mcp_tool.functions),
                        "application_id": Observability.mask_application_id(application.application_id),
                    },
                )

                # Create ChatAgent with connected MCP tool
                agent = ChatAgent(
                    chat_client=self.chat_client,
                    instructions=self.instructions,
                    name="Intake_Agent",
                    description="Sharp-eyed application validator with efficient humor",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format=IntakeAssessment,
                    tools=[self.mcp_tool],
                )

                # Create message with JSON-serialized application data
                message = f"""Process this loan application for intake validation and routing:

{application.model_dump_json(indent=2)}

Provide your assessment as valid JSON matching the required output format from your instructions."""

                # Process with Microsoft Agent Framework (with optional conversation context)
                logger.info(
                    "Processing application",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "agent": "intake",
                    },
                )

                response: AgentRunResponse = await agent.run(message, thread=thread)

                # Log tool usage at debug level with safe extraction
                tool_calls = Observability.extract_tool_calls_from_response(response.messages)
                if tool_calls:
                    logger.debug(
                        "Tools called",
                        extra={
                            "tools": tool_calls,
                            "application_id": Observability.mask_application_id(application.application_id),
                        },
                    )

                # Agent Framework automatically parses response into IntakeAssessment
                assessment = response.value  # Already parsed as IntakeAssessment object

                if assessment is None:
                    # Fallback if parsing failed - extract from text
                    last_message = response.messages[-1] if response.messages else None
                    content = last_message.text if last_message else "No response"
                    logger.warning(
                        "Structured response parsing failed",
                        extra={
                            "application_id": Observability.mask_application_id(application.application_id),
                            "response_preview": content[:200],
                        },
                    )

                    # Create fallback assessment with structured response
                    assessment = IntakeAssessment(
                        validation_status="FAILED",
                        routing_decision="MANUAL",
                        confidence_score=0.0,
                        processing_notes=f"Eagle eye scan encountered parsing issue: {content[:200]}...",
                        data_quality_score=0.0,
                        specialist_name="Intake Agent",
                        celebration_message="🦅 Eagle eyes spotted something! Let me fix this with precision!",
                        encouragement_note="Technical hiccup detected - these eagle eyes will sort it out!",
                        next_step_preview="Getting this sharpened up for the Dream Team!",
                        animation_type="pulse",
                        celebration_level="mild",
                    )

                # Build Pydantic response model (no dict conversion needed!)
                usage = UsageStats(
                    input_tokens=response.usage_details.input_token_count if response.usage_details else None,
                    output_tokens=response.usage_details.output_token_count if response.usage_details else None,
                    total_tokens=response.usage_details.total_token_count if response.usage_details else None,
                )

                result = AgentResponse(
                    assessment=assessment,  # Keep as Pydantic model!
                    usage_stats=usage,
                    response_id=response.response_id,
                    created_at=response.created_at,
                    agent_name="intake",
                    application_id=application.application_id,
                )

                logger.info(
                    "Application processed",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "agent": "intake",
                        "validation_status": assessment.validation_status,
                        "routing_decision": assessment.routing_decision,
                        "tokens_used": usage.total_tokens,
                    },
                )

                return result

        except Exception as e:
            logger.error(
                "Application processing failed",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "agent": "intake",
                },
                exc_info=True,
            )
            # Create error assessment with structured response
            error_assessment = IntakeAssessment(
                validation_status="FAILED",
                routing_decision="MANUAL",
                confidence_score=0.0,
                processing_notes=f"Processing error: {str(e)}",
                data_quality_score=0.0,
                specialist_name="Intake Agent",
                celebration_message="Processing encountered a technical issue, let me refocus!",
                encouragement_note="Technical hiccup detected - but your data still has potential!",
                next_step_preview="Working to get this sorted for the next step!",
                animation_type="pulse",
                celebration_level="mild",
            )

            # Return error response as Pydantic model
            return AgentResponse(
                assessment=error_assessment,
                usage_stats=UsageStats(input_tokens=None, output_tokens=None, total_tokens=None),
                response_id=None,
                created_at=None,
                agent_name="intake",
                application_id=application.application_id,
            )


__all__ = ["IntakeAgent"]
