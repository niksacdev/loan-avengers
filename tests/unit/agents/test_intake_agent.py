"""
Unit tests for the IntakeAgent class.

These tests focus on testing the IntakeAgent in isolation with mocked dependencies,
ensuring the agent logic works correctly without external dependencies.
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from agent_framework import AgentRunResponse

from loan_avengers.agents.intake_agent import IntakeAgent
from loan_avengers.models.responses import IntakeAssessment


class TestIntakeAgentInit:
    """Test IntakeAgent initialization."""

    @patch("loan_avengers.agents.intake_agent.AzureChatClient")
    @patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona")
    @patch("loan_avengers.agents.intake_agent.ChatAgent")
    def test_init_with_default_client(self, mock_chat_agent, mock_load_persona, mock_azure_client):
        """Test IntakeAgent initialization with default Azure client."""
        # Setup mocks
        mock_load_persona.return_value = "Test persona instructions"
        mock_azure_instance = Mock()
        mock_azure_client.return_value = mock_azure_instance
        mock_agent_instance = Mock()
        mock_chat_agent.return_value = mock_agent_instance

        # Initialize IntakeAgent
        agent = IntakeAgent()

        # Verify initialization
        assert agent.chat_client == mock_azure_instance
        assert agent.instructions == "Test persona instructions"
        assert agent.agent == mock_agent_instance

        # Verify AzureChatClient was called to create default client
        mock_azure_client.assert_called_once()

        # Verify persona was loaded
        mock_load_persona.assert_called_once_with("intake")

        # Verify ChatAgent was initialized with correct parameters
        mock_chat_agent.assert_called_once()
        call_args = mock_chat_agent.call_args
        assert call_args[1]["chat_client"] == mock_azure_instance
        assert call_args[1]["instructions"] == "Test persona instructions"
        assert call_args[1]["name"] == "John - The Eagle Eye"
        assert call_args[1]["description"] == "Sharp-eyed application validator with efficient humor"
        assert call_args[1]["temperature"] == 0.1
        assert call_args[1]["max_tokens"] == 500
        assert call_args[1]["response_format"] == IntakeAssessment

        # Verify MCP tool is configured
        tools = call_args[1]["tools"]
        assert len(tools) == 1
        assert tools[0].name == "application-verification"
        assert tools[0].url == "http://localhost:8010/sse"

    @patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona")
    @patch("loan_avengers.agents.intake_agent.ChatAgent")
    def test_init_with_custom_client(self, mock_chat_agent, mock_load_persona, mock_azure_chat_client):
        """Test IntakeAgent initialization with custom Azure client."""
        # Setup mocks
        mock_load_persona.return_value = "Test persona instructions"
        mock_agent_instance = Mock()
        mock_chat_agent.return_value = mock_agent_instance

        # Initialize IntakeAgent with custom client
        agent = IntakeAgent(chat_client=mock_azure_chat_client, temperature=0.3, max_tokens=1000)

        # Verify initialization
        assert agent.chat_client == mock_azure_chat_client
        assert agent.instructions == "Test persona instructions"

        # Verify ChatAgent was initialized with custom parameters
        call_args = mock_chat_agent.call_args
        assert call_args[1]["chat_client"] == mock_azure_chat_client
        assert call_args[1]["temperature"] == 0.3
        assert call_args[1]["max_tokens"] == 1000


class TestIntakeAgentProcessApplication:
    """Test the main process_application method."""

    @pytest.fixture
    def mock_intake_agent(self, mock_azure_chat_client):
        """Create a mock IntakeAgent for testing."""
        with (
            patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona") as mock_load_persona,
            patch("loan_avengers.agents.intake_agent.ChatAgent") as mock_chat_agent,
        ):
            mock_load_persona.return_value = "Test persona"
            mock_agent_instance = Mock()
            mock_chat_agent.return_value = mock_agent_instance

            agent = IntakeAgent(chat_client=mock_azure_chat_client)
            agent.agent = mock_agent_instance
            return agent

    async def test_process_application_success(
        self, mock_intake_agent, sample_loan_application, sample_intake_assessment
    ):
        """Test successful application processing."""
        # Setup mock response
        mock_response = AgentRunResponse(
            messages=[Mock(text="Test response", author_name="John")],
            response_id="test-response-id",
            created_at="2025-01-01T00:00:00Z",
            usage_details=Mock(input_token_count=100, output_token_count=50, total_token_count=150),
            value=sample_intake_assessment,  # Structured response
        )
        mock_intake_agent.agent.run = AsyncMock(return_value=mock_response)

        # Process application
        result = await mock_intake_agent.process_application(sample_loan_application)

        # Verify result structure
        assert "assessment" in result
        assert "usage_stats" in result
        assert "response_id" in result
        assert "created_at" in result
        assert "agent_name" in result
        assert "application_id" in result

        # Verify assessment data
        assessment = result["assessment"]
        assert assessment["validation_status"] == "COMPLETE"
        assert assessment["routing_decision"] == "STANDARD"
        assert assessment["confidence_score"] == 0.95
        assert assessment["specialist_name"] == "John"

        # Verify usage stats
        usage = result["usage_stats"]
        assert usage["input_tokens"] == 100
        assert usage["output_tokens"] == 50
        assert usage["total_tokens"] == 150

        # Verify metadata
        assert result["response_id"] == "test-response-id"
        assert result["agent_name"] == "intake"
        assert result["application_id"] == sample_loan_application.application_id

        # Verify agent was called with correct message format
        mock_intake_agent.agent.run.assert_called_once()
        call_args = mock_intake_agent.agent.run.call_args[0]
        assert "Process this loan application for intake validation and routing:" in call_args[0]
        assert sample_loan_application.application_id in call_args[0]

    async def test_process_application_with_thread(
        self, mock_intake_agent, sample_loan_application, sample_agent_thread
    ):
        """Test application processing with conversation thread."""
        # Setup mock response
        mock_response = AgentRunResponse(
            messages=[Mock(text="Test response", author_name="John")],
            response_id="test-response-id-2",
            created_at="2025-01-01T00:00:00Z",
            usage_details=Mock(input_token_count=120, output_token_count=60, total_token_count=180),
            value=Mock(),  # Mock assessment
        )
        mock_intake_agent.agent.run = AsyncMock(return_value=mock_response)

        # Process application with thread
        result = await mock_intake_agent.process_application(sample_loan_application, thread=sample_agent_thread)

        # Verify agent was called with thread
        mock_intake_agent.agent.run.assert_called_once()
        call_args = mock_intake_agent.agent.run.call_args
        assert call_args[1]["thread"] == sample_agent_thread

        # Verify result includes thread context
        assert result["response_id"] == "test-response-id-2"

    async def test_process_application_parsing_failure(self, mock_intake_agent, sample_loan_application):
        """Test application processing when response parsing fails."""
        # Setup mock response with parsing failure (value=None)
        mock_response = AgentRunResponse(
            messages=[Mock(text="Invalid response format", author_name="John")],
            response_id="test-response-id-3",
            created_at="2025-01-01T00:00:00Z",
            usage_details=Mock(input_token_count=80, output_token_count=40, total_token_count=120),
            value=None,  # Parsing failed
        )
        mock_intake_agent.agent.run = AsyncMock(return_value=mock_response)

        # Process application
        result = await mock_intake_agent.process_application(sample_loan_application)

        # Verify fallback assessment was created
        assessment = result["assessment"]
        assert assessment["validation_status"] == "FAILED"
        assert assessment["routing_decision"] == "MANUAL"
        assert assessment["confidence_score"] == 0.0
        assert "Eagle eye scan encountered parsing issue" in assessment["processing_notes"]
        assert "🦅 Eagle eyes spotted something!" in assessment["celebration_message"]

    async def test_process_application_exception_handling(self, mock_intake_agent, sample_loan_application):
        """Test application processing when an exception occurs."""
        # Setup mock to raise exception
        mock_intake_agent.agent.run = AsyncMock(side_effect=Exception("Test error"))

        # Process application
        result = await mock_intake_agent.process_application(sample_loan_application)

        # Verify error assessment was created
        assessment = result["assessment"]
        assert assessment["validation_status"] == "FAILED"
        assert assessment["routing_decision"] == "MANUAL"
        assert assessment["confidence_score"] == 0.0
        assert "Eagle eye processing failed: Test error" in assessment["processing_notes"]
        assert "🦅 Eagle eyes spotted a technical issue!" in assessment["celebration_message"]

        # Verify usage stats are None for error case
        usage = result["usage_stats"]
        assert usage["input_tokens"] is None
        assert usage["output_tokens"] is None
        assert usage["total_tokens"] is None


class TestIntakeAgentMessageFormatting:
    """Test message formatting and JSON serialization."""

    def test_loan_application_json_serialization(self, sample_loan_application):
        """Test that loan application properly serializes to JSON."""
        # This tests the Pydantic model integration
        json_data = sample_loan_application.model_dump_json(indent=2)

        # Verify it's valid JSON
        parsed_data = json.loads(json_data)

        # Verify key fields are present
        assert parsed_data["application_id"] == "LN1234567890"
        assert parsed_data["applicant_name"] == "John Doe"
        assert float(parsed_data["annual_income"]) == 85000.00
        assert parsed_data["employment_status"] == "employed"

    @patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona")
    @patch("loan_avengers.agents.intake_agent.ChatAgent")
    async def test_message_contains_application_data(self, mock_chat_agent, mock_load_persona, sample_loan_application):
        """Test that the message sent to the agent contains the application data."""
        # Setup mocks
        mock_load_persona.return_value = "Test persona"
        mock_agent_instance = AsyncMock()
        mock_chat_agent.return_value = mock_agent_instance

        # Create agent
        agent = IntakeAgent()
        agent.agent = mock_agent_instance

        # Mock successful response
        mock_response = AgentRunResponse(
            messages=[],
            response_id="test-id",
            created_at="2025-01-01T00:00:00Z",
            usage_details=None,
            value=Mock(),
        )
        mock_agent_instance.run.return_value = mock_response

        # Process application
        await agent.process_application(sample_loan_application)

        # Verify the message format
        mock_agent_instance.run.assert_called_once()
        message = mock_agent_instance.run.call_args[0][0]

        # Check message structure
        assert "Process this loan application for intake validation and routing:" in message
        assert sample_loan_application.application_id in message
        assert "Provide your assessment as valid JSON matching the required output format" in message

        # Verify JSON data is included
        assert '"applicant_name": "John Doe"' in message
        assert '"annual_income": 85000.0' in message


class TestIntakeAgentConfiguration:
    """Test IntakeAgent configuration and MCP tool setup."""

    @patch("loan_avengers.agents.intake_agent.MCPStreamableHTTPTool")
    @patch("loan_avengers.agents.intake_agent.PersonaLoader.load_persona")
    @patch("loan_avengers.agents.intake_agent.ChatAgent")
    def test_mcp_tool_configuration(self, mock_chat_agent, mock_load_persona, mock_mcp_tool):
        """Test that MCP tool is properly configured."""
        # Setup mocks
        mock_load_persona.return_value = "Test persona"
        mock_tool_instance = Mock()
        mock_mcp_tool.return_value = mock_tool_instance
        mock_agent_instance = Mock()
        mock_chat_agent.return_value = mock_agent_instance

        # Initialize agent
        IntakeAgent()

        # Verify MCP tool was created with correct parameters
        mock_mcp_tool.assert_called_once_with(
            name="application-verification",
            url="http://localhost:8010/sse",
            description="Application verification service for basic parameter validation",
            load_tools=True,
            load_prompts=False,
        )

        # Verify tool was passed to ChatAgent
        call_args = mock_chat_agent.call_args
        tools = call_args[1]["tools"]
        assert len(tools) == 1
        assert tools[0] == mock_tool_instance
