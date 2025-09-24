"""
Agent registry implementation for dynamic agent creation and management.

This module implements the registry pattern from ADR-005 to create workflow-agnostic
agents without hardcoded dependencies or circular imports.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import yaml

from loan_processing.agents.base import AgentRegistry as BaseRegistry, LoanProcessingAgent
from loan_processing.models.application import LoanApplication

logger = logging.getLogger(__name__)


class AgentRegistryManager:
    """
    Extended agent registry with configuration loading and management capabilities.

    This class extends the base registry functionality with configuration management,
    MCP server factory integration, and structured output format generation.
    """

    def __init__(self):
        """Initialize the registry manager."""
        self._mcp_server_factory = None
        self._config_loaded = False
        self._agent_personas = {}

    async def initialize(self, config_file: Optional[str] = None) -> None:
        """
        Initialize the agent registry with configuration.

        Args:
            config_file: Path to YAML configuration file
        """
        if config_file:
            await self.load_configuration_from_file(config_file)

        # Initialize MCP server factory
        await self._initialize_mcp_factory()

        logger.info("Agent registry manager initialized successfully")

    async def load_configuration_from_file(self, config_file: str) -> None:
        """
        Load agent configurations from YAML file.

        Args:
            config_file: Path to the configuration YAML file
        """
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)

            BaseRegistry.load_agent_configs(config)
            self._config_loaded = True

            logger.info(f"Loaded agent configuration from {config_file}")

        except Exception as e:
            logger.error(f"Failed to load configuration from {config_file}: {e}")
            raise

    async def _initialize_mcp_factory(self) -> None:
        """Initialize MCP server factory for agent tool management."""
        # MCP server factory implementation will be added with framework integration
        logger.debug("MCP server factory initialization placeholder")

    def register_specialized_agents(self) -> None:
        """
        Register all specialized agent types with the base registry.

        This method will be called to register concrete agent implementations
        once they are created.
        """
        # Import and register specialized agents
        # This will be implemented when specialized agents are created
        logger.info("Specialized agent registration placeholder")

    async def create_agent_with_tools(
        self,
        agent_type: str,
        **kwargs
    ) -> LoanProcessingAgent:
        """
        Create an agent instance with initialized MCP tools.

        Args:
            agent_type: Type of agent to create
            **kwargs: Additional agent configuration parameters

        Returns:
            LoanProcessingAgent: Fully configured agent with tools

        Raises:
            AgentError: If agent creation or tool initialization fails
        """
        # Create the agent using base registry
        agent = BaseRegistry.create_agent(agent_type, **kwargs)

        # Initialize tools if MCP servers are configured
        if agent.mcp_servers:
            await agent.initialize_tools()

        logger.info(f"Created agent {agent_type} with tools: {agent.mcp_servers}")
        return agent

    def get_agent_capabilities(self, agent_type: str) -> List[str]:
        """
        Get the capabilities list for a specific agent type.

        Args:
            agent_type: The agent type to query

        Returns:
            List of capability strings
        """
        agent_info = BaseRegistry.get_agent_info(agent_type)
        return agent_info.get("capabilities", [])

    def get_mcp_servers_for_agent(self, agent_type: str) -> List[str]:
        """
        Get the MCP servers configured for a specific agent type.

        Args:
            agent_type: The agent type to query

        Returns:
            List of MCP server names
        """
        agent_info = BaseRegistry.get_agent_info(agent_type)
        return agent_info.get("mcp_servers", [])

    def generate_structured_output_instructions(self, agent_type: str) -> str:
        """
        Generate structured output format instructions for an agent.

        Args:
            agent_type: The agent type to generate instructions for

        Returns:
            String containing structured output format instructions
        """
        try:
            agent_info = BaseRegistry.get_agent_info(agent_type)
            output_format = agent_info.get("output_format", {})

            if not output_format:
                return "Return results in a clear, structured format."

            instructions = ["Return your assessment in the following JSON structure:"]
            instructions.append("```json")
            instructions.append("{")

            for field_name, field_spec in output_format.items():
                field_type = field_spec.get("type", "string")
                description = field_spec.get("description", "")

                # Add field with type and description
                if field_type == "enum":
                    values = field_spec.get("values", [])
                    instructions.append(f'  "{field_name}": "{values[0] if values else "value"}", // {description} (options: {values})')
                elif field_type == "array":
                    item_type = field_spec.get("item_type", "string")
                    instructions.append(f'  "{field_name}": ["{item_type}_value"], // {description}')
                else:
                    example_value = self._get_example_value_for_type(field_type)
                    instructions.append(f'  "{field_name}": {example_value}, // {description}')

            instructions.append("}")
            instructions.append("```")

            return "\n".join(instructions)

        except Exception as e:
            logger.error(f"Failed to generate output instructions for {agent_type}: {e}")
            return "Return results in a clear, structured format."

    def _get_example_value_for_type(self, field_type: str) -> str:
        """Get an example value for a field type."""
        type_examples = {
            "string": '"example_value"',
            "integer": "123",
            "float": "0.85",
            "boolean": "true",
            "decimal": "10000.00"
        }
        return type_examples.get(field_type, '"value"')

    async def validate_agent_configuration(self, agent_type: str) -> bool:
        """
        Validate that an agent configuration is complete and valid.

        Args:
            agent_type: The agent type to validate

        Returns:
            bool: True if configuration is valid
        """
        try:
            agent_info = BaseRegistry.get_agent_info(agent_type)

            # Check required fields
            required_fields = ["name", "description", "capabilities"]
            for field in required_fields:
                if field not in agent_info:
                    logger.error(f"Agent {agent_type} missing required field: {field}")
                    return False

            # Validate MCP server references
            mcp_servers = agent_info.get("mcp_servers", [])
            # TODO: Validate MCP servers exist and are available

            logger.debug(f"Agent configuration for {agent_type} is valid")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed for {agent_type}: {e}")
            return False

    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get current status of the agent registry.

        Returns:
            Dict containing registry status information
        """
        return {
            "config_loaded": self._config_loaded,
            "available_agents": BaseRegistry.get_available_agent_types(),
            "total_agents": len(BaseRegistry.get_available_agent_types()),
            "mcp_factory_initialized": self._mcp_server_factory is not None
        }


# Global registry instance
_global_registry_manager = AgentRegistryManager()


async def initialize_global_registry(config_file: Optional[str] = None) -> None:
    """Initialize the global agent registry manager."""
    await _global_registry_manager.initialize(config_file)


def get_global_registry() -> AgentRegistryManager:
    """Get the global agent registry manager instance."""
    return _global_registry_manager


__all__ = [
    "AgentRegistryManager",
    "initialize_global_registry",
    "get_global_registry"
]