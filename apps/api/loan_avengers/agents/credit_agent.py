"""
Credit Agent - Creditworthiness Analysis using Microsoft Agent Framework.

Performs comprehensive credit analysis, risk scoring, and debt-to-income calculations.
Personality and display name are defined in the persona file for UI flexibility.
"""

from __future__ import annotations

import os

from agent_framework import ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.models.responses import CreditAssessment
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
    - Used with SequentialBuilder for workflow orchestration
    - Structured logging with masked sensitive data

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

        Args:
            chat_client: Azure AI Agent client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for the model (low for consistency)
            max_tokens: Maximum tokens for response

        Environment:
            MCP_APPLICATION_VERIFICATION_URL: MCP verification server URL
            MCP_FINANCIAL_CALCULATIONS_URL: MCP calculations server URL
            AZURE_AI_PROJECT_ENDPOINT: Azure AI project endpoint
            AZURE_AI_MODEL_DEPLOYMENT_NAME: Model deployment name
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = AzureAIAgentClient(async_credential=DefaultAzureCredential())

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("credit")

        # Create MCP tools for credit assessment
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        if not verification_url:
            msg = "MCP_APPLICATION_VERIFICATION_URL environment variable not set"
            raise ValueError(msg)

        self.verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Credit report and identity verification services",
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
            description="Financial calculations for credit analysis",
            load_tools=True,
            load_prompts=False,
        )

        # Store agent configuration
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(
            "CreditAgent initialized",
            extra={"agent": "credit", "mcp_servers": ["application_verification", "financial_calculations"]},
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
            name="Credit_Assessor",
            instructions=self.instructions,
            description="Expert credit analyst with celebratory personality",
            model_config={
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            response_format=CreditAssessment,
            tools=[self.verification_tool, self.calculations_tool],
        )


__all__ = ["CreditAgent"]
