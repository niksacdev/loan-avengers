"""
End-to-end integration tests for SequentialPipeline.

Tests the complete multi-agent workflow with mock MCP servers,
validating that all agents coordinate correctly via SequentialBuilder.
"""

from unittest.mock import Mock, patch

import pytest

from loan_avengers.models.application import LoanApplication
from loan_avengers.orchestrators.sequential_pipeline import SequentialPipeline
from tests.fixtures.mcp_test_harness import MCPTestHarness


@pytest.fixture
def mcp_harness():
    """Provide MCP test harness for integration tests."""
    harness = MCPTestHarness()
    yield harness
    harness.reset_all()


@pytest.fixture
def mock_chat_client():
    """Mock AzureAIAgentClient for testing."""
    client = Mock()

    # Mock create_agent to return a ChatAgent-like object
    mock_agent = Mock()
    mock_agent.name = "TestAgent"
    client.create_agent = Mock(return_value=mock_agent)

    return client


@pytest.fixture
def sample_loan_application():
    """Provide sample loan application for testing."""
    return LoanApplication(
        application_id="LN1234567890",
        applicant_name="Tony Stark",
        applicant_id="550e8400-e29b-41d4-a716-446655440000",
        email="tony@starkindustries.com",
        phone="5555551234",
        date_of_birth="1970-05-29",
        loan_amount=500000.0,
        loan_purpose="home_purchase",
        loan_term_months=360,
        annual_income=200000.0,
        employment_status="employed",
        employer_name="Stark Industries",
        months_employed=120,
        down_payment=100000.0,
    )


@pytest.mark.asyncio
class TestSequentialPipelineIntegration:
    """Integration tests for SequentialPipeline with mock MCP servers."""

    async def test_pipeline_initialization(self, mock_chat_client, mcp_harness):
        """Test that pipeline initializes all agents correctly."""
        pipeline = SequentialPipeline(chat_client=mock_chat_client)

        # Verify all agents are initialized
        assert pipeline.intake_agent is not None
        assert pipeline.credit_agent is not None
        assert pipeline.income_agent is not None
        assert pipeline.risk_agent is not None

        # Verify agents have correct MCP tools
        assert pipeline.intake_agent.mcp_tool.name == "application-verification"
        assert pipeline.credit_agent.verification_tool.name == "application-verification"
        assert pipeline.credit_agent.calculations_tool.name == "financial-calculations"
        assert pipeline.income_agent.verification_tool.name == "application-verification"
        assert pipeline.income_agent.documents_tool.name == "document-processing"
        assert pipeline.income_agent.calculations_tool.name == "financial-calculations"

    async def test_agent_creation_for_sequential_builder(self, mock_chat_client, mcp_harness):
        """Test that agents can create ChatAgent instances for SequentialBuilder."""
        pipeline = SequentialPipeline(chat_client=mock_chat_client)

        # Create agents for SequentialBuilder
        intake_chat = pipeline.intake_agent.create_agent()
        credit_chat = pipeline.credit_agent.create_agent()
        income_chat = pipeline.income_agent.create_agent()
        risk_chat = pipeline.risk_agent.create_agent()

        # Verify all agents created successfully
        assert intake_chat is not None
        assert credit_chat is not None
        assert income_chat is not None
        assert risk_chat is not None

        # Verify create_agent was called with correct parameters
        assert mock_chat_client.create_agent.call_count == 4

    @patch("loan_avengers.orchestrators.sequential_pipeline.SequentialBuilder")
    async def test_workflow_creation(self, mock_builder_class, mock_chat_client, sample_loan_application):
        """Test that SequentialBuilder workflow is created correctly."""
        # Set up mock SequentialBuilder
        mock_workflow = Mock()
        mock_builder = Mock()
        mock_builder.participants.return_value.build.return_value = mock_workflow
        mock_builder_class.return_value = mock_builder

        # Mock async generator for run_stream
        async def mock_stream(input_text):
            yield Mock(executor_id="Intake_Agent")
            yield Mock(executor_id="Credit_Assessor")
            yield Mock(executor_id="Income_Verifier")
            yield Mock(executor_id="Risk_Analyzer")

        mock_workflow.run_stream = mock_stream

        pipeline = SequentialPipeline(chat_client=mock_chat_client)

        # Process application
        updates = []
        async for update in pipeline.process_application(sample_loan_application):
            updates.append(update)

        # Verify workflow was built with all agents
        mock_builder.participants.assert_called_once()
        participants = mock_builder.participants.call_args[0][0]
        assert len(participants) == 4  # All 4 agents

        # Verify workflow was executed
        assert len(updates) > 0


@pytest.mark.asyncio
class TestApprovalScenario:
    """Test complete approval scenario end-to-end."""

    @patch("loan_avengers.orchestrators.sequential_pipeline.SequentialBuilder")
    async def test_approval_workflow(self, mock_builder_class, mock_chat_client, sample_loan_application, mcp_harness):
        """Test complete approval workflow with mock MCP responses."""
        # Configure approval scenario
        mcp_harness.configure_approval_scenario()

        # Set up mock workflow
        mock_workflow = Mock()
        mock_builder = Mock()
        mock_builder.participants.return_value.build.return_value = mock_workflow
        mock_builder_class.return_value = mock_builder

        # Mock events for each agent
        async def mock_stream(input_text):
            # Intake validates application
            yield Mock(executor_id="Intake_Agent", status="in_progress")

            # Credit checks credit score
            yield Mock(executor_id="Credit_Assessor", status="in_progress")

            # Income verifies employment
            yield Mock(executor_id="Income_Verifier", status="in_progress")

            # Risk makes final decision
            yield Mock(executor_id="Risk_Analyzer", status="in_progress")
            yield Mock(executor_id="Risk_Analyzer", status="completed")

        mock_workflow.run_stream = mock_stream

        pipeline = SequentialPipeline(chat_client=mock_chat_client)

        # Process application
        updates = []
        async for update in pipeline.process_application(sample_loan_application):
            updates.append(update)

        # Verify all phases completed
        assert len(updates) >= 4
        phases = [u.phase for u in updates]
        assert "validating" in phases
        assert "assessing_credit" in phases
        assert "verifying_income" in phases
        assert "deciding" in phases

        # Verify final completion
        final_update = updates[-1]
        assert final_update.completion_percentage == 100


@pytest.mark.asyncio
class TestRejectionScenario:
    """Test complete rejection scenario end-to-end."""

    @patch("loan_avengers.orchestrators.sequential_pipeline.SequentialBuilder")
    async def test_rejection_workflow(self, mock_builder_class, mock_chat_client, sample_loan_application, mcp_harness):
        """Test complete rejection workflow with poor credit."""
        # Configure rejection scenario (low credit score, high DTI)
        mcp_harness.configure_rejection_scenario()

        # Set up mock workflow
        mock_workflow = Mock()
        mock_builder = Mock()
        mock_builder.participants.return_value.build.return_value = mock_workflow
        mock_builder_class.return_value = mock_builder

        # Mock events for rejection scenario
        async def mock_stream(input_text):
            yield Mock(executor_id="Intake_Agent", status="in_progress")
            yield Mock(executor_id="Credit_Assessor", status="in_progress")
            yield Mock(executor_id="Income_Verifier", status="in_progress")
            yield Mock(executor_id="Risk_Analyzer", status="in_progress")
            yield Mock(executor_id="Risk_Analyzer", status="completed")

        mock_workflow.run_stream = mock_stream

        pipeline = SequentialPipeline(chat_client=mock_chat_client)

        # Process application
        updates = []
        async for update in pipeline.process_application(sample_loan_application):
            updates.append(update)

        # Verify workflow completed even for rejection
        assert len(updates) >= 4
        final_update = updates[-1]
        assert final_update.status == "completed"
        assert final_update.completion_percentage == 100


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling in the pipeline."""

    @patch("loan_avengers.orchestrators.sequential_pipeline.SequentialBuilder")
    async def test_pipeline_handles_exceptions(self, mock_builder_class, mock_chat_client, sample_loan_application):
        """Test that pipeline handles exceptions gracefully."""
        # Set up mock workflow that raises exception
        mock_workflow = Mock()
        mock_builder = Mock()
        mock_builder.participants.return_value.build.return_value = mock_workflow
        mock_builder_class.return_value = mock_builder

        async def mock_stream_with_error(input_text):
            yield Mock(executor_id="Intake_Agent")
            raise RuntimeError("Simulated agent failure")

        mock_workflow.run_stream = mock_stream_with_error

        pipeline = SequentialPipeline(chat_client=mock_chat_client)

        # Process application and expect error handling
        updates = []
        async for update in pipeline.process_application(sample_loan_application):
            updates.append(update)

        # Verify error update was yielded
        assert len(updates) > 0
        error_update = updates[-1]
        assert error_update.status == "error"
        assert "error" in error_update.phase
