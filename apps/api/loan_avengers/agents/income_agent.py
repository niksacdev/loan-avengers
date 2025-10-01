"""
Income Agent - Employment and Income Verification using Microsoft Agent Framework.

Performs comprehensive income verification, employment validation, and income stability analysis.
Personality and display name are defined in the persona file for UI flexibility.
"""

from __future__ import annotations

import os

from agent_framework import ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.models.responses import IncomeAssessment
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
    - Three MCP tools: application_verification, document_processing,
      and financial_calculations for comprehensive income analysis
    - Used with SequentialBuilder for workflow orchestration
    - Structured logging with masked sensitive data

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

        Args:
            chat_client: Azure AI Agent client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for the model (low for precision)
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
        self.instructions = PersonaLoader.load_persona("income")

        # Create MCP tools for income verification
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        if not verification_url:
            msg = "MCP_APPLICATION_VERIFICATION_URL environment variable not set"
            raise ValueError(msg)

        self.verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Employment verification and bank account data services",
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
            description="Document extraction and validation for income verification",
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
            description="Income stability and affordability calculations",
            load_tools=True,
            load_prompts=False,
        )

        # Store agent configuration
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(
            "IncomeAgent initialized",
            extra={
                "agent": "income",
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
            name="Income_Verifier",
            instructions=self.instructions,
            description="Income and employment verification specialist",
            model_config={
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            response_format=IncomeAssessment,
            tools=[self.verification_tool, self.documents_tool, self.calculations_tool],
        )


__all__ = ["IncomeAgent"]
