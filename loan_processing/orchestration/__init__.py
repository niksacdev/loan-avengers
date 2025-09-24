"""
Orchestration module for multi-agent loan processing workflows.

This module implements the configuration-driven orchestration architecture
from ADR-005, supporting dynamic pattern execution without hardcoded dependencies.
"""

from .engine import (
    OrchestrationEngine,
    OrchestrationContext,
    WorkflowPattern,
    PatternType,
    AgentExecutionStatus
)

__all__ = [
    "OrchestrationEngine",
    "OrchestrationContext",
    "WorkflowPattern",
    "PatternType",
    "AgentExecutionStatus"
]