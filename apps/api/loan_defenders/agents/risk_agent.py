"""
Risk Agent - Comprehensive Risk Assessment using Microsoft Agent Framework.

Performs final risk evaluation, synthesizes all agent assessments, and provides loan recommendations.
Personality and display name are defined in the persona file for UI flexibility.
"""

from __future__ import annotations

import os

from agent_framework import ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_defenders.models.responses import RiskAssessment
from loan_defenders.utils.observability import Observability
from loan_defenders.utils.persona_loader import PersonaLoader

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
    - Three MCP tools: ALL servers (application_verification, document_processing,
      financial_calculations) for holistic risk analysis
    - Used with SequentialBuilder for workflow orchestration
    - Structured logging with masked sensitive data

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

        Args:
            chat_client: Azure AI Agent client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for the model (low for consistency)
            max_tokens: Maximum tokens for response

        Environment:
            MCP_APPLICATION_VERIFICATION_URL: MCP verification server URL
            MCP_DOCUMENT_PROCESSING_URL: MCP document processing server URL
            MCP_FINANCIAL_CALCULATIONS_URL: MCP calculations server URL
            AZURE_AI_PROJECT_ENDPOINT: Azure AI project endpoint
            AZURE_AI_MODEL_DEPLOYMENT_NAME: Model deployment name
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = AzureAIAgentClient(async_credential=DefaultAzureCredential())

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("risk")

        # Create MCP tools for comprehensive risk assessment
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        if not verification_url:
            msg = "MCP_APPLICATION_VERIFICATION_URL environment variable not set"
            raise ValueError(msg)

        self.verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Final verification and fraud detection services",
            load_tools=True,
            load_prompts=False,
        )

        documents_url = os.getenv("MCP_DOCUMENT_PROCESSING_URL")
        if not documents_url:
            msg = "MCP_DOCUMENT_PROCESSING_URL environment variable not set"
            raise ValueError(msg)

        self.documents_tool = MCPStreamableHTTPTool(
            name="document-processing",
            url=documents_url,
            description="Comprehensive document validation and metadata analysis",
            load_tools=True,
            load_prompts=False,
        )

        calculations_url = os.getenv("MCP_FINANCIAL_CALCULATIONS_URL")
        if not calculations_url:
            msg = "MCP_FINANCIAL_CALCULATIONS_URL environment variable not set"
            raise ValueError(msg)

        self.calculations_tool = MCPStreamableHTTPTool(
            name="financial-calculations",
            url=calculations_url,
            description="Final financial risk calculations and metrics",
            load_tools=True,
            load_prompts=False,
        )

        # Store agent configuration
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(
            "RiskAgent initialized",
            extra={
                "agent": "risk",
                "mcp_servers": ["application_verification", "document_processing", "financial_calculations"],
            },
        )

    def create_agent(self) -> ChatAgent:
        """
        Create a ChatAgent for SequentialBuilder workflow orchestration.

        Returns:
            ChatAgent: Configured agent with MCP tools and persona

        Note:
            Framework manages MCP tool lifecycle automatically.
        """
        return self.chat_client.create_agent(
            name="Risk_Analyzer",
            instructions=self.instructions,
            description="Final loan decision maker with comprehensive risk analysis",
            model_config={
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            response_format=RiskAssessment,
            tools=[self.verification_tool, self.documents_tool, self.calculations_tool],
        )


__all__ = ["RiskAgent"]
