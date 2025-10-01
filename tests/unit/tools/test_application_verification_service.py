"""
Unit tests for the ApplicationVerificationServiceImpl class.

These tests focus on testing the validation service logic in isolation,
particularly the new validate_basic_parameters method.
"""

import json
from datetime import datetime
from decimal import Decimal

import pytest

from loan_avengers.models.application import EmploymentStatus, LoanApplication, LoanPurpose
from loan_avengers.tools.mcp_servers.application_verification.service import ApplicationVerificationServiceImpl


def serialize_test_data(data: dict) -> str:
    """Helper function to serialize test data with proper datetime handling.

    Args:
        data: Dictionary containing test data with potential datetime objects

    Returns:
        str: JSON string with proper datetime serialization
    """
    return json.dumps(data, default=lambda obj: obj.isoformat() if isinstance(obj, datetime) else str(obj))


class TestApplicationVerificationServiceImpl:
    """Test ApplicationVerificationServiceImpl methods."""

    @pytest.fixture
    def service(self) -> ApplicationVerificationServiceImpl:
        """Create service instance for testing.

        Returns:
            ApplicationVerificationServiceImpl: Service instance for testing
        """
        return ApplicationVerificationServiceImpl()

    @pytest.fixture
    def complete_application_json(self, sample_loan_application: LoanApplication) -> str:
        """Get complete application as JSON string.

        Args:
            sample_loan_application: Sample loan application fixture

        Returns:
            str: JSON representation of complete application
        """
        return sample_loan_application.model_dump_json()

    @pytest.fixture
    def vip_application_json(self, vip_loan_application: LoanApplication) -> str:
        """Get VIP application as JSON string.

        Args:
            vip_loan_application: VIP loan application fixture

        Returns:
            str: JSON representation of VIP application
        """
        return vip_loan_application.model_dump_json()

    async def test_validate_basic_parameters_complete_application(self, service, complete_application_json):
        """Test validation of a complete loan application."""
        result = await service.validate_basic_parameters(complete_application_json)

        # Verify result structure
        assert result["type"] == "basic_parameter_validation"
        assert "validation_status" in result
        assert "completeness_score" in result
        assert "routing_recommendation" in result
        assert "validation_results" in result
        assert "issues" in result
        assert "messages" in result

        # Verify validation passed
        assert result["validation_status"] == "VALID"
        assert result["completeness_score"] == 1.0  # All fields present
        assert result["routing_recommendation"] == "STANDARD"  # Standard income level

        # Verify validation details
        validation_results = result["validation_results"]
        assert validation_results["required_fields_complete"] is True
        assert validation_results["format_validation_passed"] is True
        assert validation_results["completed_fields"] == 16
        assert validation_results["total_fields"] == 16

        # Verify no issues
        assert len(result["issues"]) == 0

        # Verify success messages
        messages = result["messages"]
        assert "All required fields present and valid" in messages
        assert "Excellent profile completeness" in messages

    async def test_validate_basic_parameters_vip_application(self, service, vip_application_json):
        """Test validation of a VIP loan application (fast-track eligible)."""
        result = await service.validate_basic_parameters(vip_application_json)

        # Verify VIP routing
        assert result["validation_status"] == "VALID"
        assert result["completeness_score"] == 1.0
        assert result["routing_recommendation"] == "FAST_TRACK"  # High income

        # Verify fast-track message
        messages = result["messages"]
        assert "Profile qualifies for fast-track processing" in messages

    async def test_validate_basic_parameters_missing_required_field(self, service, sample_loan_application):
        """Test validation when required fields are missing."""
        # Remove required field
        app_data = sample_loan_application.model_dump()
        del app_data["annual_income"]
        incomplete_json = serialize_test_data(app_data)

        result = await service.validate_basic_parameters(incomplete_json)

        # Verify validation failed
        assert result["validation_status"] == "INVALID"
        assert result["completeness_score"] < 1.0
        assert result["routing_recommendation"] == "ENHANCED"

        # Verify validation details
        validation_results = result["validation_results"]
        assert validation_results["required_fields_complete"] is False
        assert validation_results["completed_fields"] < validation_results["total_fields"]

        # Verify issues reported
        assert len(result["issues"]) > 0
        assert "Missing required field: annual_income" in result["issues"]

    async def test_validate_basic_parameters_invalid_email_format(self, service, sample_loan_application):
        """Test validation with invalid email format."""
        # Set invalid email
        app_data = sample_loan_application.model_dump()
        app_data["email"] = "invalid-email-format"
        invalid_json = serialize_test_data(app_data)

        result = await service.validate_basic_parameters(invalid_json)

        # Should have format issues but still have required fields
        assert result["validation_status"] == "WARNING"  # Has required fields but format issues

        validation_results = result["validation_results"]
        assert validation_results["required_fields_complete"] is True
        assert validation_results["format_validation_passed"] is False

        # Verify format issue reported
        assert "Invalid email format" in result["issues"]

    async def test_validate_basic_parameters_negative_loan_amount(self, service, sample_loan_application):
        """Test validation with negative loan amount."""
        # Set negative loan amount
        app_data = sample_loan_application.model_dump()
        app_data["loan_amount"] = -50000.0
        invalid_json = serialize_test_data(app_data)

        result = await service.validate_basic_parameters(invalid_json)

        # Should have format issues
        validation_results = result["validation_results"]
        assert validation_results["format_validation_passed"] is False

        # Verify issue reported
        assert "Loan amount must be greater than zero" in result["issues"]

    async def test_validate_basic_parameters_negative_annual_income(self, service, sample_loan_application):
        """Test validation with negative annual income."""
        # Set negative income
        app_data = sample_loan_application.model_dump()
        app_data["annual_income"] = -1000.0
        invalid_json = serialize_test_data(app_data)

        result = await service.validate_basic_parameters(invalid_json)

        # Should have format issues
        validation_results = result["validation_results"]
        assert validation_results["format_validation_passed"] is False

        # Verify issue reported
        assert "Annual income cannot be negative" in result["issues"]

    async def test_validate_basic_parameters_low_completeness_score(self, service):
        """Test validation with minimal required fields only."""
        # Create minimal application with valid phone number
        minimal_app = LoanApplication(
            application_id="LN1111111111",
            applicant_name="Minimal User",
            applicant_id="850e8400-e29b-41d4-a716-446655440003",
            email="minimal@example.com",
            phone="+15552345678",  # Valid US phone (area code 555, exchange 234)
            date_of_birth=datetime(1995, 1, 1),
            loan_amount=Decimal("100000.00"),
            loan_purpose=LoanPurpose.PERSONAL,
            loan_term_months=120,
            annual_income=Decimal("40000.00"),  # Low income
            employment_status=EmploymentStatus.EMPLOYED,
        )
        minimal_json = minimal_app.model_dump_json()

        result = await service.validate_basic_parameters(minimal_json)

        # Should be valid but with lower completeness
        assert result["validation_status"] == "VALID"
        assert result["completeness_score"] < 0.8  # Missing optional fields
        # Routing is ENHANCED only if completeness < 0.6, otherwise STANDARD
        assert result["routing_recommendation"] in ["STANDARD", "ENHANCED"]

    async def test_validate_basic_parameters_invalid_json(self, service):
        """Test validation with invalid JSON input."""
        invalid_json = "{ invalid json format"

        result = await service.validate_basic_parameters(invalid_json)

        # Should return error status
        assert result["validation_status"] == "ERROR"
        assert result["completeness_score"] == 0.0
        assert result["routing_recommendation"] == "ENHANCED"

        # Verify error details
        validation_results = result["validation_results"]
        assert validation_results["required_fields_complete"] is False
        assert validation_results["format_validation_passed"] is False

        # Verify error message
        assert len(result["issues"]) > 0
        assert "Invalid JSON format" in result["issues"][0]
        assert "Unable to parse application data" in result["messages"]

    async def test_validate_basic_parameters_exception_handling(self, service):
        """Test validation service exception handling."""
        # Pass None to trigger exception
        result = await service.validate_basic_parameters(None)

        # Should return error status
        assert result["validation_status"] == "ERROR"
        assert result["completeness_score"] == 0.0
        assert result["routing_recommendation"] == "ENHANCED"

        # Verify error handling
        assert "Validation error" in result["issues"][0]
        assert "Validation service encountered an error" in result["messages"]

    async def test_completeness_score_calculation(self, service):
        """Test completeness score calculation logic."""
        # Create application with exactly half the fields
        partial_app_data = {
            "application_id": "LN2222222222",
            "applicant_name": "Partial User",
            "applicant_id": "950e8400-e29b-41d4-a716-446655440004",
            "email": "partial@example.com",
            "phone": "+12345678901",  # Valid US phone (area code 234, exchange 567)
            "date_of_birth": "1990-06-15T00:00:00",
            "loan_amount": 150000.0,
            "loan_purpose": "home_purchase",
            "loan_term_months": 360,
            "annual_income": 70000.0,
            "employment_status": "employed",
            # Missing all optional fields (5 out of 16 total)
        }
        partial_json = serialize_test_data(partial_app_data)

        result = await service.validate_basic_parameters(partial_json)

        # Verify completeness score reflects partial completion
        # Service calculates based on actual field counting logic
        assert result["completeness_score"] < 0.7  # Missing optional fields
        assert result["completeness_score"] > 0.5  # Has most required fields

    @pytest.mark.parametrize(
        "income,expected_routing",
        [
            (80000.0, "STANDARD"),  # Standard income with full profile
            (160000.0, "FAST_TRACK"),  # VIP income (>= 150k)
        ],
    )
    async def test_routing_recommendations_by_income(self, service, sample_loan_application, income, expected_routing):
        """Test routing recommendations based on income levels.

        Note: ENHANCED routing only triggers if completeness < 0.6 or validation fails.
        With full sample_loan_application (completeness = 1.0), income alone doesn't
        trigger ENHANCED routing - only STANDARD or FAST_TRACK.
        """
        # Modify income
        app_data = sample_loan_application.model_dump()
        app_data["annual_income"] = income
        app_json = serialize_test_data(app_data)

        result = await service.validate_basic_parameters(app_json)

        # Verify routing matches income level
        assert result["routing_recommendation"] == expected_routing


class TestLegacyApplicationVerificationMethods:
    """Test the existing mock methods in ApplicationVerificationServiceImpl."""

    @pytest.fixture
    def service(self) -> ApplicationVerificationServiceImpl:
        """Create service instance for testing.

        Returns:
            ApplicationVerificationServiceImpl: Service instance for testing legacy methods
        """
        return ApplicationVerificationServiceImpl()

    async def test_retrieve_credit_report(self, service):
        """Test credit report retrieval mock."""
        result = await service.retrieve_credit_report("test-applicant-id", "John Doe", "123 Main St")

        # Verify result structure
        assert result["type"] == "credit_report"
        assert result["applicant_id"] == "test-applicant-id"
        assert result["full_name"] == "John Doe"
        assert result["address"] == "123 Main St"
        assert "credit_score" in result
        assert result["credit_score"] >= 620 and result["credit_score"] <= 780

    async def test_verify_employment(self, service):
        """Test employment verification mock."""
        result = await service.verify_employment("test-applicant-id", "Tech Corp", "Software Engineer")

        # Verify result structure
        assert result["type"] == "employment_verification"
        assert result["applicant_id"] == "test-applicant-id"
        assert result["employer_name"] == "Tech Corp"
        assert result["position"] == "Software Engineer"
        assert result["employment_status"] == "verified"

    async def test_get_bank_account_data(self, service):
        """Test bank account data retrieval mock."""
        result = await service.get_bank_account_data("1234567890", "021000021")

        # Verify result structure
        assert result["type"] == "bank_account_data"
        assert result["account_number_suffix"] == "7890"
        assert result["routing_number"] == "021000021"
        assert "current_balance" in result
