"""
Centralized observability configuration for loan processing agents.

Simple setup for stdio logging and optional Application Insights integration
using Microsoft Agent Framework's built-in observability capabilities.

Now enhanced with:
- OpenTelemetry distributed tracing via Azure Monitor
- Correlation ID tracking across requests
- Token usage tracking for cost management
"""

from __future__ import annotations

import logging
import os
import uuid
from contextvars import ContextVar

try:
    from agent_framework import get_logger
    from agent_framework.observability import setup_observability

    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    # Fallback to standard logging when agent_framework is not available
    AGENT_FRAMEWORK_AVAILABLE = False


class Observability:
    """
    Centralized observability configuration for all agents.

    Features:
    - Agent Framework observability (setup_observability)
    - OpenTelemetry distributed tracing (via Azure Monitor)
    - Correlation ID tracking for request tracing
    - Token usage tracking for cost management
    """

    _initialized = False

    # Context-local storage for correlation ID (thread-safe for async)
    _correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

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

        # Initialize Agent Framework observability if enabled and available
        enable_otel = os.getenv("ENABLE_OTEL", "false").lower() == "true"

        if AGENT_FRAMEWORK_AVAILABLE and enable_otel and app_insights_connection_string:
            setup_observability(
                applicationinsights_connection_string=app_insights_connection_string,
                enable_sensitive_data=enable_sensitive_data,
                enable_live_metrics=True,  # Enable live metrics for real-time monitoring
            )
            logging.info("Observability initialized with Application Insights and OpenTelemetry")
        elif AGENT_FRAMEWORK_AVAILABLE and enable_otel:
            logging.warning("ENABLE_OTEL=true but APPLICATIONINSIGHTS_CONNECTION_STRING not set - using basic logging")
        elif AGENT_FRAMEWORK_AVAILABLE:
            logging.debug("OpenTelemetry disabled (ENABLE_OTEL not set) - using basic logging")
        else:
            logging.debug("agent_framework not available - using standard Python logging")

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

        if AGENT_FRAMEWORK_AVAILABLE:
            # Agent Framework REQUIRES 'agent_framework' prefix (unit test verified)
            # See test_logger_requirements.py - get_logger('test') raises error:
            # "Logger name must start with 'agent_framework'"
            # PR reviewer suggestion to remove prefix is INCORRECT
            framework_logger_name = f"agent_framework.{name}"
            return get_logger(framework_logger_name)
        else:
            # Fallback to standard logging when agent framework is not available
            logger_name = f"loan_avengers.{name}"
            return logging.getLogger(logger_name)

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

    @staticmethod
    def mask_application_id(app_id: str) -> str:
        """
        Mask application ID for secure logging.

        Shows first 8 characters followed by *** to preserve some context
        while protecting full identifiers in logs.

        Args:
            app_id: The application ID to mask

        Returns:
            str: Masked application ID in format "XXXXXXXX***"

        Examples:
            >>> Observability.mask_application_id("LN1234567890ABCD")
            "LN123456***"
        """
        if not app_id or len(app_id) <= 8:
            return f"{app_id}***" if app_id else "***"
        return f"{app_id[:8]}***"

    @classmethod
    def set_correlation_id(cls, correlation_id: str | None = None) -> str:
        """
        Set correlation ID for current request context.

        Correlation IDs enable end-to-end request tracing across services
        and agent executions. They're automatically propagated through logs
        and OpenTelemetry traces.

        Args:
            correlation_id: Optional correlation ID. If None, generates a new UUID.

        Returns:
            str: The correlation ID that was set

        Example:
            >>> correlation_id = Observability.set_correlation_id()
            >>> logger.info("Processing", extra={"correlation_id": Observability.get_correlation_id()})
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        cls._correlation_id_var.set(correlation_id)
        return correlation_id

    @classmethod
    def get_correlation_id(cls) -> str:
        """
        Get correlation ID for current request context.

        If no correlation ID has been set, generates and sets a new one.

        Returns:
            str: Current correlation ID

        Example:
            >>> logger.info("Processing", extra={"correlation_id": Observability.get_correlation_id()})
        """
        correlation_id = cls._correlation_id_var.get()
        if not correlation_id:
            correlation_id = cls.set_correlation_id()
        return correlation_id

    @classmethod
    def clear_correlation_id(cls) -> None:
        """Clear correlation ID from current context."""
        cls._correlation_id_var.set("")

    @staticmethod
    def log_token_usage(
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        model: str | None = None,
        application_id: str | None = None,
    ) -> None:
        """
        Log token usage for cost tracking and analysis.

        Token usage is logged with structured fields for easy querying
        in Azure Application Insights using KQL.

        Args:
            agent_name: Name of the agent that used tokens
            input_tokens: Number of input tokens consumed
            output_tokens: Number of output tokens generated
            model: Optional model name/deployment
            application_id: Optional application ID for correlation

        Example:
            >>> Observability.log_token_usage(
            ...     agent_name="Credit_Assessor",
            ...     input_tokens=150,
            ...     output_tokens=75,
            ...     model="gpt-4",
            ...     application_id="LN1234567890"
            ... )

        Query in Azure Application Insights (KQL):
            ```kql
            traces
            | where customDimensions.event_type == "token_usage"
            | summarize
                total_tokens = sum(toint(customDimensions.total_tokens)),
                total_cost_estimate = sum(toint(customDimensions.total_tokens)) * 0.00001
                by tostring(customDimensions.agent_name)
            ```
        """
        logger = logging.getLogger("agent_framework.observability.token_usage")

        total_tokens = input_tokens + output_tokens

        logger.info(
            f"Token usage: {agent_name} ({total_tokens} tokens)",
            extra={
                "event_type": "token_usage",
                "agent_name": agent_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "model": model or "unknown",
                "application_id": Observability.mask_application_id(application_id) if application_id else None,
                "correlation_id": Observability.get_correlation_id(),
            },
        )


__all__ = ["Observability"]
