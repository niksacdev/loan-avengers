"""
Unit tests for the FinancialCalculationsServiceImpl class.

These tests focus on testing the financial calculations service logic in isolation,
ensuring accurate calculations and proper error handling.
"""

import pytest

from loan_avengers.tools.mcp_servers.financial_calculations.service import FinancialCalculationsServiceImpl


class TestFinancialCalculationsServiceImpl:
    """Test FinancialCalculationsServiceImpl methods."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FinancialCalculationsServiceImpl()

    async def test_calculate_debt_to_income_ratio_excellent(self, service):
        """Test DTI calculation with excellent qualification."""
        result = await service.calculate_debt_to_income_ratio(monthly_income=6000.0, monthly_debt_payments=1800.0)

        # Verify result structure
        assert result["type"] == "dti_calculation"
        assert result["monthly_income"] == 6000.0
        assert result["monthly_debt_payments"] == 1800.0

        # DTI should be 30% (1800/6000 * 100)
        assert result["debt_to_income_ratio"] == 30.0
        assert result["qualification_status"] == "excellent"
        assert result["risk_level"] == "low"
        assert "max_additional_debt" in result

    async def test_calculate_debt_to_income_ratio_good(self, service):
        """Test DTI calculation with good qualification."""
        result = await service.calculate_debt_to_income_ratio(monthly_income=5000.0, monthly_debt_payments=2000.0)

        # DTI should be 40% (2000/5000 * 100)
        assert result["debt_to_income_ratio"] == 40.0
        assert result["qualification_status"] == "good"
        assert result["risk_level"] == "moderate"

    async def test_calculate_debt_to_income_ratio_poor(self, service):
        """Test DTI calculation with poor qualification."""
        result = await service.calculate_debt_to_income_ratio(monthly_income=4000.0, monthly_debt_payments=2500.0)

        # DTI should be 62.5% (2500/4000 * 100)
        assert result["debt_to_income_ratio"] == 62.5
        assert result["qualification_status"] == "poor"
        assert result["risk_level"] == "very_high"

    async def test_calculate_debt_to_income_ratio_invalid_income(self, service):
        """Test DTI calculation with invalid income."""
        result = await service.calculate_debt_to_income_ratio(monthly_income=0, monthly_debt_payments=1000.0)

        # Should return error
        assert result["type"] == "calculation_error"
        assert "error" in result

    async def test_calculate_monthly_payment_standard(self, service):
        """Test monthly payment calculation with standard loan."""
        loan_amount = 100000.0
        result = await service.calculate_monthly_payment(
            loan_amount=loan_amount,
            interest_rate=0.05,
            loan_term_months=360,  # 5% annual
        )

        # Verify result structure
        assert result["type"] == "payment_calculation"
        assert result["loan_amount"] == 100000.0
        assert result["annual_interest_rate"] == 0.05
        assert result["term_months"] == 360

        # Monthly payment should be around $536.82 for 100k at 5% over 30 years
        assert 530 < result["monthly_payment"] < 545
        assert result["total_interest"] > 0
        assert result["total_payment"] > loan_amount

    async def test_calculate_monthly_payment_zero_interest(self, service):
        """Test monthly payment calculation with zero interest."""
        result = await service.calculate_monthly_payment(
            loan_amount=12000.0,
            interest_rate=0.0,
            loan_term_months=12,  # 0% interest
        )

        # Monthly payment should be exactly loan_amount / term_months
        assert result["monthly_payment"] == 1000.0
        assert result["total_interest"] == 0.0

    async def test_calculate_loan_affordability_affordable(self, service):
        """Test loan affordability calculation for affordable scenario."""
        result = await service.calculate_loan_affordability(
            monthly_income=8000.0, existing_debt=1000.0, loan_amount=150000.0, interest_rate=0.04, loan_term_months=360
        )

        # Verify result structure
        assert result["type"] == "affordability_assessment"
        assert result["loan_amount"] == 150000.0
        assert "monthly_payment" in result
        assert "total_monthly_debt" in result
        assert "debt_to_income_ratio" in result
        assert result["affordability_status"] in ["highly_affordable", "affordable", "marginal", "unaffordable"]
        assert 0 <= result["approval_probability"] <= 1

    async def test_calculate_loan_affordability_unaffordable(self, service):
        """Test loan affordability calculation for unaffordable scenario."""
        result = await service.calculate_loan_affordability(
            monthly_income=3000.0,
            existing_debt=1500.0,
            loan_amount=200000.0,
            interest_rate=0.06,
            loan_term_months=360,
        )

        # With high debt and low income, should be unaffordable
        assert result["debt_to_income_ratio"] > 50
        assert result["affordability_status"] == "unaffordable"

    async def test_calculate_credit_utilization_ratio_excellent(self, service):
        """Test credit utilization with excellent rating."""
        result = await service.calculate_credit_utilization_ratio(
            total_credit_used=500.0, total_credit_available=10000.0
        )

        # 5% utilization should be excellent
        assert result["type"] == "utilization_calculation"
        assert result["utilization_ratio"] == 5.0
        assert result["credit_impact"] == "excellent"
        assert result["available_credit"] == 9500.0

    async def test_calculate_credit_utilization_ratio_poor(self, service):
        """Test credit utilization with poor rating."""
        result = await service.calculate_credit_utilization_ratio(
            total_credit_used=8000.0, total_credit_available=10000.0
        )

        # 80% utilization should be poor
        assert result["utilization_ratio"] == 80.0
        assert result["credit_impact"] == "poor"

    async def test_calculate_credit_utilization_ratio_invalid(self, service):
        """Test credit utilization with invalid input."""
        result = await service.calculate_credit_utilization_ratio(total_credit_used=5000.0, total_credit_available=0)

        # Should return error
        assert result["type"] == "calculation_error"
        assert "error" in result

    async def test_calculate_total_debt_service_ratio_qualified(self, service):
        """Test TDSR calculation with qualified status."""
        result = await service.calculate_total_debt_service_ratio(
            monthly_income=10000.0, total_monthly_debt=3000.0, property_taxes=500.0, insurance=200.0, hoa_fees=100.0
        )

        # Total debt = 3000 + 500 + 200 + 100 = 3800
        # TDSR = 3800/10000 * 100 = 38%
        assert result["type"] == "tdsr_calculation"
        assert result["total_housing_expenses"] == 800.0
        assert result["total_debt_payments"] == 3800.0
        assert result["total_debt_service_ratio"] == 38.0
        assert result["qualification_status"] == "qualified"
        assert result["risk_assessment"] == "low_risk"

    async def test_calculate_total_debt_service_ratio_unqualified(self, service):
        """Test TDSR calculation with unqualified status."""
        result = await service.calculate_total_debt_service_ratio(
            monthly_income=5000.0, total_monthly_debt=3000.0, property_taxes=500.0, insurance=300.0, hoa_fees=200.0
        )

        # Total debt = 3000 + 500 + 300 + 200 = 4000
        # TDSR = 4000/5000 * 100 = 80%
        assert result["total_debt_service_ratio"] == 80.0
        assert result["qualification_status"] == "unqualified"
        assert result["risk_assessment"] == "high_risk"

    async def test_analyze_income_stability_stable(self, service):
        """Test income stability analysis with stable income."""
        income_history = [
            {"amount": 5000.0, "month": "2024-01"},
            {"amount": 5100.0, "month": "2024-02"},
            {"amount": 4950.0, "month": "2024-03"},
            {"amount": 5050.0, "month": "2024-04"},
        ]
        employment_history = [{"month": f"2024-{i:02d}", "employer": "TechCorp"} for i in range(1, 25)]

        result = await service.analyze_income_stability(income_history, employment_history)

        # Verify result structure
        assert result["type"] == "income_stability_analysis"
        assert result["income_count"] == 4
        assert 4900 < result["average_income"] < 5100
        assert result["stability_rating"] in ["very_stable", "stable", "variable", "unstable"]
        assert result["employment_months"] == 24
        assert result["employment_stability"] == "stable"

    async def test_analyze_income_stability_unstable(self, service):
        """Test income stability analysis with unstable income."""
        income_history = [
            {"amount": 2000.0, "month": "2024-01"},
            {"amount": 5000.0, "month": "2024-02"},
            {"amount": 1000.0, "month": "2024-03"},
            {"amount": 7000.0, "month": "2024-04"},
        ]
        employment_history = [{"month": f"2024-{i:02d}", "employer": "Various"} for i in range(1, 7)]

        result = await service.analyze_income_stability(income_history, employment_history)

        # High variance should result in unstable rating
        assert result["income_variance"] > 35  # High coefficient of variation
        assert result["stability_rating"] in ["unstable", "variable"]
        assert result["income_risk_level"] in ["high", "very_high"]
        assert result["employment_months"] == 6
        assert result["employment_stability"] == "insufficient"

    async def test_analyze_income_stability_no_history(self, service):
        """Test income stability analysis with no income history."""
        result = await service.analyze_income_stability(income_history=[], employment_history=[])

        # Should return error
        assert result["type"] == "analysis_error"
        assert "error" in result
