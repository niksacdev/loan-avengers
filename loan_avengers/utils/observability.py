"""
Centralized observability configuration for loan processing agents.

Simple setup for stdio logging and optional Application Insights integration
using Microsoft Agent Framework's built-in observability capabilities.
"""

from __future__ import annotations

import logging
import os

from agent_framework import get_logger
from agent_framework.observability import setup_observability


class Observability:
    """Simple observability configuration for all agents."""

    _initialized = False

    @classmethod
    def initialize(cls, force_reinit: bool = False) -> None:
        """
        Initialize observability for the application.

        Args:
            force_reinit: Force reinitialization even if already initialized
        """
        if cls._initialized and not force_reinit:
            return

        # Get configuration from environment
        app_insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        enable_sensitive_data = os.getenv("ENABLE_SENSITIVE_DATA", "false").lower() == "true"
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Configure basic Python logging first
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            force=True,  # Override any existing configuration
        )

        # Initialize Agent Framework observability if Application Insights is configured
        if app_insights_connection_string:
            setup_observability(
                applicationinsights_connection_string=app_insights_connection_string,
                enable_sensitive_data=enable_sensitive_data,
                enable_live_metrics=True,  # Enable live metrics for real-time monitoring
            )
            logging.info("Agent Framework observability initialized with Application Insights")
        else:
            logging.info("Agent Framework observability using stdio logging only")

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger for an agent, ensuring observability is initialized.

        Args:
            name: Logger name (typically agent name)

        Returns:
            Logger instance with proper observability configuration
        """
        # Ensure observability is initialized
        cls.initialize()

        # Agent Framework REQUIRES 'agent_framework' prefix (unit test verified)
        # See test_logger_requirements.py - get_logger('test') raises "Logger name must start with 'agent_framework'"
        # PR reviewer suggestion to remove prefix is INCORRECT
        framework_logger_name = f"agent_framework.{name}"
        return get_logger(framework_logger_name)

    @classmethod
    def is_application_insights_enabled(cls) -> bool:
        """Check if Application Insights is enabled."""
        return bool(os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))

    @classmethod
    def get_log_level(cls) -> str:
        """Get the configured log level."""
        return os.getenv("LOG_LEVEL", "INFO").upper()

    @staticmethod
    def extract_tool_calls_from_response(response_messages) -> list[str]:
        """
        Extract tool call names from agent response messages.

        Safely traverses the complex nested structure with proper error handling.
        Replaces fragile list comprehension with clear, maintainable logic.

        Args:
            response_messages: List of messages from AgentRunResponse

        Returns:
            List of tool names that were called

        Example:
            tool_calls = Observability.extract_tool_calls_from_response(response.messages)
        """
        tool_calls = []

        try:
            for msg in response_messages:
                if not hasattr(msg, "contents"):
                    continue

                for content in msg.contents:
                    try:
                        # Check if this is a function call content
                        content_type = getattr(content, "type", None)
                        if content_type is None:
                            continue

                        # Check for function call indicators
                        type_str = str(content_type).lower()
                        if "function" in type_str:
                            # Extract function name safely
                            tool_name = getattr(content, "name", "unknown")
                            tool_calls.append(tool_name)

                    except (AttributeError, TypeError) as e:
                        # Log parsing issues at debug level but don't fail
                        logging.debug(f"Failed to parse content for tool calls: {e}")
                        continue

        except (AttributeError, TypeError) as e:
            # Log response parsing issues but don't fail
            logging.debug(f"Failed to extract tool calls from response: {e}")

        return tool_calls


__all__ = ["Observability"]
