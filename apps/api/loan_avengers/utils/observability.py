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
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from agent_framework.observability import setup_observability


class JsonExtraFormatter(logging.Formatter):
    """
    Custom formatter that includes extra data as JSON in log output.

    Standard formatter only outputs: asctime, name, levelname, message
    This formatter appends extra data as JSON for debugging and observability.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with extra data as JSON."""
        import json

        # Format base message using standard formatter
        base_message = super().format(record)

        # Extract extra fields (everything not in standard LogRecord attributes)
        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "exc_info",
            "exc_text",
            "stack_info",
            "asctime",
        }

        extra_data = {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_attrs and not key.startswith("_")
        }

        # If there's extra data, append it as JSON
        if extra_data:
            try:
                extra_json = json.dumps(extra_data, default=str, indent=None)
                return f"{base_message} | extra={extra_json}"
            except (TypeError, ValueError) as e:
                # If JSON serialization fails, append raw representation
                return f"{base_message} | extra={extra_data} [serialization_error: {e}]"

        return base_message


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

        # Setup log directory and file
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create log filename with timestamp
        log_filename = log_dir / f"loan_avengers_{datetime.now().strftime('%Y%m%d')}.log"

        # Configure formatters with extra data support
        formatter = JsonExtraFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level))

        # Remove existing handlers
        root_logger.handlers.clear()

        # Add console handler (stdout)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Add file handler with rotation (10MB per file, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Log to file and stdio
        logging.info(f"Logging to file: {log_filename}")
        logging.info(f"Log level: {log_level}")

        # Initialize Agent Framework observability if Application Insights is configured
        if app_insights_connection_string:
            setup_observability(
                applicationinsights_connection_string=app_insights_connection_string,
                enable_sensitive_data=enable_sensitive_data,
            )
            logging.info("Observability initialized with Application Insights and OpenTelemetry")
        else:
            logging.info("Application Insights not configured - using stdio and file logging only")

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

        # Use loan_avengers prefix to distinguish our application logs
        # from agent_framework's internal logs in Application Insights
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
                        logging.debug("Failed to parse content for tool calls: %s", e)
                        continue

        except (AttributeError, TypeError) as e:
            # Log response parsing issues but don't fail
            logging.debug("Failed to extract tool calls from response: %s", e)

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

    @staticmethod
    def mask_pii(value: str | None, field_type: str = "name") -> str:
        """
        Mask personally identifiable information (PII) for secure logging.

        Implements privacy-preserving masking for different PII types:
        - Names: Shows first letter + last initial (e.g., "J*** D***")
        - Emails: Shows first 2 chars + domain (e.g., "jo***@example.com")
        - Generic: Shows first 3 chars (e.g., "abc***")

        Args:
            value: The PII value to mask
            field_type: Type of PII - "name", "email", or "generic" (default: "name")

        Returns:
            str: Masked value with sensitive portions replaced by ***

        Examples:
            >>> Observability.mask_pii("John Doe", "name")
            "J*** D***"
            >>> Observability.mask_pii("john.doe@example.com", "email")
            "jo***@example.com"
            >>> Observability.mask_pii("sensitive-data", "generic")
            "sen***"
        """
        if not value:
            return "***"

        if field_type == "name":
            # Split name into parts
            parts = value.strip().split()
            if len(parts) == 0:
                return "***"
            elif len(parts) == 1:
                # Single name: show first letter
                return f"{parts[0][0]}***" if parts[0] else "***"
            else:
                # Multiple parts: show first letter of each part
                masked_parts = [f"{part[0]}***" if part else "***" for part in parts]
                return " ".join(masked_parts)

        elif field_type == "email":
            # Email: show first 2 chars + domain
            if "@" in value:
                local, domain = value.rsplit("@", 1)
                masked_local = f"{local[:2]}***" if len(local) >= 2 else "***"
                return f"{masked_local}@{domain}"
            else:
                return f"{value[:2]}***" if len(value) >= 2 else "***"

        else:  # generic
            # Generic: show first 3 characters
            return f"{value[:3]}***" if len(value) >= 3 else "***"

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
            "Token usage: %s (%d tokens)",
            agent_name,
            total_tokens,
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


__all__ = ["Observability", "JsonExtraFormatter"]
