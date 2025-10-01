"""
Credit Agent - Creditworthiness Analysis using Microsoft Agent Framework.

Performs comprehensive credit analysis, risk scoring, and debt-to-income calculations.
Personality and display name are defined in the persona file for UI flexibility.
"""

from __future__ import annotations

import os

from agent_framework import AgentRunResponse, AgentThread, ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import AgentResponse, CreditAssessment, UsageStats
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("credit_agent")


class CreditAgent:
    """
    Credit Agent - Creditworthiness Analyst for the Loan Processing System.

    Responsibilities:
    - Comprehensive credit history analysis and risk categorization
    - Credit score validation and interpretation
    - Debt-to-income ratio calculations and affordability assessment
    - Identity verification through credit bureau integration
    - MCP tool integration for credit reports and financial calculations

    Architecture:
    - Uses Azure AI Foundry with DefaultAzureCredential (Entra ID)
    - Two MCP tools: application_verification and financial_calculations
    - Structured logging with masked sensitive data (application_id[:8]***)
    - Async context managers for proper MCP tool lifecycle

    Note: Personality and display names are defined in persona files for flexibility.
    """

    def __init__(
        self,
        chat_client: AzureAIAgentClient | None = None,
        temperature: float = 0.2,
        max_tokens: int = 600,
    ):
        """
        Initialize the Credit Agent.

        Creates MCP tool connections for credit verification and financial calculations.
        ChatAgent is created per-request to ensure proper MCP tool lifecycle.

        Args:
            chat_client: Azure AI Agent client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for the model (low for consistency)
            max_tokens: Maximum tokens for response

        Environment:
            Requires AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME.
            MCP_APPLICATION_VERIFICATION_URL for credit report access.
            MCP_FINANCIAL_CALCULATIONS_URL for DTI and affordability calculations.
            Authentication via Azure CLI (az login) or Managed Identity.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = AzureAIAgentClient(async_credential=DefaultAzureCredential())

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("credit")

        # Create MCP tools for credit assessment
        # Tool 1: Application verification for credit reports and identity verification
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        self.verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Credit report and identity verification services",
            load_tools=True,
            load_prompts=False,
        )

        # Tool 2: Financial calculations for DTI and affordability analysis
        calculations_url = os.getenv("MCP_FINANCIAL_CALCULATIONS_URL")
        self.calculations_tool = MCPStreamableHTTPTool(
            name="financial-calculations",
            url=calculations_url,
            description="Financial calculations for credit analysis",
            load_tools=True,
            load_prompts=False,
        )

        # Store agent configuration for later initialization
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(
            "CreditAgent initialized",
            extra={"agent": "credit", "mcp_servers": ["application_verification", "financial_calculations"]},
        )

    async def process_application(
        self,
        application: LoanApplication,
        thread: AgentThread | None = None,
        previous_assessments: list[AgentResponse] | None = None,
    ) -> AgentResponse[CreditAssessment]:
        """
        Process loan application for credit analysis.

        Uses async context managers to connect MCP tools and create ChatAgent per request.
        This ensures proper tool discovery and lifecycle management.

        Args:
            application: The loan application to process
            thread: Optional conversation thread for context (conversation history)
            previous_assessments: Optional list of assessments from previous agents (e.g., Intake)

        Returns:
            AgentResponse: Pydantic model containing:
            - assessment: CreditAssessment with credit analysis
            - usage_stats: UsageStats with token metrics
            - response_id: Unique identifier
            - created_at: Timestamp
            - agent_name: "credit"
            - application_id: Application ID

        Note:
            Logs mask sensitive data - application_id logged as "[:8]***"
        """
        try:
            # Connect to both MCP tools within async contexts
            async with self.verification_tool, self.calculations_tool:
                # Log MCP tool connection details
                logger.debug(
                    "MCP tools connected",
                    extra={
                        "tool_count": len(self.verification_tool.functions) + len(self.calculations_tool.functions),
                        "application_id": Observability.mask_application_id(application.application_id),
                    },
                )

                # Create ChatAgent with connected MCP tools
                agent = ChatAgent(
                    chat_client=self.chat_client,
                    instructions=self.instructions,
                    name="Credit_Assessor",
                    description="Expert credit analyst with celebratory personality",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format=CreditAssessment,
                    tools=[self.verification_tool, self.calculations_tool],
                )

                # Build message with application data and optional previous context
                context_info = ""
                if previous_assessments:
                    context_info = "\n\nPrevious Agent Assessments:\n"
                    for prev in previous_assessments:
                        context_info += f"\n{prev.agent_name}: {prev.assessment.processing_notes[:200]}..."

                message = f"""Analyze the creditworthiness for this loan application:

{application.model_dump_json(indent=2)}{context_info}

Provide your credit assessment as valid JSON matching the required output format from your instructions."""

                # Process with Microsoft Agent Framework
                logger.info(
                    "Processing credit analysis",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "agent": "credit",
                        "has_previous_context": bool(previous_assessments),
                    },
                )

                response: AgentRunResponse = await agent.run(message, thread=thread)

                # Log tool usage at debug level
                tool_calls = Observability.extract_tool_calls_from_response(response.messages)
                if tool_calls:
                    logger.debug(
                        "Tools called",
                        extra={
                            "tools": tool_calls,
                            "application_id": Observability.mask_application_id(application.application_id),
                        },
                    )

                # Agent Framework automatically parses response into CreditAssessment
                assessment = response.value

                if assessment is None:
                    # Fallback if parsing failed
                    last_message = response.messages[-1] if response.messages else None
                    content = last_message.text if last_message else "No response"
                    logger.warning(
                        "Structured response parsing failed",
                        extra={
                            "application_id": Observability.mask_application_id(application.application_id),
                            "response_preview": content[:200],
                        },
                    )

                    # Create fallback assessment
                    assessment = CreditAssessment(
                        credit_score_range="UNKNOWN",
                        risk_level="HIGH",
                        recommended_rate=8.0,
                        debt_to_income_ratio=None,
                        identity_verified=False,
                        processing_notes=f"Credit analysis encountered parsing issue: {content[:200]}...",
                        next_agent="income",
                    )

                # Build Pydantic response model
                usage = UsageStats(
                    input_tokens=response.usage_details.input_token_count if response.usage_details else None,
                    output_tokens=response.usage_details.output_token_count if response.usage_details else None,
                    total_tokens=response.usage_details.total_token_count if response.usage_details else None,
                )

                result = AgentResponse(
                    assessment=assessment,
                    usage_stats=usage,
                    response_id=response.response_id,
                    created_at=response.created_at,
                    agent_name="credit",
                    application_id=application.application_id,
                )

                logger.info(
                    "Credit analysis completed",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "agent": "credit",
                        "credit_score_range": assessment.credit_score_range,
                        "risk_level": assessment.risk_level,
                        "tokens_used": usage.total_tokens,
                    },
                )

                return result

        except Exception as e:
            logger.error(
                "Credit analysis failed",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "agent": "credit",
                },
                exc_info=True,
            )

            # Create error assessment with structured response
            error_assessment = CreditAssessment(
                credit_score_range="UNKNOWN",
                risk_level="CRITICAL",
                recommended_rate=10.0,
                debt_to_income_ratio=None,
                identity_verified=False,
                processing_notes=f"Processing error: {str(e)}",
                next_agent="income",
            )

            # Return error response as Pydantic model
            return AgentResponse(
                assessment=error_assessment,
                usage_stats=UsageStats(input_tokens=None, output_tokens=None, total_tokens=None),
                response_id=None,
                created_at=None,
                agent_name="credit",
                application_id=application.application_id,
            )


__all__ = ["CreditAgent"]
