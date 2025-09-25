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

        # Agent Framework logger requires 'agent_framework' prefix (verified requirement)
        # Direct testing shows: get_logger('test') raises "Logger name must start with 'agent_framework'"
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


__all__ = ["Observability"]
