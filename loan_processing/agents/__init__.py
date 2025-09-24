"""
Agent module for loan processing system using Microsoft Agent Framework.

This module provides the agent infrastructure following the architectural
patterns established in ADRs 002 and 005.
"""

from .base import (
    LoanProcessingAgent,
    AgentRegistry,
    AgentError,
    AgentTimeoutError,
    MCPServerError
)

from .registry import (
    AgentRegistryManager,
    initialize_global_registry,
    get_global_registry
)

__all__ = [
    # Base agent classes and exceptions
    "LoanProcessingAgent",
    "AgentRegistry",
    "AgentError",
    "AgentTimeoutError",
    "MCPServerError",

    # Registry management
    "AgentRegistryManager",
    "initialize_global_registry",
    "get_global_registry",
]
