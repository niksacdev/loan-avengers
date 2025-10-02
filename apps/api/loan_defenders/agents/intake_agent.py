"""
Intake Agent - Application Validator using Microsoft Agent Framework.

Performs lightning-fast application validation and routing with precision.
Personality and display name are defined in the persona file for UI flexibility.
"""

from __future__ import annotations

import os

from agent_framework import ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_defenders.models.responses import IntakeAssessment
from loan_defenders.utils.observability import Observability
from loan_defenders.utils.persona_loader import PersonaLoader

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
    - MCP tools passed at agent creation (framework manages lifecycle)
    - Used with SequentialBuilder for workflow orchestration
    - Structured logging with masked sensitive data

    Note: Personality and display names are defined in persona files for flexibility.
    """

    def __init__(
        self,
        chat_client: AzureAIAgentClient | None = None,
        temperature: float = 0.1,
        max_tokens: int = 500,
    ):
        """
        Initialize the Intake Agent.

        Args:
            chat_client: Azure AI Agent client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
            temperature: Sampling temperature for the model (low for consistency)
            max_tokens: Maximum tokens for response (small for speed)

        Environment:
            MCP_APPLICATION_VERIFICATION_URL: MCP server URL
            AZURE_AI_PROJECT_ENDPOINT: Azure AI project endpoint
            AZURE_AI_MODEL_DEPLOYMENT_NAME: Model deployment name
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = AzureAIAgentClient(async_credential=DefaultAzureCredential())

        # Load persona instructions from markdown file
        self.instructions = PersonaLoader.load_persona("intake")

        # Create MCP tool for application verification server
        mcp_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        if not mcp_url:
            msg = "MCP_APPLICATION_VERIFICATION_URL environment variable not set"
            raise ValueError(msg)

        self.mcp_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=mcp_url,
            description="Application verification service for basic parameter validation",
            load_tools=True,
            load_prompts=False,
        )

        # Store agent configuration
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info("IntakeAgent initialized", extra={"agent": "intake"})

    def create_agent(self) -> ChatAgent:
        """
        Create a ChatAgent for SequentialBuilder workflow orchestration.

        Returns:
            ChatAgent: Configured agent with MCP tools and persona

        Note:
            Framework manages MCP tool lifecycle automatically.
        """
        return self.chat_client.create_agent(
            name="Intake_Agent",
            instructions=self.instructions,
            description="Sharp-eyed application validator with efficient humor",
            model_config={
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            response_format=IntakeAssessment,
            tools=self.mcp_tool,
        )


__all__ = ["IntakeAgent"]
