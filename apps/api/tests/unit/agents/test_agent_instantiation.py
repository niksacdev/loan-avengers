"""
Test agent instantiation and SequentialBuilder integration.

Verifies that all agents can be instantiated correctly and that they
provide ChatAgent instances compatible with SequentialBuilder.
"""

from unittest.mock import Mock, patch

import pytest
from agent_framework import ChatAgent
from agent_framework._mcp import MCPStreamableHTTPTool

from loan_avengers.agents.credit_agent import CreditAgent
from loan_avengers.agents.income_agent import IncomeAgent
from loan_avengers.agents.intake_agent import IntakeAgent
from loan_avengers.agents.risk_agent import RiskAgent
from loan_avengers.models.responses import (
    CreditAssessment,
    IncomeAssessment,
    IntakeAssessment,
    RiskAssessment,
)


@pytest.fixture
def mock_chat_client():
    """Mock AzureAIAgentClient for testing."""
    client = Mock()
    client.create_agent = Mock(return_value=Mock(spec=ChatAgent))
    return client


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for MCP servers."""
    monkeypatch.setenv("MCP_APPLICATION_VERIFICATION_URL", "http://localhost:8010")
    monkeypatch.setenv("MCP_DOCUMENT_PROCESSING_URL", "http://localhost:8011")
    monkeypatch.setenv("MCP_FINANCIAL_CALCULATIONS_URL", "http://localhost:8012")


class TestIntakeAgent:
    """Test IntakeAgent instantiation and configuration."""

    def test_init_with_client(self, mock_chat_client, mock_env_vars):
        """Test IntakeAgent initialization with provided client."""
        agent = IntakeAgent(chat_client=mock_chat_client)

        assert agent.chat_client == mock_chat_client
        assert agent.temperature == 0.1
        assert agent.max_tokens == 500
        assert isinstance(agent.mcp_tool, MCPStreamableHTTPTool)
        assert agent.mcp_tool.name == "application-verification"

    def test_init_without_client(self, mock_env_vars):
        """Test IntakeAgent initialization without provided client."""
        with patch("loan_avengers.agents.intake_agent.AzureAIAgentClient") as mock_client_class:
            with patch("loan_avengers.agents.intake_agent.DefaultAzureCredential"):
                agent = IntakeAgent()

                assert agent.chat_client is not None
                mock_client_class.assert_called_once()

    def test_create_agent(self, mock_chat_client, mock_env_vars):
        """Test IntakeAgent creates ChatAgent correctly."""
        agent = IntakeAgent(chat_client=mock_chat_client)
        agent.create_agent()

        # Verify create_agent was called with correct parameters
        mock_chat_client.create_agent.assert_called_once()
        call_kwargs = mock_chat_client.create_agent.call_args.kwargs

        assert call_kwargs["name"] == "Intake_Agent"
        assert "instructions" in call_kwargs
        assert call_kwargs["response_format"] == IntakeAssessment
        assert call_kwargs["tools"] == agent.mcp_tool
        assert call_kwargs["model_config"]["temperature"] == 0.1
        assert call_kwargs["model_config"]["max_tokens"] == 500

    def test_custom_temperature_and_tokens(self, mock_chat_client, mock_env_vars):
        """Test IntakeAgent with custom temperature and max_tokens."""
        agent = IntakeAgent(chat_client=mock_chat_client, temperature=0.5, max_tokens=1000)

        assert agent.temperature == 0.5
        assert agent.max_tokens == 1000


class TestCreditAgent:
    """Test CreditAgent instantiation and configuration."""

    def test_init_with_client(self, mock_chat_client, mock_env_vars):
        """Test CreditAgent initialization with provided client."""
        agent = CreditAgent(chat_client=mock_chat_client)

        assert agent.chat_client == mock_chat_client
        assert agent.temperature == 0.2
        assert agent.max_tokens == 600
        assert isinstance(agent.verification_tool, MCPStreamableHTTPTool)
        assert isinstance(agent.calculations_tool, MCPStreamableHTTPTool)
        assert agent.verification_tool.name == "application-verification"
        assert agent.calculations_tool.name == "financial-calculations"

    def test_create_agent(self, mock_chat_client, mock_env_vars):
        """Test CreditAgent creates ChatAgent correctly."""
        agent = CreditAgent(chat_client=mock_chat_client)
        agent.create_agent()

        # Verify create_agent was called with correct parameters
        mock_chat_client.create_agent.assert_called_once()
        call_kwargs = mock_chat_client.create_agent.call_args.kwargs

        assert call_kwargs["name"] == "Credit_Assessor"
        assert "instructions" in call_kwargs
        assert call_kwargs["response_format"] == CreditAssessment
        assert len(call_kwargs["tools"]) == 2
        assert agent.verification_tool in call_kwargs["tools"]
        assert agent.calculations_tool in call_kwargs["tools"]
        assert call_kwargs["model_config"]["temperature"] == 0.2
        assert call_kwargs["model_config"]["max_tokens"] == 600


class TestIncomeAgent:
    """Test IncomeAgent instantiation and configuration."""

    def test_init_with_client(self, mock_chat_client, mock_env_vars):
        """Test IncomeAgent initialization with provided client."""
        agent = IncomeAgent(chat_client=mock_chat_client)

        assert agent.chat_client == mock_chat_client
        assert agent.temperature == 0.1
        assert agent.max_tokens == 500
        assert isinstance(agent.verification_tool, MCPStreamableHTTPTool)
        assert isinstance(agent.documents_tool, MCPStreamableHTTPTool)
        assert isinstance(agent.calculations_tool, MCPStreamableHTTPTool)
        assert agent.verification_tool.name == "application-verification"
        assert agent.documents_tool.name == "document-processing"
        assert agent.calculations_tool.name == "financial-calculations"

    def test_create_agent(self, mock_chat_client, mock_env_vars):
        """Test IncomeAgent creates ChatAgent correctly."""
        agent = IncomeAgent(chat_client=mock_chat_client)
        agent.create_agent()

        # Verify create_agent was called with correct parameters
        mock_chat_client.create_agent.assert_called_once()
        call_kwargs = mock_chat_client.create_agent.call_args.kwargs

        assert call_kwargs["name"] == "Income_Verifier"
        assert "instructions" in call_kwargs
        assert call_kwargs["response_format"] == IncomeAssessment
        assert len(call_kwargs["tools"]) == 3
        assert agent.verification_tool in call_kwargs["tools"]
        assert agent.documents_tool in call_kwargs["tools"]
        assert agent.calculations_tool in call_kwargs["tools"]
        assert call_kwargs["model_config"]["temperature"] == 0.1
        assert call_kwargs["model_config"]["max_tokens"] == 500


class TestRiskAgent:
    """Test RiskAgent instantiation and configuration."""

    def test_init_with_client(self, mock_chat_client, mock_env_vars):
        """Test RiskAgent initialization with provided client."""
        agent = RiskAgent(chat_client=mock_chat_client)

        assert agent.chat_client == mock_chat_client
        assert agent.temperature == 0.1
        assert agent.max_tokens == 600
        assert isinstance(agent.verification_tool, MCPStreamableHTTPTool)
        assert isinstance(agent.documents_tool, MCPStreamableHTTPTool)
        assert isinstance(agent.calculations_tool, MCPStreamableHTTPTool)
        assert agent.verification_tool.name == "application-verification"
        assert agent.documents_tool.name == "document-processing"
        assert agent.calculations_tool.name == "financial-calculations"

    def test_create_agent(self, mock_chat_client, mock_env_vars):
        """Test RiskAgent creates ChatAgent correctly."""
        agent = RiskAgent(chat_client=mock_chat_client)
        agent.create_agent()

        # Verify create_agent was called with correct parameters
        mock_chat_client.create_agent.assert_called_once()
        call_kwargs = mock_chat_client.create_agent.call_args.kwargs

        assert call_kwargs["name"] == "Risk_Analyzer"
        assert "instructions" in call_kwargs
        assert call_kwargs["response_format"] == RiskAssessment
        assert len(call_kwargs["tools"]) == 3
        assert agent.verification_tool in call_kwargs["tools"]
        assert agent.documents_tool in call_kwargs["tools"]
        assert agent.calculations_tool in call_kwargs["tools"]
        assert call_kwargs["model_config"]["temperature"] == 0.1
        assert call_kwargs["model_config"]["max_tokens"] == 600


class TestSequentialBuilderIntegration:
    """Test that all agents work together with SequentialBuilder."""

    def test_all_agents_return_chat_agent(self, mock_chat_client, mock_env_vars):
        """Test that all agents return ChatAgent instances."""
        intake = IntakeAgent(chat_client=mock_chat_client)
        credit = CreditAgent(chat_client=mock_chat_client)
        income = IncomeAgent(chat_client=mock_chat_client)
        risk = RiskAgent(chat_client=mock_chat_client)

        # All should return ChatAgent instances
        assert intake.create_agent() is not None
        assert credit.create_agent() is not None
        assert income.create_agent() is not None
        assert risk.create_agent() is not None

    def test_agents_can_be_added_to_sequential_builder(self, mock_chat_client, mock_env_vars):
        """Test that agents can be used with SequentialBuilder."""
        with patch("agent_framework.SequentialBuilder") as mock_builder_class:
            mock_workflow = Mock()
            mock_builder = Mock()
            mock_builder.participants.return_value.build.return_value = mock_workflow
            mock_builder_class.return_value = mock_builder

            intake = IntakeAgent(chat_client=mock_chat_client)
            credit = CreditAgent(chat_client=mock_chat_client)
            income = IncomeAgent(chat_client=mock_chat_client)
            risk = RiskAgent(chat_client=mock_chat_client)

            # Create chat agents
            intake_chat = intake.create_agent()
            credit_chat = credit.create_agent()
            income_chat = income.create_agent()
            risk_chat = risk.create_agent()

            # Simulate SequentialBuilder pattern
            from agent_framework import SequentialBuilder

            workflow = SequentialBuilder().participants([intake_chat, credit_chat, income_chat, risk_chat]).build()

            # Verify workflow was created
            assert workflow is not None
            mock_builder.participants.assert_called_once()
            mock_builder.participants.return_value.build.assert_called_once()

    def test_mcp_tools_configured_per_agent(self, mock_chat_client, mock_env_vars):
        """Test that each agent has correct MCP tools configured."""
        intake = IntakeAgent(chat_client=mock_chat_client)
        credit = CreditAgent(chat_client=mock_chat_client)
        income = IncomeAgent(chat_client=mock_chat_client)
        risk = RiskAgent(chat_client=mock_chat_client)

        # Intake: 1 tool (verification)
        intake.create_agent()
        intake_call = mock_chat_client.create_agent.call_args_list[0]
        assert isinstance(intake_call.kwargs["tools"], MCPStreamableHTTPTool)

        # Credit: 2 tools (verification, calculations)
        credit.create_agent()
        credit_call = mock_chat_client.create_agent.call_args_list[1]
        assert len(credit_call.kwargs["tools"]) == 2

        # Income: 3 tools (verification, documents, calculations)
        income.create_agent()
        income_call = mock_chat_client.create_agent.call_args_list[2]
        assert len(income_call.kwargs["tools"]) == 3

        # Risk: 3 tools (verification, documents, calculations)
        risk.create_agent()
        risk_call = mock_chat_client.create_agent.call_args_list[3]
        assert len(risk_call.kwargs["tools"]) == 3
