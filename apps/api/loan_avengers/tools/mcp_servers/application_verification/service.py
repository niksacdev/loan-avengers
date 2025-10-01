"""
Application Verification Service Implementation (Mock).

Implements the ApplicationVerificationService interface with mock logic.
The MCP server calls into this service and returns JSON strings to clients.
"""

from __future__ import annotations

import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from loan_avengers.tools.services.application_verification import ApplicationVerificationService  # noqa: E402
from loan_avengers.utils.observability import Observability  # noqa: E402

# Initialize logging (observability auto-initializes)
logger = Observability.get_logger("application_verification_service")


class ApplicationVerificationServiceImpl(ApplicationVerificationService):
    """
    Mock implementation providing deterministic structures with slight
    randomization to simulate real-world variability for demos.
    """

    async def retrieve_credit_report(self, applicant_id: str, full_name: str, address: str) -> dict[str, Any]:
        logger.info(f"Retrieving credit report for {full_name} (ID: {applicant_id[:8]}***) at address: {address}")

        score = random.randint(620, 780)
        utilization = round(random.uniform(0.15, 0.45), 2)
        payment_history = round(random.uniform(0.85, 0.99), 2)
        inquiries = random.randint(0, 5)

        risk_level = "low" if score >= 740 else "medium" if score >= 680 else "high"
        recommendation = "approve" if score >= 700 and utilization <= 0.3 else "review"

        logger.info(
            f"Credit report analysis completed - Score: {score}, Risk: {risk_level}, Recommendation: {recommendation}"
        )

        return {
            "applicant_id": applicant_id,
            "full_name": full_name,
            "address": address,
            "credit_score": score,
            "credit_bureau": random.choice(["Experian", "Equifax", "TransUnion"]),
            "credit_utilization": utilization,
            "payment_history_score": payment_history,
            "recent_inquiries": inquiries,
            "delinquencies": random.randint(0, 2),
            "bankruptcies": 0,
            "trade_lines": random.randint(3, 12),
            "risk_level": risk_level,
            "recommendation": recommendation,
            "type": "credit_report",
        }

    async def verify_employment(self, applicant_id: str, employer_name: str, position: str) -> dict[str, Any]:
        logger.info(f"Verifying employment for {position} at {employer_name} (ID: {applicant_id[:8]}***)")

        income = random.randint(50000, 120000)
        tenure_months = random.randint(6, 60)
        employment_type = random.choice(["full-time", "part-time", "contract"])

        verification_status = "verified" if tenure_months >= 12 else "conditional"

        logger.info(
            f"Employment verification completed - Status: {verification_status}, "
            f"Annual Income: ${income}, Tenure: {tenure_months} months"
        )

        return {
            "applicant_id": applicant_id,
            "employer_name": employer_name,
            "position": position,
            "employment_status": "verified",
            "employment_type": employment_type,
            "annual_income": income,
            "tenure_months": tenure_months,
            "verification_date": datetime.now().isoformat(),
            "hr_contact": f"hr@{employer_name.lower().replace(' ', '')}.com",
            "income_stability": "stable" if tenure_months >= 24 else "developing",
            "recommendation": "verify" if income >= 50000 and employment_type == "full-time" else "review",
            "type": "employment_verification",
        }

    async def get_bank_account_data(self, account_number: str, routing_number: str) -> dict[str, Any]:
        balance = round(random.uniform(500, 25000), 2)

        return {
            "account_number_suffix": account_number[-4:],
            "routing_number": routing_number,
            "current_balance": balance,
            "average_daily_balance": round(balance * random.uniform(0.8, 1.0), 2),
            "owner_verified": True,
            "recent_transactions": [
                {"date": "2025-07-28", "amount": -125.34, "description": "Utility Bill"},
                {"date": "2025-07-22", "amount": -58.12, "description": "Groceries"},
                {"date": "2025-07-15", "amount": 3250.00, "description": "Payroll"},
            ],
            "overdrafts_last_90_days": random.randint(0, 1),
            "type": "bank_account_data",
        }

    async def get_tax_transcript_data(self, applicant_id: str, tax_year: int) -> dict[str, Any]:
        agi = round(random.uniform(55000, 150000), 2)

        return {
            "applicant_id": applicant_id,
            "tax_year": tax_year,
            "adjusted_gross_income": agi,
            "total_income": round(agi * random.uniform(1.0, 1.2), 2),
            "taxable_income": round(agi * random.uniform(0.7, 0.9), 2),
            "withholding": round(agi * random.uniform(0.15, 0.25), 2),
            "refund_or_amount_owed": round(random.uniform(-2500, 2500), 2),
            "filing_status": random.choice(["single", "married_joint", "head_of_household"]),
            "type": "tax_transcript",
        }

    async def verify_asset_information(self, asset_type: str, asset_details: dict[str, Any]) -> dict[str, Any]:
        value = round(random.uniform(10000, 500000), 2)

        return {
            "asset_type": asset_type,
            "asset_details": asset_details,
            "ownership_verified": True,
            "estimated_value": value,
            "liquidity_score": round(random.uniform(0.3, 0.9), 2),
            "lien_check": False,
            "verification_confidence": round(random.uniform(0.75, 0.95), 2),
            "type": "asset_verification",
        }

    async def validate_basic_parameters(self, application_data: str) -> dict[str, Any]:
        """
        Validate basic loan application parameters for intake agent.

        Performs lightweight validation focusing on:
        - Required field completeness
        - Basic data format validation
        - Profile completeness scoring
        - Routing recommendations based on profile strength

        This is specifically for intake validation - NOT comprehensive business rule validation.
        """
        import json

        logger.info("Starting basic parameter validation for intake agent")

        try:
            # Parse the application data
            app_data = json.loads(application_data)

            # Track validation results
            validation_issues = []
            completeness_score = 0.0
            total_fields = 0
            completed_fields = 0

            # Required fields for basic validation
            required_fields = [
                "applicant_name",
                "applicant_id",
                "email",
                "phone",
                "date_of_birth",
                "loan_amount",
                "loan_purpose",
                "loan_term_months",
                "annual_income",
                "employment_status",
            ]

            # Check required fields
            for field in required_fields:
                total_fields += 1
                if field in app_data and app_data[field] is not None:
                    # Additional check for empty strings
                    if isinstance(app_data[field], str) and app_data[field].strip():
                        completed_fields += 1
                    elif not isinstance(app_data[field], str):
                        completed_fields += 1
                else:
                    validation_issues.append(f"Missing required field: {field}")

            # Optional but important fields for completeness scoring
            optional_fields = [
                "employer_name",
                "months_employed",
                "monthly_expenses",
                "existing_debt",
                "assets",
                "down_payment",
            ]

            for field in optional_fields:
                total_fields += 1
                if field in app_data and app_data[field] is not None:
                    if isinstance(app_data[field], str) and app_data[field].strip():
                        completed_fields += 1
                    elif not isinstance(app_data[field], str):
                        completed_fields += 1

            # Calculate completeness score
            completeness_score = completed_fields / total_fields if total_fields > 0 else 0.0

            # Basic format validation
            format_issues = []

            # Email format (basic check)
            if "email" in app_data and app_data["email"]:
                if "@" not in str(app_data["email"]) or "." not in str(app_data["email"]).split("@")[-1]:
                    format_issues.append("Invalid email format")

            # Loan amount should be positive
            if "loan_amount" in app_data and app_data["loan_amount"]:
                try:
                    amount = float(app_data["loan_amount"])
                    if amount <= 0:
                        format_issues.append("Loan amount must be greater than zero")
                except (ValueError, TypeError):
                    format_issues.append("Invalid loan amount format")

            # Annual income should be positive
            if "annual_income" in app_data and app_data["annual_income"]:
                try:
                    income = float(app_data["annual_income"])
                    if income < 0:
                        format_issues.append("Annual income cannot be negative")
                except (ValueError, TypeError):
                    format_issues.append("Invalid annual income format")

            # Determine validation status
            has_required_fields = len([issue for issue in validation_issues if "Missing required field" in issue]) == 0
            has_valid_formats = len(format_issues) == 0

            if has_required_fields and has_valid_formats:
                validation_status = "VALID"
            elif has_required_fields:
                validation_status = "WARNING"  # Format issues but complete
            else:
                validation_status = "INVALID"  # Missing required fields

            # Routing recommendation based on profile strength
            routing_recommendation = "STANDARD"  # Default

            if validation_status == "VALID" and completeness_score >= 0.85:
                # Check for VIP indicators
                annual_income = app_data.get("annual_income", 0)
                try:
                    if float(annual_income) >= 150000:
                        routing_recommendation = "FAST_TRACK"
                except (ValueError, TypeError):
                    pass
            elif validation_status == "INVALID" or completeness_score < 0.6:
                routing_recommendation = "ENHANCED"

            # Compile all issues
            all_issues = validation_issues + format_issues

            # Create response
            result = {
                "validation_status": validation_status,
                "completeness_score": round(completeness_score, 2),
                "routing_recommendation": routing_recommendation,
                "validation_results": {
                    "required_fields_complete": has_required_fields,
                    "format_validation_passed": has_valid_formats,
                    "completed_fields": completed_fields,
                    "total_fields": total_fields,
                },
                "issues": all_issues,
                "messages": [],
                "type": "basic_parameter_validation",
            }

            # Add success messages based on results
            if validation_status == "VALID":
                result["messages"].append("All required fields present and valid")
                if completeness_score >= 0.9:
                    result["messages"].append("Excellent profile completeness")
                elif completeness_score >= 0.75:
                    result["messages"].append("Good profile completeness")

            if routing_recommendation == "FAST_TRACK":
                result["messages"].append("Profile qualifies for fast-track processing")

            logger.info(
                f"Basic validation completed - Status: {validation_status}, "
                f"Completeness: {completeness_score:.2f}, Routing: {routing_recommendation}"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse application data: {e}")
            return {
                "validation_status": "ERROR",
                "completeness_score": 0.0,
                "routing_recommendation": "ENHANCED",
                "validation_results": {
                    "required_fields_complete": False,
                    "format_validation_passed": False,
                    "completed_fields": 0,
                    "total_fields": 0,
                },
                "issues": [f"Invalid JSON format: {str(e)}"],
                "messages": ["Unable to parse application data"],
                "type": "basic_parameter_validation",
            }

        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            return {
                "validation_status": "ERROR",
                "completeness_score": 0.0,
                "routing_recommendation": "ENHANCED",
                "validation_results": {
                    "required_fields_complete": False,
                    "format_validation_passed": False,
                    "completed_fields": 0,
                    "total_fields": 0,
                },
                "issues": [f"Validation error: {str(e)}"],
                "messages": ["Validation service encountered an error"],
                "type": "basic_parameter_validation",
            }
