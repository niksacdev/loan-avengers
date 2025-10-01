"""
Income Agent - Employment and Income Verification using Microsoft Agent Framework.

Performs comprehensive income verification, employment validation, and income stability analysis.
Personality and display name are defined in the persona file for UI flexibility.
"""

from __future__ import annotations

import os

from agent_framework import AgentRunResponse, AgentThread, ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import AgentResponse, IncomeAssessment, UsageStats
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("income_agent")


class IncomeAgent:
    """
    Income Agent - Employment and Income Verification Specialist for the Loan Processing System.

    Responsibilities:
    - Employment verification and job stability assessment
    - Income documentation validation (paystubs, tax returns)
    - Income adequacy analysis for requested loan amount
    - Income stability evaluation and trend analysis
    - MCP tool integration for verification, documents, and calculations

    Architecture:
    - Uses Azure AI Foundry with DefaultAzureCredential (Entra ID)
    - Three MCP tools: application_verification (8010), document_processing (8011),
      and financial_calculations (8012) for comprehensive income analysis
    - Structured logging with masked sensitive data (application_id[:8]***)
    - Async context managers for proper MCP tool lifecycle

    Note: Personality and display name are defined in persona files for flexibility.
    """

    def __init__(
        self,
        chat_client: AzureAIAgentClient | None = None,
        temperature: float = 0.1,
        max_tokens: int = 500,
    ):
        """
        Initialize the Income Agent.

        Creates MCP tool connections for employment verification, document processing,
        and financial calculations. ChatAgent is created per-request to ensure proper
        MCP tool lifecycle.

        Args:
            chat_client: Azure AI Agent client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for the model (low for precision)
            max_tokens: Maximum tokens for response

        Environment:
            Requires AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME.
            MCP_APPLICATION_VERIFICATION_URL for employment verification.
            MCP_DOCUMENT_PROCESSING_URL for document extraction and validation.
            MCP_FINANCIAL_CALCULATIONS_URL for income stability analysis.
            Authentication via Azure CLI (az login) or Managed Identity.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = AzureAIAgentClient(async_credential=DefaultAzureCredential())

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("income")

        # Create MCP tools for income verification
        # Tool 1: Application verification for employment and bank data
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        self.verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Employment verification and bank account data services",
            load_tools=True,
            load_prompts=False,
        )

        # Tool 2: Document processing for paystubs and tax returns
        documents_url = os.getenv("MCP_DOCUMENT_PROCESSING_URL")
        self.documents_tool = MCPStreamableHTTPTool(
            name="document-processing",
            url=documents_url,
            description="Document extraction and validation for income verification",
            load_tools=True,
            load_prompts=False,
        )

        # Tool 3: Financial calculations for income stability analysis
        calculations_url = os.getenv("MCP_FINANCIAL_CALCULATIONS_URL")
        self.calculations_tool = MCPStreamableHTTPTool(
            name="financial-calculations",
            url=calculations_url,
            description="Income stability and affordability calculations",
            load_tools=True,
            load_prompts=False,
        )

        # Store agent configuration for later initialization
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info("IncomeAgent initialized", extra={"agent": "income", "mcp_servers": ["8010", "8011", "8012"]})

    async def process_application(
        self,
        application: LoanApplication,
        thread: AgentThread | None = None,
        previous_assessments: list[AgentResponse] | None = None,
    ) -> AgentResponse[IncomeAssessment]:
        """
        Process loan application for income verification.

        Uses async context managers to connect MCP tools and create ChatAgent per request.
        This ensures proper tool discovery and lifecycle management.

        Args:
            application: The loan application to process
            thread: Optional conversation thread for context (conversation history)
            previous_assessments: Optional list of assessments from previous agents
                (e.g., Intake, Credit)

        Returns:
            AgentResponse: Pydantic model containing:
            - assessment: IncomeAssessment with verification results
            - usage_stats: UsageStats with token metrics
            - response_id: Unique identifier
            - created_at: Timestamp
            - agent_name: "income"
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
                    name="Income_Verifier",
                    description="Income and employment verification specialist",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format=IncomeAssessment,
                    tools=[self.verification_tool, self.documents_tool, self.calculations_tool],
                )

                # Build message with application data and optional previous context
                context_info = ""
                if previous_assessments:
                    context_info = "\n\nPrevious Agent Assessments:\n"
                    for prev in previous_assessments:
                        context_info += f"\n{prev.agent_name}: {prev.assessment.processing_notes[:200]}..."

                message = f"""Verify the income and employment for this loan application:

{application.model_dump_json(indent=2)}{context_info}

Provide your income verification assessment as valid JSON matching the required output format from your instructions."""

                # Process with Microsoft Agent Framework
                logger.info(
                    "Processing income verification",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "agent": "income",
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

                # Agent Framework automatically parses response into IncomeAssessment
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
                    assessment = IncomeAssessment(
                        employment_verified=False,
                        income_stability="UNKNOWN",
                        income_adequacy="INSUFFICIENT",
                        verified_monthly_income=None,
                        employment_duration_months=None,
                        processing_notes=f"Income verification encountered parsing issue: {content[:200]}...",
                        next_agent="risk",
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
                    agent_name="income",
                    application_id=application.application_id,
                )

                logger.info(
                    "Income verification completed",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "agent": "income",
                        "employment_verified": assessment.employment_verified,
                        "income_stability": assessment.income_stability,
                        "tokens_used": usage.total_tokens,
                    },
                )

                return result

        except Exception as e:
            logger.error(
                "Income verification failed",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "agent": "income",
                },
                exc_info=True,
            )

            # Create error assessment with structured response
            error_assessment = IncomeAssessment(
                employment_verified=False,
                income_stability="UNKNOWN",
                income_adequacy="INSUFFICIENT",
                verified_monthly_income=None,
                employment_duration_months=None,
                processing_notes=f"Processing error: {str(e)}",
                next_agent="risk",
            )

            # Return error response as Pydantic model
            return AgentResponse(
                assessment=error_assessment,
                usage_stats=UsageStats(input_tokens=None, output_tokens=None, total_tokens=None),
                response_id=None,
                created_at=None,
                agent_name="income",
                application_id=application.application_id,
            )


__all__ = ["IncomeAgent"]
