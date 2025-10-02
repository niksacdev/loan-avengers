"""
Pytest configuration and shared fixtures for the loan processing system.

This module provides common fixtures and test configuration used across
unit and integration tests.
"""

import os
import tempfile
from collections.abc import AsyncGenerator, Generator
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

import pytest

try:
    from agent_framework import AgentThread
    from azure.ai.projects.models import ThreadMessage
except ImportError:
    # Fallback for when agent_framework is not available
    AgentThread = None
    ThreadMessage = None

from loan_defenders.models.application import EmploymentStatus, LoanApplication, LoanPurpose
from loan_defenders.models.responses import IntakeAssessment


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> None:
    """Set up test environment variables for unit tests only."""
    # Disable Azure Application Insights for tests
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = ""
    # Set test log level
    os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture(scope="function", autouse=True)
def setup_unit_test_environment(request) -> None:
    """Override Foundry config for unit tests only (not integration tests).

    Args:
        request: Pytest request fixture

    Yields:
        None: Fixture provides environment configuration context
    """
    from unittest.mock import patch

    # Check if this is an integration test
    if "integration" in request.keywords:
        # Integration test - use real .env values, no override
        yield
        return

    # Unit test - override with test values using patch.dict for proper isolation
    with patch.dict(
        "os.environ",
        {
            "FOUNDRY_PROJECT_ENDPOINT": "https://test-project.projects.ai.azure.com",
            "FOUNDRY_MODEL_DEPLOYMENT_NAME": "test-model",
        },
    ):
        yield


@pytest.fixture
def sample_loan_application() -> LoanApplication:
    """Create a complete sample loan application for testing."""
    return LoanApplication(
        application_id="LN1234567890",
        applicant_name="John Doe",
        applicant_id="550e8400-e29b-41d4-a716-446655440000",
        email="john.doe@example.com",
        phone="12345678901",
        date_of_birth=datetime(1990, 5, 15),
        loan_amount=Decimal("250000.00"),
        loan_purpose=LoanPurpose.HOME_PURCHASE,
        loan_term_months=360,
        annual_income=Decimal("85000.00"),
        employment_status=EmploymentStatus.EMPLOYED,
        employer_name="Tech Corp Inc",
        months_employed=36,
        monthly_expenses=Decimal("3500.00"),
        existing_debt=Decimal("25000.00"),
        assets=Decimal("50000.00"),
        down_payment=Decimal("50000.00"),
    )


@pytest.fixture
def vip_loan_application() -> LoanApplication:
    """Create a VIP loan application (high income) for testing fast-track routing."""
    return LoanApplication(
        application_id="LN9999999999",
        applicant_name="Jane VIP",
        applicant_id="650e8400-e29b-41d4-a716-446655440001",
        email="jane.vip@example.com",
        phone="19876543210",
        date_of_birth=datetime(1985, 3, 20),
        loan_amount=Decimal("500000.00"),
        loan_purpose=LoanPurpose.HOME_PURCHASE,
        loan_term_months=360,
        annual_income=Decimal("200000.00"),  # VIP income level
        employment_status=EmploymentStatus.EMPLOYED,
        employer_name="Fortune 500 Corp",
        months_employed=60,
        monthly_expenses=Decimal("6000.00"),
        existing_debt=Decimal("30000.00"),
        assets=Decimal("150000.00"),
        down_payment=Decimal("100000.00"),
    )


@pytest.fixture
def incomplete_loan_application() -> LoanApplication:
    """Create an incomplete loan application for testing validation."""
    return LoanApplication(
        application_id="LN5555555555",
        applicant_name="Bob Incomplete",
        applicant_id="750e8400-e29b-41d4-a716-446655440002",
        email="bob.incomplete@example.com",
        phone="15555551234",
        date_of_birth=datetime(1992, 8, 10),
        loan_amount=Decimal("180000.00"),
        loan_purpose=LoanPurpose.HOME_REFINANCE,
        loan_term_months=240,
        annual_income=Decimal("65000.00"),
        employment_status=EmploymentStatus.EMPLOYED,
        # Missing optional fields to test completeness scoring
    )


@pytest.fixture
def sample_intake_assessment() -> IntakeAssessment:
    """Create a sample intake assessment for testing."""
    return IntakeAssessment(
        validation_status="COMPLETE",
        routing_decision="STANDARD",
        confidence_score=0.95,
        processing_notes="Eagle eyes scan complete - application data is pristine!",
        data_quality_score=0.98,
        specialist_name="John",
        celebration_message="🦅 Eagle eyes engaged! Everything looks sharp and ready!",
        encouragement_note="Your application data is incredibly organized - these eagle eyes are impressed!",
        next_step_preview="Sarah's going to love working with such clean data!",
        animation_type="pulse",
        celebration_level="mild",
        next_agent="income",
    )


@pytest.fixture
def mock_azure_chat_client() -> Mock:
    """Create a mock Azure AI chat client for testing."""
    mock_client = Mock()

    # Mock successful response
    mock_response = Mock()
    mock_response.messages = [Mock(text="Test response", author_name="John")]
    mock_response.response_id = "test-response-id"
    mock_response.created_at = datetime.utcnow()
    mock_response.usage_details = Mock(input_token_count=100, output_token_count=50, total_token_count=150)
    mock_response.conversation_id = "test-conversation-id"
    mock_response.value = None
    mock_response.additional_properties = {}

    mock_client.get_response = AsyncMock(return_value=mock_response)
    mock_client.get_streaming_response = AsyncMock()

    return mock_client


@pytest.fixture
def sample_agent_thread() -> AgentThread:
    """Create a sample agent thread for conversation testing."""
    return AgentThread(service_thread_id="test_session_123")


@pytest.fixture
def mock_mcp_validation_result() -> dict:
    """Create a mock validation result from MCP server."""
    return {
        "validation_status": "VALID",
        "completeness_score": 0.95,
        "routing_recommendation": "STANDARD",
        "validation_results": {
            "required_fields_complete": True,
            "format_validation_passed": True,
            "completed_fields": 16,
            "total_fields": 16,
        },
        "issues": [],
        "messages": ["All required fields present and valid", "Excellent profile completeness"],
        "type": "basic_parameter_validation",
    }


@pytest.fixture
def mock_mcp_validation_result_vip() -> dict:
    """Create a mock validation result for VIP application."""
    return {
        "validation_status": "VALID",
        "completeness_score": 1.0,
        "routing_recommendation": "FAST_TRACK",
        "validation_results": {
            "required_fields_complete": True,
            "format_validation_passed": True,
            "completed_fields": 16,
            "total_fields": 16,
        },
        "issues": [],
        "messages": [
            "All required fields present and valid",
            "Excellent profile completeness",
            "Profile qualifies for fast-track processing",
        ],
        "type": "basic_parameter_validation",
    }


@pytest.fixture
def mock_mcp_validation_result_incomplete() -> dict:
    """Create a mock validation result for incomplete application."""
    return {
        "validation_status": "INVALID",
        "completeness_score": 0.75,
        "routing_recommendation": "ENHANCED",
        "validation_results": {
            "required_fields_complete": False,
            "format_validation_passed": True,
            "completed_fields": 12,
            "total_fields": 16,
        },
        "issues": ["Missing required field: employer_name", "Missing required field: months_employed"],
        "messages": [],
        "type": "basic_parameter_validation",
    }


@pytest.fixture
def temp_directory() -> Generator[str, None, None]:
    """Create a temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Async fixtures for integration tests
@pytest.fixture
async def mock_running_mcp_server() -> AsyncGenerator[dict, None]:
    """Mock a running MCP server for integration tests."""
    # This would normally start an actual MCP server process
    # For now, we'll return connection info for mocking
    server_info = {
        "host": "localhost",
        "port": 8010,
        "url": "http://localhost:8010/sse",
        "status": "running",
    }
    yield server_info
    # Cleanup would happen here


# Pytest configuration for async tests
pytest_plugins = ["pytest_asyncio"]
