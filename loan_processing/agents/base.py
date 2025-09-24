"""
Base agent class for loan processing using Microsoft Agent Framework.

This module provides the foundational agent architecture that all specialized
loan processing agents inherit from, implementing the patterns defined in ADR-002.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from loan_processing.models.application import LoanApplication
from loan_processing.models.assessment import BaseAssessment

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass


class AgentTimeoutError(AgentError):
    """Raised when agent operations timeout."""
    pass


class MCPServerError(AgentError):
    """Raised when MCP server operations fail."""
    pass


class LoanProcessingAgent(ABC):
    """
    Abstract base class for loan processing agents using Microsoft Agent Framework.

    This class implements the composition pattern from ADR-002, providing a consistent
    interface for all loan processing agents while abstracting framework specifics.

    Key Design Principles:
    - Separation of concerns: Business logic separate from framework
    - Consistent error handling and logging patterns
    - Development support with placeholder implementations
    - Type-safe assessment response parsing
    """

    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[str],
        mcp_servers: List[str] = None,
        timeout_seconds: int = 300
    ):
        """
        Initialize the loan processing agent.

        Args:
            name: Human-readable name for the agent
            description: Description of agent's purpose and capabilities
            capabilities: List of agent capabilities for documentation
            mcp_servers: List of MCP server names this agent can access
            timeout_seconds: Maximum execution time for agent operations
        """
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.mcp_servers = mcp_servers or []
        self.timeout_seconds = timeout_seconds
        self._agent_client = None  # Will be set by framework integration

        logger.info(f"Initialized agent {name} with capabilities: {capabilities}")

    @abstractmethod
    async def assess_application(
        self,
        application: LoanApplication,
        context: Optional[Dict[str, Any]] = None
    ) -> BaseAssessment:
        """
        Perform agent-specific assessment of the loan application.

        This method must be implemented by each specialized agent to perform
        their specific assessment logic using available MCP tools.

        Args:
            application: The loan application to assess
            context: Optional context from previous agents in workflow

        Returns:
            BaseAssessment: Agent-specific assessment results

        Raises:
            AgentError: If assessment cannot be completed
            AgentTimeoutError: If assessment times out
            MCPServerError: If MCP tool calls fail
        """
        pass

    async def initialize_tools(self) -> None:
        """
        Initialize MCP server connections and tools.

        This method sets up connections to the MCP servers specified
        in the agent configuration. Override for custom tool initialization.
        """
        logger.info(f"Initializing tools for agent {self.name}")
        for server_name in self.mcp_servers:
            logger.debug(f"Connecting to MCP server: {server_name}")
            # MCP server connections will be implemented with framework integration

    def validate_assessment_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate assessment result structure and completeness.

        Args:
            result: Raw assessment result dictionary

        Returns:
            bool: True if result is valid, False otherwise
        """
        required_fields = ["application_id", "assessment_type", "confidence_score"]
        return all(field in result for field in required_fields)

    def parse_assessment_response(
        self,
        raw_response: Dict[str, Any],
        application: LoanApplication
    ) -> BaseAssessment:
        """
        Parse raw agent response into typed assessment result.

        Args:
            raw_response: Raw response from agent execution
            application: Original loan application for reference

        Returns:
            BaseAssessment: Parsed and validated assessment result

        Raises:
            AgentError: If response cannot be parsed or is invalid
        """
        try:
            # Ensure required fields are present
            if not self.validate_assessment_result(raw_response):
                raise AgentError(f"Invalid assessment result from {self.name}")

            # Add standard fields if missing
            raw_response.setdefault("application_id", application.application_id)
            raw_response.setdefault("assessed_at", datetime.utcnow())
            raw_response.setdefault("assessed_by", self.name)

            # This will be overridden by specialized agents to return their specific types
            return BaseAssessment(**raw_response)

        except Exception as e:
            logger.error(f"Failed to parse assessment response from {self.name}: {e}")
            raise AgentError(f"Assessment parsing failed: {e}") from e

    async def handle_mcp_error(self, error: Exception, tool_name: str) -> Dict[str, Any]:
        """
        Handle MCP server errors with appropriate fallback behavior.

        Args:
            error: The exception that occurred
            tool_name: Name of the MCP tool that failed

        Returns:
            Dict containing error information and any fallback data
        """
        logger.error(f"MCP tool {tool_name} failed in {self.name}: {error}")
        return {
            "error": str(error),
            "tool_name": tool_name,
            "agent": self.name,
            "fallback_used": True,
            "confidence_impact": -0.2  # Reduce confidence when using fallbacks
        }

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information for monitoring and debugging.

        Returns:
            Dict containing agent metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "mcp_servers": self.mcp_servers,
            "timeout_seconds": self.timeout_seconds,
            "status": "initialized"
        }

    @property
    def assessment_type(self) -> str:
        """
        Get the assessment type this agent produces.

        This should be overridden by specialized agents to return
        their specific assessment type identifier.
        """
        return "base"


class AgentRegistry:
    """
    Central registry for creating and managing loan processing agents.

    Implements the registry pattern from ADR-005 for creating workflow-agnostic
    agents without hardcoded handoffs or circular dependencies.
    """

    _agent_configs: Dict[str, Dict[str, Any]] = {}
    _registered_agents: Dict[str, type] = {}

    @classmethod
    def register_agent_type(cls, agent_type: str, agent_class: type) -> None:
        """
        Register a specialized agent type with the registry.

        Args:
            agent_type: Identifier for the agent type (e.g., "credit", "income")
            agent_class: The agent class to register
        """
        cls._registered_agents[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")

    @classmethod
    def load_agent_configs(cls, config: Dict[str, Any]) -> None:
        """
        Load agent configurations from YAML or other config source.

        Args:
            config: Configuration dictionary containing agent definitions
        """
        cls._agent_configs = config.get("agents", {})
        logger.info(f"Loaded configurations for {len(cls._agent_configs)} agent types")

    @classmethod
    def create_agent(cls, agent_type: str, **kwargs) -> LoanProcessingAgent:
        """
        Create an agent instance of the specified type.

        Args:
            agent_type: Type of agent to create (e.g., "credit", "income")
            **kwargs: Additional parameters for agent creation

        Returns:
            LoanProcessingAgent: Configured agent instance

        Raises:
            AgentError: If agent type is not registered or configuration is invalid
        """
        if agent_type not in cls._registered_agents:
            raise AgentError(f"Unknown agent type: {agent_type}")

        if agent_type not in cls._agent_configs:
            raise AgentError(f"No configuration found for agent type: {agent_type}")

        agent_class = cls._registered_agents[agent_type]
        config = cls._agent_configs[agent_type].copy()

        # Merge in any provided kwargs
        config.update(kwargs)

        return agent_class(**config)

    @classmethod
    def get_available_agent_types(cls) -> List[str]:
        """Get list of available agent types."""
        return list(cls._registered_agents.keys())

    @classmethod
    def get_agent_info(cls, agent_type: str) -> Dict[str, Any]:
        """Get information about a specific agent type."""
        if agent_type not in cls._agent_configs:
            raise AgentError(f"Unknown agent type: {agent_type}")

        return cls._agent_configs[agent_type].copy()


__all__ = [
    "LoanProcessingAgent",
    "AgentRegistry",
    "AgentError",
    "AgentTimeoutError",
    "MCPServerError"
]