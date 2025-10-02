"""
Loan Processing System - Business Logic Foundation

A simplified loan processing system that provides core business logic,
data models, and agent personas for integration with Microsoft Agent Framework.

Key Components:
- Business data models with Pydantic validation
- MCP server implementations for external tool integration
- Agent persona definitions for specialized loan processing tasks
- Business service interfaces for financial calculations and verification

This foundation can be used with any agent framework, particularly
Microsoft Agent Framework with ChatClientAgent patterns.

Usage:
    from loan_defenders.models import LoanApplication, LoanDecision
    from loan_defenders.agents import get_persona_path

    # Load agent persona for framework integration
    persona_path = get_persona_path("credit")

    # Create loan application with business validation
    application = LoanApplication(
        application_id="LN1234567890",
        applicant_name="Sample Applicant",
        # ... other fields
    )

Architecture:
- models/: Core business data models (LoanApplication, Assessment, Decision)
- tools/: MCP servers and business service interfaces
- agents/: Agent persona definitions (markdown files)
- config/: Configuration files for agents and MCP servers
- utils/: Shared utilities for configuration and logging

Agent Personas:
- intake: Data completeness and routing
- credit: Credit risk assessment
- income: Income and employment verification
- risk: Final decision synthesis
- orchestrator: Workflow coordination

The system is designed to preserve all business logic while being
framework-agnostic for easy integration with any agent system.
"""

from loan_defenders.models.application import LoanApplication
from loan_defenders.models.assessment import ComprehensiveAssessment
from loan_defenders.models.decision import LoanDecision

# Export core models
__all__ = [
    # Core business models
    "LoanApplication",
    "ComprehensiveAssessment",
    "LoanDecision",
]

__version__ = "2.0.0"
