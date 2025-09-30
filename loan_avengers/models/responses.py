"""
Structured response models for agent outputs.

These models define the expected output format for each agent in the loan processing
workflow, designed to be compatible with Agent Framework's response_format parameter.
"""

from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field


class IntakeAssessment(BaseModel):
    """
    Enhanced response from the Intake Agent (Application Validator).

    Combines technical validation data with personality-driven messaging
    for enhanced user experience. Personality details defined in persona file.
    """

    # Technical Processing Data (Core Functionality)
    validation_status: Literal["COMPLETE", "INCOMPLETE", "FAILED"] = Field(
        description="Status of application data validation"
    )

    routing_decision: Literal["FAST_TRACK", "STANDARD", "ENHANCED", "MANUAL"] = Field(
        description="Routing decision based on application profile"
    )

    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the routing decision (0.0 to 1.0)")

    data_quality_score: float = Field(ge=0.0, le=1.0, description="Overall data quality assessment (0.0 to 1.0)")

    processing_notes: str = Field(description="Technical processing notes")

    next_agent: str = Field(default="credit", description="Next agent in the workflow chain")

    # AI Dream Team Personality Layer (Revolutionary UX)
    specialist_name: str = Field(default="Intake Agent", description="AI specialist name for personalization")

    celebration_message: str = Field(description="Eagle-eyed validation message with efficient humor")

    encouragement_note: str = Field(description="Sharp-eyed assessment building confidence in data quality")

    next_step_preview: str = Field(description="Exciting preview of what's coming next")

    # UI Enhancement Triggers
    animation_type: Literal["sparkles", "confetti", "pulse", "glow"] = Field(
        default="pulse", description="Animation type for UI celebration"
    )

    celebration_level: Literal["mild", "moderate", "high", "maximum"] = Field(
        default="moderate", description="Intensity level for UI celebrations"
    )


class CreditAssessment(BaseModel):
    """
    Structured response from the Credit Agent.

    Provides credit analysis and risk scoring for the loan application.
    """

    credit_score_range: Literal["EXCELLENT", "GOOD", "FAIR", "POOR", "UNKNOWN"] = Field(
        description="Assessed credit score category"
    )

    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(description="Credit risk assessment level")

    recommended_rate: float = Field(ge=0.0, le=50.0, description="Recommended interest rate percentage")

    debt_to_income_ratio: float | None = Field(None, ge=0.0, le=10.0, description="Calculated debt-to-income ratio")

    identity_verified: bool = Field(description="Whether applicant identity has been verified")

    processing_notes: str = Field(description="Credit assessment notes and recommendations")

    next_agent: str = Field(default="income", description="Next agent in the workflow chain")


class IncomeAssessment(BaseModel):
    """
    Structured response from the Income Agent.

    Provides employment and income verification results.
    """

    employment_verified: bool = Field(description="Whether employment has been verified")

    income_stability: Literal["STABLE", "VARIABLE", "UNSTABLE", "UNKNOWN"] = Field(
        description="Assessment of income stability"
    )

    income_adequacy: Literal["ADEQUATE", "MARGINAL", "INSUFFICIENT"] = Field(
        description="Whether income is sufficient for requested loan"
    )

    verified_monthly_income: float | None = Field(None, ge=0.0, description="Verified monthly income amount")

    employment_duration_months: int | None = Field(None, ge=0, description="Duration of current employment in months")

    processing_notes: str = Field(description="Income verification notes and findings")

    next_agent: str = Field(default="risk", description="Next agent in the workflow chain")


class RiskAssessment(BaseModel):
    """
    Structured response from the Risk Agent.

    Provides comprehensive risk analysis and recommendations.
    """

    overall_risk: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        description="Overall risk assessment for the loan"
    )

    fraud_indicators: list[str] = Field(default_factory=list, description="List of potential fraud indicators found")

    risk_factors: list[str] = Field(default_factory=list, description="Identified risk factors for the application")

    mitigation_recommendations: list[str] = Field(
        default_factory=list, description="Recommended risk mitigation actions"
    )

    loan_recommendation: Literal["APPROVE", "CONDITIONAL", "DECLINE", "MANUAL_REVIEW"] = Field(
        description="Final loan recommendation"
    )

    processing_notes: str = Field(description="Risk analysis summary and rationale")

    next_agent: str = Field(default="orchestrator", description="Next agent in the workflow chain")


class LoanDecision(BaseModel):
    """
    Final structured response from the Orchestrator Agent.

    Provides the final loan decision with complete rationale.
    """

    decision: Literal["APPROVED", "CONDITIONALLY_APPROVED", "DECLINED", "MANUAL_REVIEW"] = Field(
        description="Final loan decision"
    )

    approved_amount: float | None = Field(None, ge=0.0, description="Approved loan amount (if approved)")

    interest_rate: float | None = Field(None, ge=0.0, le=50.0, description="Approved interest rate percentage")

    loan_term_months: int | None = Field(None, ge=1, le=360, description="Approved loan term in months")

    conditions: list[str] = Field(default_factory=list, description="Conditions that must be met for approval")

    decline_reasons: list[str] = Field(default_factory=list, description="Reasons for decline (if applicable)")

    processing_summary: str = Field(description="Summary of the entire processing workflow")

    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the final decision")


# Generic type for agent assessments
AssessmentType = TypeVar(
    "AssessmentType", IntakeAssessment, CreditAssessment, IncomeAssessment, RiskAssessment, LoanDecision
)


class UsageStats(BaseModel):
    """Token usage statistics from agent execution."""

    input_tokens: int | None = Field(None, description="Number of input tokens used")
    output_tokens: int | None = Field(None, description="Number of output tokens generated")
    total_tokens: int | None = Field(None, description="Total tokens used")


class AgentResponse(BaseModel, Generic[AssessmentType]):
    """
    Generic response wrapper for agent outputs.

    Type-safe wrapper that preserves the specific assessment type.
    Combines assessment data with metadata and usage statistics.

    Example:
        intake_response: AgentResponse[IntakeAssessment] = await intake_agent.process(...)
        credit_response: AgentResponse[CreditAssessment] = await credit_agent.process(...)

    Benefits:
        - Full IDE autocomplete for assessment-specific properties
        - Type checking at compile time
        - Self-documenting return types
    """

    assessment: AssessmentType = Field(description="The agent's assessment result")
    usage_stats: UsageStats = Field(description="Token usage statistics")
    response_id: str | None = Field(None, description="Unique response identifier")
    created_at: str | None = Field(None, description="Response timestamp")
    agent_name: str = Field(description="Name of the agent that produced this response")
    application_id: str = Field(description="Application identifier")


__all__ = [
    "IntakeAssessment",
    "CreditAssessment",
    "IncomeAssessment",
    "RiskAssessment",
    "LoanDecision",
    "UsageStats",
    "AgentResponse",
    "AssessmentType",
]
