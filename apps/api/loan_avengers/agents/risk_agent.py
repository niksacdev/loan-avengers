"""
Risk Agent - Comprehensive Risk Assessment using Microsoft Agent Framework.

Performs final risk evaluation, synthesizes all agent assessments, and provides loan recommendations.
Personality and display name are defined in the persona file for UI flexibility.
"""

from __future__ import annotations

import os

from agent_framework import AgentRunResponse, AgentThread, ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import AgentResponse, RiskAssessment, UsageStats
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("risk_agent")


class RiskAgent:
    """
    Risk Agent - Comprehensive Risk Evaluator for the Loan Processing System.

    Responsibilities:
    - Synthesize assessments from all previous agents (Intake, Credit, Income)
    - Comprehensive risk evaluation across credit, capacity, and collateral
    - Fraud detection and identity verification validation
    - Final loan recommendation with risk mitigation strategies
    - MCP tool integration for comprehensive analysis across all services

    Architecture:
    - Uses Azure AI Foundry with DefaultAzureCredential (Entra ID)
    - Three MCP tools: ALL servers (8010, 8011, 8012) for holistic risk analysis
    - Structured logging with masked sensitive data (application_id[:8]***)
    - Async context managers for proper MCP tool lifecycle

    Note: Personality and display name are defined in persona files for flexibility.
    """

    def __init__(
        self,
        chat_client: AzureAIAgentClient | None = None,
        temperature: float = 0.1,
        max_tokens: int = 600,
    ):
        """
        Initialize the Risk Agent.

        Creates MCP tool connections for all three services to enable comprehensive
        risk assessment. ChatAgent is created per-request to ensure proper MCP tool lifecycle.

        Args:
            chat_client: Azure AI Agent client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for the model (low for consistency)
            max_tokens: Maximum tokens for response

        Environment:
            Requires AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME.
            MCP_APPLICATION_VERIFICATION_URL for final verification checks.
            MCP_DOCUMENT_PROCESSING_URL for document validation.
            MCP_FINANCIAL_CALCULATIONS_URL for final risk metrics.
            Authentication via Azure CLI (az login) or Managed Identity.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = AzureAIAgentClient(async_credential=DefaultAzureCredential())

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("risk")

        # Create MCP tools for comprehensive risk assessment
        # Tool 1: Application verification for final fraud and identity checks
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        self.verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Final verification and fraud detection services",
            load_tools=True,
            load_prompts=False,
        )

        # Tool 2: Document processing for comprehensive document validation
        documents_url = os.getenv("MCP_DOCUMENT_PROCESSING_URL")
        self.documents_tool = MCPStreamableHTTPTool(
            name="document-processing",
            url=documents_url,
            description="Comprehensive document validation and metadata analysis",
            load_tools=True,
            load_prompts=False,
        )

        # Tool 3: Financial calculations for final risk metrics
        calculations_url = os.getenv("MCP_FINANCIAL_CALCULATIONS_URL")
        self.calculations_tool = MCPStreamableHTTPTool(
            name="financial-calculations",
            url=calculations_url,
            description="Final financial risk calculations and metrics",
            load_tools=True,
            load_prompts=False,
        )

        # Store agent configuration for later initialization
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info("RiskAgent initialized", extra={"agent": "risk", "mcp_servers": ["8010", "8011", "8012"]})

    async def process_application(
        self,
        application: LoanApplication,
        thread: AgentThread | None = None,
        previous_assessments: list[AgentResponse] | None = None,
    ) -> AgentResponse[RiskAssessment]:
        """
        Process loan application for comprehensive risk assessment.

        Uses async context managers to connect MCP tools and create ChatAgent per request.
        This ensures proper tool discovery and lifecycle management.

        Args:
            application: The loan application to process
            thread: Optional conversation thread for context (conversation history)
            previous_assessments: Required list of assessments from previous agents
                (Intake, Credit, Income). The risk agent synthesizes these into final decision.

        Returns:
            AgentResponse: Pydantic model containing:
            - assessment: RiskAssessment with final risk evaluation
            - usage_stats: UsageStats with token metrics
            - response_id: Unique identifier
            - created_at: Timestamp
            - agent_name: "risk"
            - application_id: Application ID

        Note:
            Logs mask sensitive data - application_id logged as "[:8]***"
        """
        try:
            # Connect to all three MCP tools within async contexts
            async with self.verification_tool, self.documents_tool, self.calculations_tool:
                # Log MCP tool connection details
                logger.debug(
                    "MCP tools connected",
                    extra={
                        "tool_count": len(self.verification_tool.functions)
                        + len(self.documents_tool.functions)
                        + len(self.calculations_tool.functions),
                        "application_id": Observability.mask_application_id(application.application_id),
                    },
                )

                # Create ChatAgent with connected MCP tools
                agent = ChatAgent(
                    chat_client=self.chat_client,
                    instructions=self.instructions,
                    name="Risk_Analyzer",
                    description="Final loan decision maker with comprehensive risk analysis",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format=RiskAssessment,
                    tools=[self.verification_tool, self.documents_tool, self.calculations_tool],
                )

                # Build message with application data and ALL previous assessments
                context_info = ""
                if previous_assessments:
                    context_info = "\n\nPrevious Agent Assessments (for synthesis):\n"
                    for prev in previous_assessments:
                        context_info += f"\n{prev.agent_name.upper()}: {prev.assessment.processing_notes[:200]}..."

                message = f"""Perform comprehensive risk assessment for this loan application:

{application.model_dump_json(indent=2)}{context_info}

Synthesize all previous assessments and provide final risk evaluation as valid JSON matching
the required output format from your instructions."""

                # Process with Microsoft Agent Framework
                logger.info(
                    "Processing risk assessment",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "agent": "risk",
                        "previous_agents_count": len(previous_assessments) if previous_assessments else 0,
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

                # Agent Framework automatically parses response into RiskAssessment
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
                    assessment = RiskAssessment(
                        overall_risk="CRITICAL",
                        fraud_indicators=[],
                        risk_factors=["Unable to complete risk assessment due to parsing error"],
                        mitigation_recommendations=["Manual review required"],
                        loan_recommendation="MANUAL_REVIEW",
                        processing_notes=f"Risk assessment encountered parsing issue: {content[:200]}...",
                        next_agent="orchestrator",
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
                    agent_name="risk",
                    application_id=application.application_id,
                )

                logger.info(
                    "Risk assessment completed",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "agent": "risk",
                        "overall_risk": assessment.overall_risk,
                        "loan_recommendation": assessment.loan_recommendation,
                        "tokens_used": usage.total_tokens,
                    },
                )

                return result

        except Exception as e:
            logger.error(
                "Risk assessment failed",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "agent": "risk",
                },
                exc_info=True,
            )

            # Create error assessment with structured response
            error_assessment = RiskAssessment(
                overall_risk="CRITICAL",
                fraud_indicators=[],
                risk_factors=[f"Processing error: {str(e)}"],
                mitigation_recommendations=["Manual review required due to system error"],
                loan_recommendation="MANUAL_REVIEW",
                processing_notes=f"Processing error: {str(e)}",
                next_agent="orchestrator",
            )

            # Return error response as Pydantic model
            return AgentResponse(
                assessment=error_assessment,
                usage_stats=UsageStats(input_tokens=None, output_tokens=None, total_tokens=None),
                response_id=None,
                created_at=None,
                agent_name="risk",
                application_id=application.application_id,
            )


__all__ = ["RiskAgent"]
