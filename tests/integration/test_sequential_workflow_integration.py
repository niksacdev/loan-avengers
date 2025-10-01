"""Integration tests for MockSequentialLoanWorkflow (placeholder for future real workflow)."""

from collections.abc import Generator
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Skip all tests in this module - these test a workflow that was removed during refactoring
# The MockSequentialLoanWorkflow is a simple mock without agent framework dependencies
# TODO: Create new integration tests for ConversationOrchestrator + LoanProcessingPipeline
pytestmark = pytest.mark.skip(reason="SequentialLoanWorkflow was removed during refactoring")


class TestSequentialLoanWorkflowIntegration:
    """Integration tests for MockSequentialLoanWorkflow."""

    @pytest.fixture
    def mock_chat_client(self) -> Mock:
        """Create mock chat client.

        Returns:
            Mock: Mock chat client for testing workflows
        """
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def mock_agent_framework(self) -> dict:
        """Mock agent framework components.

        Yields:
            dict: Dictionary containing mocked ChatAgent and SequentialBuilder
        """
        with (
            patch("loan_avengers.agents.mock_sequential_workflow.ChatAgent") as mock_chat_agent,
            patch("loan_avengers.agents.mock_sequential_workflow.SequentialBuilder") as mock_builder,
        ):
            mock_chat_agent.return_value = Mock()
            mock_builder.return_value = Mock()
            yield {"ChatAgent": mock_chat_agent, "SequentialBuilder": mock_builder}

    @pytest.fixture
    def mock_persona_loader(self) -> Mock:
        """Mock persona loader.

        Yields:
            Mock: Mocked PersonaLoader with default persona instructions
        """
        with patch("loan_avengers.agents.mock_sequential_workflow.PersonaLoader") as mock_loader:
            mock_loader.load_persona.return_value = "Mock persona instructions"
            yield mock_loader

    def test_workflow_initialization(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test workflow initializes correctly."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        assert workflow is not None
        assert workflow.chat_client is mock_chat_client

    def test_workflow_creates_coordinator_collector(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test coordinator collector agent creation."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        _workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        # Verify persona was loaded
        mock_persona_loader.load_persona.assert_any_call("coordinator")

        # Verify ChatAgent was created
        assert mock_agent_framework["ChatAgent"].called

    def test_workflow_creates_intake_validator(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test intake validator agent creation."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        _workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        # Verify intake persona was loaded
        mock_persona_loader.load_persona.assert_any_call("intake")

    def test_workflow_creates_credit_assessor(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test credit assessor agent creation."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        # Credit agent is created with inline instructions (TODO to load persona)
        # Just verify workflow initialized
        assert workflow.credit_assessor is not None

    def test_workflow_creates_income_verifier(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test income verifier agent creation."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        assert workflow.income_verifier is not None

    def test_workflow_creates_risk_analyzer(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test risk analyzer agent creation."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        assert workflow.risk_analyzer is not None

    def test_workflow_builds_sequential_workflow(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test workflow builds sequential workflow."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        _workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        # Verify SequentialBuilder was used
        assert mock_agent_framework["SequentialBuilder"].called

    def test_workflow_with_default_client(self, mock_agent_framework, mock_persona_loader):
        """Test workflow creates default client if none provided."""
        with (
            patch("loan_avengers.agents.mock_sequential_workflow.FoundryChatClient") as mock_foundry,
            patch("loan_avengers.agents.mock_sequential_workflow.DefaultAzureCredential") as mock_credential,
        ):
            mock_foundry.return_value = Mock()
            mock_credential.return_value = Mock()

            from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

            workflow = MockSequentialLoanWorkflow()

            # Should create FoundryChatClient with DefaultAzureCredential
            assert mock_foundry.called
            assert mock_credential.called
            assert workflow.chat_client is not None

    @pytest.mark.asyncio
    async def test_process_conversation_with_empty_history(
        self, mock_chat_client, mock_agent_framework, mock_persona_loader
    ):
        """Test processing conversation with empty history."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        # Mock workflow.workflow.run to return async generator
        async def mock_run(*args, **kwargs):
            yield Mock(content="Test response", metadata={})

        workflow.workflow = Mock()
        workflow.workflow.run = mock_run

        # Mock thread and shared_state
        mock_thread = Mock()
        mock_thread.conversation_history = []

        with patch("loan_avengers.agents.mock_sequential_workflow.SharedState") as mock_state:
            mock_state.return_value = AsyncMock()

            # Process conversation
            responses = []
            async for response in workflow.process_conversation("Test message", mock_thread, mock_state()):
                responses.append(response)
                break  # Just test one iteration

    def test_create_loan_application_with_complete_data(
        self, mock_chat_client, mock_agent_framework, mock_persona_loader
    ):
        """Test creating LoanApplication from collected data."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        collected_data = {
            "applicant_name": "Integration Test User",
            "email": "integration@example.com",
            "phone": "5559999999",
            "date_of_birth": "1989-09-09",
            "loan_amount": 280000,
            "loan_purpose": "home_purchase",
            "loan_term_months": 360,
            "annual_income": 82000,
            "employment_status": "employed",
            "employer_name": "Integration Corp",
            "months_employed": 30,
        }

        loan_app = workflow.create_loan_application(collected_data)

        assert loan_app.applicant_name == "Integration Test User"
        assert loan_app.email == "integration@example.com"
        assert loan_app.loan_amount == 280000
        assert loan_app.annual_income == 82000

    def test_create_loan_application_with_invalid_data_raises_error(
        self, mock_chat_client, mock_agent_framework, mock_persona_loader
    ):
        """Test creating LoanApplication with invalid data raises ValueError."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        invalid_data = {"applicant_name": "Invalid User"}  # Missing required fields

        with pytest.raises(ValueError, match="Invalid workflow data"):
            workflow.create_loan_application(invalid_data)

    def test_workflow_agent_temperature_settings(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test agents have appropriate temperature settings."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        _workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        # Check ChatAgent was called with temperature parameter
        calls = mock_agent_framework["ChatAgent"].call_args_list

        # Coordinator should have higher temperature (0.7)
        # Other agents should have lower temperature (0.1-0.2)
        temperatures = []
        for call in calls:
            if "temperature" in call.kwargs:
                temperatures.append(call.kwargs["temperature"])

        assert len(temperatures) > 0
        assert any(t >= 0.5 for t in temperatures)  # Coordinator
        assert any(t <= 0.3 for t in temperatures)  # Validators/Assessors

    def test_workflow_agent_max_tokens_settings(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test agents have appropriate max_tokens settings."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        _workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        # Check ChatAgent was called with max_tokens parameter
        calls = mock_agent_framework["ChatAgent"].call_args_list

        max_tokens_list = []
        for call in calls:
            if "max_tokens" in call.kwargs:
                max_tokens_list.append(call.kwargs["max_tokens"])

        assert len(max_tokens_list) > 0
        # Coordinator should have higher max_tokens (800)
        assert any(t >= 700 for t in max_tokens_list)

    def test_workflow_agent_descriptions_set(self, mock_chat_client, mock_agent_framework, mock_persona_loader):
        """Test agents have descriptions set."""
        from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

        _workflow = MockSequentialLoanWorkflow(chat_client=mock_chat_client)

        # Check ChatAgent was called with description parameter
        calls = mock_agent_framework["ChatAgent"].call_args_list

        descriptions = []
        for call in calls:
            if "description" in call.kwargs:
                descriptions.append(call.kwargs["description"])

        assert len(descriptions) > 0
        # Should have meaningful descriptions
        assert all(len(desc) > 5 for desc in descriptions)


class TestSequentialWorkflowAgentCreation:
    """Test individual agent creation methods."""

    @pytest.fixture
    def workflow_with_mocks(self) -> Generator:
        """Create workflow with all mocks.

        Yields:
            MockSequentialLoanWorkflow: Workflow instance with all dependencies mocked
        """
        with (
            patch("loan_avengers.agents.mock_sequential_workflow.ChatAgent") as mock_chat_agent,
            patch("loan_avengers.agents.mock_sequential_workflow.SequentialBuilder") as mock_builder,
            patch("loan_avengers.agents.mock_sequential_workflow.PersonaLoader") as mock_persona,
            patch("loan_avengers.agents.mock_sequential_workflow.FoundryChatClient") as mock_client,
        ):
            mock_chat_agent.return_value = Mock()
            mock_builder.return_value = Mock()
            mock_persona.load_persona.return_value = "Mock persona"
            mock_client.return_value = Mock()

            from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

            workflow = MockSequentialLoanWorkflow()

            yield workflow

    def test_coordinator_collector_created(self, workflow_with_mocks):
        """Test coordinator collector is created."""
        assert workflow_with_mocks.coordinator_collector is not None

    def test_intake_validator_created(self, workflow_with_mocks):
        """Test intake validator is created."""
        assert workflow_with_mocks.intake_validator is not None

    def test_credit_assessor_created(self, workflow_with_mocks):
        """Test credit assessor is created."""
        assert workflow_with_mocks.credit_assessor is not None

    def test_income_verifier_created(self, workflow_with_mocks):
        """Test income verifier is created."""
        assert workflow_with_mocks.income_verifier is not None

    def test_risk_analyzer_created(self, workflow_with_mocks):
        """Test risk analyzer is created."""
        assert workflow_with_mocks.risk_analyzer is not None

    def test_workflow_built(self, workflow_with_mocks):
        """Test workflow is built."""
        assert workflow_with_mocks.workflow is not None


class TestSequentialWorkflowDataTransformation:
    """Test data transformation logic."""

    @pytest.fixture
    def workflow(self) -> "MockSequentialLoanWorkflow":
        """Create workflow with mocked dependencies.

        Returns:
            MockSequentialLoanWorkflow: Workflow instance with mocked framework dependencies
        """
        with (
            patch("loan_avengers.agents.mock_sequential_workflow.ChatAgent"),
            patch("loan_avengers.agents.mock_sequential_workflow.SequentialBuilder"),
            patch("loan_avengers.agents.mock_sequential_workflow.PersonaLoader") as mock_persona,
            patch("loan_avengers.agents.mock_sequential_workflow.FoundryChatClient"),
        ):
            mock_persona.load_persona.return_value = "Mock persona"

            from loan_avengers.agents.mock_sequential_workflow import MockSequentialLoanWorkflow

            return MockSequentialLoanWorkflow()

    def test_create_loan_application_maps_fields_correctly(self, workflow):
        """Test field mapping from collected data to LoanApplication."""
        data = {
            "applicant_name": "Field Mapping Test",
            "email": "fieldmap@example.com",
            "phone": "5558888888",
            "date_of_birth": "1991-11-11",
            "loan_amount": 265000,
            "loan_purpose": "home_refinance",
            "loan_term_months": 180,
            "annual_income": 78000,
            "employment_status": "self_employed",
            "employer_name": "Self Employed LLC",
            "months_employed": 120,
        }

        loan_app = workflow.create_loan_application(data)

        # Verify all fields mapped correctly
        assert loan_app.applicant_name == data["applicant_name"]
        assert loan_app.email == data["email"]
        assert loan_app.phone == data["phone"]
        assert loan_app.loan_amount == data["loan_amount"]
        assert loan_app.loan_term_months == data["loan_term_months"]
        assert loan_app.annual_income == data["annual_income"]
        assert loan_app.employer_name == data["employer_name"]

    def test_create_loan_application_handles_home_purchase(self, workflow):
        """Test creating application with home_purchase purpose."""
        data = {
            "applicant_name": "Home Buyer",
            "email": "buyer@example.com",
            "phone": "5557777777",
            "date_of_birth": "1986-06-06",
            "loan_amount": 350000,
            "loan_purpose": "home_purchase",
            "loan_term_months": 360,
            "annual_income": 95000,
            "employment_status": "employed",
            "employer_name": "Corporate Inc",
            "months_employed": 84,
        }

        loan_app = workflow.create_loan_application(data)

        assert loan_app.loan_purpose.value == "home_purchase"

    def test_create_loan_application_handles_refinance(self, workflow):
        """Test creating application with refinance purpose."""
        data = {
            "applicant_name": "Refinancer",
            "email": "refi@example.com",
            "phone": "5556666666",
            "date_of_birth": "1984-04-04",
            "loan_amount": 280000,
            "loan_purpose": "home_refinance",
            "loan_term_months": 360,
            "annual_income": 88000,
            "employment_status": "employed",
            "employer_name": "Business Corp",
            "months_employed": 96,
        }

        loan_app = workflow.create_loan_application(data)

        assert loan_app.loan_purpose.value == "home_refinance"
