"""
Multi-Agent Loan Processing System using Microsoft Agent Framework.

A comprehensive loan processing system that implements autonomous agents
for credit assessment, income verification, and risk evaluation using
the Microsoft Agent Framework.

Key Features:
- Multi-agent architecture for specialized loan processing tasks
- Microsoft Agent Framework integration with ChatClientAgent patterns
- MCP (Model Context Protocol) server integration for external data
- Configuration-driven orchestration without hardcoded dependencies
- Production-ready error handling and audit trails
- Comprehensive business data models with validation

Architectural Principles:
- Multi-agent strategic foundation for progressive autonomy
- Configuration-driven orchestration (ADR-005)
- Clean separation between business logic and framework code
- Agent base architecture with framework composition (ADR-002)
- Layered configuration system with dependency injection (ADR-007)

Usage:
    from loan_processing.agents import initialize_global_registry, get_global_registry
    from loan_processing.orchestration import OrchestrationEngine
    from loan_processing.models import LoanApplication

    # Initialize agent registry
    await initialize_global_registry("config/agents.yaml")

    # Create orchestration engine
    engine = OrchestrationEngine()
    await engine.load_patterns_from_directory("config/patterns/")

    # Process loan application
    decision = await engine.execute_pattern("sequential", application)

Agent Types:
- Intake Agent: Data completeness and routing decisions
- Credit Agent: Credit risk assessment and scoring
- Income Agent: Income and employment verification
- Risk Agent: Final decision synthesis and recommendations

Orchestration Patterns:
- Sequential: Agents execute in order with context passing
- Parallel: Agents execute simultaneously with result merging
- Collaborative: Agent-to-agent communication (future enhancement)

Architecture Layers:
- Agent Layer: Specialized agent implementations
- Orchestration Layer: Pattern-based workflow execution
- Business Layer: Domain models and services (preserved from v1)
- Tool Layer: MCP servers for external integrations
- Configuration Layer: YAML-based settings and patterns

Development:
- Framework-agnostic agent base classes
- Placeholder implementations for development
- Comprehensive test coverage planned
- Hot reloading of configurations and patterns

For more information see:
- ARCHITECTURE.md: Consolidated architecture documentation
- ADR documents: Detailed architectural decisions
"""

from loan_processing.models.application import LoanApplication
from loan_processing.models.assessment import ComprehensiveAssessment
from loan_processing.models.decision import LoanDecision

# Export core models
__all__ = [
    # Core business models
    "LoanApplication",
    "ComprehensiveAssessment",
    "LoanDecision",
]

__version__ = "2.0.0"
