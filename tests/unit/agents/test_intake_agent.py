"""
Unit tests for the IntakeAgent class.

These tests focus on testing the IntakeAgent in isolation with mocked dependencies,
ensuring the agent logic works correctly without external dependencies.
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from agent_framework import AgentRunResponse, ChatMessage, UsageDetails

from loan_avengers.agents.intake_agent import IntakeAgent


class TestIntakeAgentInit:
    """Test IntakeAgent initialization."""

    @patch("loan_avengers.agents.intake_agent.MCPStreamableHTTPTool")
    @patch("loan_avengers.agents.intake_agent.FoundryChatClient")
    @patch("loan_avengers.agents.intake_agent.DefaultAzureCredential")
    @patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona")
    def test_init_with_default_client(
        self, mock_load_persona, mock_default_credential, mock_foundry_client, mock_mcp_tool
    ):
        """Test IntakeAgent initialization with default Foundry client."""
        # Setup mocks
        mock_load_persona.return_value = "Test persona instructions"
        mock_credential_instance = Mock()
        mock_default_credential.return_value = mock_credential_instance
        mock_foundry_instance = Mock()
        mock_foundry_client.return_value = mock_foundry_instance
        mock_mcp_instance = Mock()
        mock_mcp_tool.return_value = mock_mcp_instance

        # Initialize IntakeAgent
        agent = IntakeAgent()

        # Verify initialization
        assert agent.chat_client == mock_foundry_instance
        assert agent.instructions == "Test persona instructions"
        assert agent.mcp_tool == mock_mcp_instance
        assert agent.temperature == 0.1
        assert agent.max_tokens == 500

        # Verify DefaultAzureCredential was created
        mock_default_credential.assert_called_once()

        # Verify FoundryChatClient was called with credential
        mock_foundry_client.assert_called_once_with(async_credential=mock_credential_instance)

        # Verify persona was loaded
        mock_load_persona.assert_called_once_with("intake")

        # Verify MCP tool was created
        mock_mcp_tool.assert_called_once_with(
            name="application-verification",
            url="http://localhost:8010/mcp",
            description="Application verification service for basic parameter validation",
            load_tools=True,
            load_prompts=False,
        )

    @patch("loan_avengers.agents.intake_agent.MCPStreamableHTTPTool")
    @patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona")
    def test_init_with_custom_client(self, mock_load_persona, mock_mcp_tool, mock_azure_chat_client):
        """Test IntakeAgent initialization with custom Azure client."""
        # Setup mocks
        mock_load_persona.return_value = "Test persona instructions"
        mock_mcp_instance = Mock()
        mock_mcp_tool.return_value = mock_mcp_instance

        # Initialize IntakeAgent with custom client
        agent = IntakeAgent(chat_client=mock_azure_chat_client, temperature=0.3, max_tokens=1000)

        # Verify initialization
        assert agent.chat_client == mock_azure_chat_client
        assert agent.instructions == "Test persona instructions"
        assert agent.temperature == 0.3
        assert agent.max_tokens == 1000


class TestIntakeAgentProcessApplication:
    """Test the main process_application method."""

    @pytest.fixture
    def mock_intake_agent(self, mock_azure_chat_client):
        """Create a mock IntakeAgent for testing."""
        with (
            patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona") as mock_load_persona,
            patch("loan_avengers.agents.intake_agent.MCPStreamableHTTPTool") as mock_mcp_tool,
        ):
            mock_load_persona.return_value = "Test persona instructions"
            mock_mcp_instance = Mock()
            mock_mcp_tool.return_value = mock_mcp_instance

            agent = IntakeAgent(chat_client=mock_azure_chat_client)
            return agent

    async def test_process_application_success(
        self, mock_intake_agent, sample_loan_application, sample_intake_assessment
    ):
        """Test successful application processing."""
        # Mock the MCP tool context manager and ChatAgent
        mock_mcp_context = AsyncMock()
        mock_mcp_context.__aenter__ = AsyncMock(return_value=mock_mcp_context)
        mock_mcp_context.__aexit__ = AsyncMock(return_value=None)
        mock_intake_agent.mcp_tool = mock_mcp_context
        mock_mcp_context.functions = [Mock(name="validate_basic_parameters")]

        # Setup mock ChatAgent response
        mock_response = AgentRunResponse(
            messages=[ChatMessage(role="assistant", text="Test response", author_name="John")],
            response_id="test-response-id",
            created_at="2025-01-01T00:00:00Z",
            usage_details=UsageDetails(input_token_count=100, output_token_count=50, total_token_count=150),
            value=sample_intake_assessment,
        )

        with patch("loan_avengers.agents.intake_agent.ChatAgent") as mock_chat_agent_class:
            mock_agent_instance = Mock()
            mock_agent_instance.run = AsyncMock(return_value=mock_response)
            mock_chat_agent_class.return_value = mock_agent_instance

            # Process application
            result = await mock_intake_agent.process_application(sample_loan_application)

        # Verify result structure (Pydantic model, not dict!)
        assert result.agent_name == "intake"
        assert result.application_id == sample_loan_application.application_id
        assert result.assessment.validation_status == "COMPLETE"
        assert result.assessment.routing_decision == "STANDARD"
        assert result.assessment.specialist_name == "John"
        assert result.usage_stats.total_tokens == 150

    async def test_process_application_with_thread(
        self, mock_intake_agent, sample_loan_application, sample_agent_thread
    ):
        """Test application processing with conversation thread."""
        # Mock the MCP tool context manager
        mock_mcp_context = AsyncMock()
        mock_mcp_context.__aenter__ = AsyncMock(return_value=mock_mcp_context)
        mock_mcp_context.__aexit__ = AsyncMock(return_value=None)
        mock_intake_agent.mcp_tool = mock_mcp_context
        mock_mcp_context.functions = []

        # Setup mock response
        mock_response = AgentRunResponse(
            messages=[ChatMessage(role="assistant", text="Test response", author_name="John")],
            response_id="test-response-id-2",
            created_at="2025-01-01T00:00:00Z",
            usage_details=UsageDetails(input_token_count=120, output_token_count=60, total_token_count=180),
            value=Mock(),
        )

        with patch("loan_avengers.agents.intake_agent.ChatAgent") as mock_chat_agent_class:
            mock_agent_instance = Mock()
            mock_agent_instance.run = AsyncMock(return_value=mock_response)
            mock_chat_agent_class.return_value = mock_agent_instance

            # Process application with thread
            result = await mock_intake_agent.process_application(sample_loan_application, thread=sample_agent_thread)

            # Verify thread was passed to agent.run
            mock_agent_instance.run.assert_called_once()
            call_args = mock_agent_instance.run.call_args
            assert call_args[1]["thread"] == sample_agent_thread

        assert result.agent_name == "intake"

    async def test_process_application_parsing_failure(self, mock_intake_agent, sample_loan_application):
        """Test handling of structured response parsing failure."""
        # Mock the MCP tool context manager
        mock_mcp_context = AsyncMock()
        mock_mcp_context.__aenter__ = AsyncMock(return_value=mock_mcp_context)
        mock_mcp_context.__aexit__ = AsyncMock(return_value=None)
        mock_intake_agent.mcp_tool = mock_mcp_context
        mock_mcp_context.functions = []

        # Setup mock response with None value (parsing failed)
        mock_response = AgentRunResponse(
            messages=[ChatMessage(role="assistant", text='{"validation_status": "COMPLETE"}', author_name="John")],
            response_id="test-response-id-3",
            created_at="2025-01-01T00:00:00Z",
            usage_details=UsageDetails(input_token_count=100, output_token_count=50, total_token_count=150),
            value=None,  # Parsing failed
        )

        with patch("loan_avengers.agents.intake_agent.ChatAgent") as mock_chat_agent_class:
            mock_agent_instance = Mock()
            mock_agent_instance.run = AsyncMock(return_value=mock_response)
            mock_chat_agent_class.return_value = mock_agent_instance

            # Process application
            result = await mock_intake_agent.process_application(sample_loan_application)

        # Verify fallback assessment was created
        assert result.assessment.validation_status == "FAILED"
        assert result.assessment.routing_decision == "MANUAL"
        assert result.assessment.confidence_score == 0.0
        assert "parsing issue" in result.assessment.processing_notes

    async def test_process_application_exception_handling(self, mock_intake_agent, sample_loan_application):
        """Test exception handling during application processing."""
        # Mock the MCP tool to raise an exception
        mock_mcp_context = AsyncMock()
        mock_mcp_context.__aenter__ = AsyncMock(side_effect=Exception("Connection error"))
        mock_intake_agent.mcp_tool = mock_mcp_context

        # Process application - should handle exception gracefully
        result = await mock_intake_agent.process_application(sample_loan_application)

        # Verify error assessment was created
        assert result.assessment.validation_status == "FAILED"
        assert result.assessment.routing_decision == "MANUAL"
        assert "Connection error" in result.assessment.processing_notes
        assert result.usage_stats.total_tokens is None


class TestIntakeAgentMessageFormatting:
    """Test message formatting and JSON serialization."""

    def test_loan_application_json_serialization(self, sample_loan_application):
        """Test that LoanApplication serializes correctly to JSON."""
        application_json = sample_loan_application.model_dump_json(indent=2)

        # Verify JSON is valid
        parsed = json.loads(application_json)
        assert parsed["application_id"] == sample_loan_application.application_id
        assert parsed["applicant_name"] == sample_loan_application.applicant_name
        assert "loan_amount" in parsed
        assert "annual_income" in parsed

    async def test_message_contains_application_data(self, mock_azure_chat_client, sample_loan_application):
        """Test that agent message contains application data."""
        with (
            patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona") as mock_load_persona,
            patch("loan_avengers.agents.intake_agent.MCPStreamableHTTPTool") as mock_mcp_tool,
            patch("loan_avengers.agents.intake_agent.ChatAgent") as mock_chat_agent_class,
        ):
            mock_load_persona.return_value = "Test persona"
            mock_mcp_instance = AsyncMock()
            mock_mcp_instance.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
            mock_mcp_instance.__aexit__ = AsyncMock(return_value=None)
            mock_mcp_instance.functions = []
            mock_mcp_tool.return_value = mock_mcp_instance

            mock_agent_instance = Mock()
            mock_response = AgentRunResponse(
                messages=[ChatMessage(role="assistant", text="Test", author_name="John")],
                response_id="test-id",
                created_at="2025-01-01T00:00:00Z",
                usage_details=UsageDetails(input_token_count=100, output_token_count=50, total_token_count=150),
                value=None,
            )
            mock_agent_instance.run = AsyncMock(return_value=mock_response)
            mock_chat_agent_class.return_value = mock_agent_instance

            agent = IntakeAgent(chat_client=mock_azure_chat_client)
            await agent.process_application(sample_loan_application)

            # Verify agent.run was called with message containing application data
            mock_agent_instance.run.assert_called_once()
            call_args = mock_agent_instance.run.call_args
            message = call_args[0][0]

            assert sample_loan_application.application_id in message
            assert sample_loan_application.applicant_name in message


class TestIntakeAgentConfiguration:
    """Test agent configuration and MCP tool setup."""

    @patch("loan_avengers.agents.intake_agent.MCPStreamableHTTPTool")
    @patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona")
    def test_mcp_tool_configuration(self, mock_load_persona, mock_mcp_tool, mock_azure_chat_client):
        """Test that MCP tool is configured correctly."""
        mock_load_persona.return_value = "Test persona"
        mock_mcp_instance = Mock()
        mock_mcp_tool.return_value = mock_mcp_instance

        IntakeAgent(chat_client=mock_azure_chat_client)

        # Verify MCP tool configuration
        mock_mcp_tool.assert_called_once()
        call_args = mock_mcp_tool.call_args
        assert call_args[1]["name"] == "application-verification"
        assert call_args[1]["url"] == "http://localhost:8010/mcp"
        assert call_args[1]["load_tools"] is True
        assert call_args[1]["load_prompts"] is False
