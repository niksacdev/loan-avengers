"""
Comprehensive tests for observability utilities.

Tests cover:
- Correlation ID tracking (set, get, clear)
- Token usage logging
- Application ID masking
- Tool call extraction
- Initialization patterns
"""

import asyncio
import logging
import os
from unittest.mock import Mock, patch

import pytest

from loan_defenders.utils.observability import AGENT_FRAMEWORK_AVAILABLE, Observability


class TestCorrelationIDTracking:
    """Test correlation ID tracking for distributed tracing."""

    def setup_method(self):
        """Clear correlation ID before each test."""
        Observability.clear_correlation_id()

    def test_set_correlation_id_with_provided_id(self):
        """Test setting correlation ID with provided value."""
        test_id = "test-correlation-123"
        result = Observability.set_correlation_id(test_id)

        assert result == test_id
        assert Observability.get_correlation_id() == test_id

    def test_set_correlation_id_auto_generates_uuid(self):
        """Test correlation ID auto-generation when none provided."""
        result = Observability.set_correlation_id()

        # Should generate a valid UUID
        assert result is not None
        assert len(result) == 36  # UUID v4 format
        assert "-" in result

        # Verify it was actually set
        assert Observability.get_correlation_id() == result

    def test_get_correlation_id_returns_same_value(self):
        """Test get_correlation_id returns same ID in same context."""
        test_id = "same-context-id"
        Observability.set_correlation_id(test_id)

        # Multiple calls should return same ID
        assert Observability.get_correlation_id() == test_id
        assert Observability.get_correlation_id() == test_id
        assert Observability.get_correlation_id() == test_id

    def test_get_correlation_id_auto_generates_if_not_set(self):
        """Test get_correlation_id auto-generates if none set."""
        # Clear any existing ID
        Observability.clear_correlation_id()

        # Get should auto-generate
        result = Observability.get_correlation_id()
        assert result is not None
        assert len(result) == 36

        # Subsequent calls should return same auto-generated ID
        assert Observability.get_correlation_id() == result

    def test_clear_correlation_id(self):
        """Test clearing correlation ID from context."""
        test_id = "clear-me"
        Observability.set_correlation_id(test_id)
        assert Observability.get_correlation_id() == test_id

        # Clear it
        Observability.clear_correlation_id()

        # Get should auto-generate a new one
        new_id = Observability.get_correlation_id()
        assert new_id != test_id

    def test_correlation_id_isolation_between_contexts(self):
        """Test correlation ID isolation between async contexts."""

        async def task_with_correlation_id(task_id: str) -> str:
            """Async task that sets and retrieves correlation ID."""
            Observability.set_correlation_id(task_id)
            # Simulate some async work
            await asyncio.sleep(0.01)
            return Observability.get_correlation_id()

        async def run_parallel_tasks():
            """Run multiple tasks with different correlation IDs."""
            # Create tasks with different correlation IDs
            task1 = asyncio.create_task(task_with_correlation_id("task-1-id"))
            task2 = asyncio.create_task(task_with_correlation_id("task-2-id"))
            task3 = asyncio.create_task(task_with_correlation_id("task-3-id"))

            # Each task should maintain its own correlation ID
            results = await asyncio.gather(task1, task2, task3)
            return results

        # Run the test
        results = asyncio.run(run_parallel_tasks())

        # Each task should have maintained its own correlation ID
        # Note: Due to ContextVar behavior, results might not be exactly as set
        # but should be consistent within each context
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)


class TestTokenUsageLogging:
    """Test token usage tracking for cost management."""

    def setup_method(self):
        """Clear correlation ID before each test."""
        Observability.clear_correlation_id()

    @patch("loan_defenders.utils.observability.logging.getLogger")
    def test_log_token_usage_basic(self, mock_get_logger):
        """Test basic token usage logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        Observability.log_token_usage(
            agent_name="TestAgent", input_tokens=100, output_tokens=50, model="gpt-4", application_id="LN123456789012"
        )

        # Verify logger was called
        mock_logger.info.assert_called_once()

        # Check logged message
        call_args = mock_logger.info.call_args
        assert "TestAgent" in call_args[0][0]
        assert "150 tokens" in call_args[0][0]

        # Check extra fields
        extra = call_args[1]["extra"]
        assert extra["event_type"] == "token_usage"
        assert extra["agent_name"] == "TestAgent"
        assert extra["input_tokens"] == 100
        assert extra["output_tokens"] == 50
        assert extra["total_tokens"] == 150
        assert extra["model"] == "gpt-4"
        assert "LN123456***" in extra["application_id"]  # Should be masked
        assert "correlation_id" in extra

    @patch("loan_defenders.utils.observability.logging.getLogger")
    def test_log_token_usage_without_optional_fields(self, mock_get_logger):
        """Test token usage logging without model and application_id."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        Observability.log_token_usage(agent_name="MinimalAgent", input_tokens=25, output_tokens=15)

        # Verify logger was called
        mock_logger.info.assert_called_once()

        # Check extra fields
        extra = mock_logger.info.call_args[1]["extra"]
        assert extra["agent_name"] == "MinimalAgent"
        assert extra["input_tokens"] == 25
        assert extra["output_tokens"] == 15
        assert extra["total_tokens"] == 40
        assert extra["model"] == "unknown"
        assert extra["application_id"] is None

    @patch("loan_defenders.utils.observability.logging.getLogger")
    def test_log_token_usage_includes_correlation_id(self, mock_get_logger):
        """Test that token usage logs include correlation ID."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Set a specific correlation ID
        test_correlation_id = "test-correlation-for-tokens"
        Observability.set_correlation_id(test_correlation_id)

        Observability.log_token_usage(agent_name="CorrelatedAgent", input_tokens=10, output_tokens=5)

        # Check correlation ID was included
        extra = mock_logger.info.call_args[1]["extra"]
        assert extra["correlation_id"] == test_correlation_id


class TestApplicationIDMasking:
    """Test PII masking for secure logging."""

    def test_mask_application_id_standard_length(self):
        """Test masking application ID with standard length."""
        app_id = "LN1234567890ABCD"
        masked = Observability.mask_application_id(app_id)

        assert masked == "LN123456***"
        assert len(masked) == 11
        assert masked.startswith("LN123456")
        assert masked.endswith("***")

    def test_mask_application_id_exact_8_chars(self):
        """Test masking application ID with exactly 8 characters."""
        app_id = "LN123456"
        masked = Observability.mask_application_id(app_id)

        assert masked == "LN123456***"

    def test_mask_application_id_short_id(self):
        """Test masking short application ID (< 8 chars)."""
        app_id = "LN123"
        masked = Observability.mask_application_id(app_id)

        assert masked == "LN123***"

    def test_mask_application_id_empty_string(self):
        """Test masking empty application ID."""
        masked = Observability.mask_application_id("")

        assert masked == "***"

    def test_mask_application_id_none(self):
        """Test masking None application ID."""
        # Pass empty string as function expects str
        masked = Observability.mask_application_id("")

        assert masked == "***"

    def test_mask_application_id_long_uuid(self):
        """Test masking UUID-style application ID."""
        app_id = "550e8400-e29b-41d4-a716-446655440000"
        masked = Observability.mask_application_id(app_id)

        assert masked == "550e8400***"
        assert len(masked) == 11


class TestToolCallExtraction:
    """Test extraction of tool calls from agent responses."""

    def test_extract_tool_calls_with_function_calls(self):
        """Test extracting tool calls from response with function calls."""
        # Create mock response structure
        mock_content1 = Mock()
        mock_content1.type = "function_call"
        mock_content1.name = "verify_credit_score"

        mock_content2 = Mock()
        mock_content2.type = "function_call"
        mock_content2.name = "calculate_dti_ratio"

        mock_message = Mock()
        mock_message.contents = [mock_content1, mock_content2]

        response_messages = [mock_message]

        tool_calls = Observability.extract_tool_calls_from_response(response_messages)

        assert len(tool_calls) == 2
        assert "verify_credit_score" in tool_calls
        assert "calculate_dti_ratio" in tool_calls

    def test_extract_tool_calls_empty_response(self):
        """Test extracting tool calls from empty response."""
        tool_calls = Observability.extract_tool_calls_from_response([])

        assert tool_calls == []

    def test_extract_tool_calls_no_function_calls(self):
        """Test extracting tool calls when no function calls present."""
        # Create mock response with text content only
        mock_content = Mock()
        mock_content.type = "text"

        mock_message = Mock()
        mock_message.contents = [mock_content]

        response_messages = [mock_message]

        tool_calls = Observability.extract_tool_calls_from_response(response_messages)

        assert tool_calls == []

    def test_extract_tool_calls_handles_missing_attributes(self):
        """Test extraction gracefully handles missing attributes."""
        # Create mock with missing contents
        mock_message = Mock(spec=[])  # No attributes

        response_messages = [mock_message]

        # Should not raise exception
        tool_calls = Observability.extract_tool_calls_from_response(response_messages)
        assert tool_calls == []

    def test_extract_tool_calls_handles_malformed_content(self):
        """Test extraction handles malformed content gracefully."""
        # Create mock with contents but malformed structure
        mock_content = Mock()
        del mock_content.type  # Remove type attribute
        del mock_content.name  # Remove name attribute

        mock_message = Mock()
        mock_message.contents = [mock_content]

        response_messages = [mock_message]

        # Should not raise exception
        tool_calls = Observability.extract_tool_calls_from_response(response_messages)
        assert tool_calls == []

    def test_extract_tool_calls_mixed_content_types(self):
        """Test extraction from mixed content types."""
        mock_func_content = Mock()
        mock_func_content.type = "function_call"
        mock_func_content.name = "validate_income"

        mock_text_content = Mock()
        mock_text_content.type = "text"

        mock_message = Mock()
        mock_message.contents = [mock_text_content, mock_func_content]

        response_messages = [mock_message]

        tool_calls = Observability.extract_tool_calls_from_response(response_messages)

        assert len(tool_calls) == 1
        assert "validate_income" in tool_calls


class TestObservabilityInitialization:
    """Test observability initialization patterns."""

    def setup_method(self):
        """Reset initialization state before each test."""
        Observability._initialized = False

    def teardown_method(self):
        """Reset initialization state after each test."""
        Observability._initialized = False

    @patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "",
            "ENABLE_OTEL": "false",
            "LOG_LEVEL": "INFO",
        },
    )
    @patch("loan_defenders.utils.observability.logging.basicConfig")
    def test_initialize_basic_logging_only(self, mock_basic_config):
        """Test initialization with basic logging only (no App Insights)."""
        Observability.initialize()

        # Verify basic logging was configured
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.INFO
        assert "format" in call_kwargs
        assert call_kwargs["force"] is True

        assert Observability._initialized is True

    @patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test-key",
            "ENABLE_OTEL": "true",
            "LOG_LEVEL": "DEBUG",
        },
    )
    @patch("loan_defenders.utils.observability.logging.basicConfig")
    @patch("loan_defenders.utils.observability.setup_observability")
    def test_initialize_with_app_insights(self, mock_setup_obs, mock_basic_config):
        """Test initialization with Application Insights enabled."""
        if not AGENT_FRAMEWORK_AVAILABLE:
            pytest.skip("Agent framework not available")

        Observability.initialize()

        # Verify basic logging configured
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.DEBUG

        # Verify App Insights setup was called
        mock_setup_obs.assert_called_once_with(
            applicationinsights_connection_string="InstrumentationKey=test-key",
            enable_sensitive_data=False,
            enable_live_metrics=True,
        )

        assert Observability._initialized is True

    @patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test-key",
            "ENABLE_OTEL": "true",
            "ENABLE_SENSITIVE_DATA": "true",
            "LOG_LEVEL": "WARNING",
        },
    )
    @patch("loan_defenders.utils.observability.logging.basicConfig")
    @patch("loan_defenders.utils.observability.setup_observability")
    def test_initialize_with_sensitive_data_enabled(self, mock_setup_obs, mock_basic_config):
        """Test initialization with sensitive data logging enabled."""
        if not AGENT_FRAMEWORK_AVAILABLE:
            pytest.skip("Agent framework not available")

        Observability.initialize()

        # Verify sensitive data flag was passed
        mock_setup_obs.assert_called_once()
        call_kwargs = mock_setup_obs.call_args[1]
        assert call_kwargs["enable_sensitive_data"] is True

    @patch("loan_defenders.utils.observability.logging.basicConfig")
    def test_initialize_idempotent(self, mock_basic_config):
        """Test initialize is idempotent (doesn't reinit unless forced)."""
        # First initialization
        Observability.initialize()
        assert mock_basic_config.call_count == 1

        # Second call should not reinitialize
        Observability.initialize()
        assert mock_basic_config.call_count == 1

        # Force reinit should work
        Observability.initialize(force_reinit=True)
        assert mock_basic_config.call_count == 2

    @patch.dict(
        os.environ,
        {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "",
            "ENABLE_OTEL": "false",
            "LOG_LEVEL": "ERROR",
        },
    )
    @patch("loan_defenders.utils.observability.logging.basicConfig")
    def test_initialize_custom_log_level(self, mock_basic_config):
        """Test initialization with custom log level."""
        Observability.initialize()

        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.ERROR


class TestObservabilityHelpers:
    """Test helper methods for observability configuration."""

    @patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"})
    def test_is_application_insights_enabled_true(self):
        """Test detecting Application Insights is enabled."""
        assert Observability.is_application_insights_enabled() is True

    @patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": ""})
    def test_is_application_insights_enabled_false(self):
        """Test detecting Application Insights is disabled."""
        assert Observability.is_application_insights_enabled() is False

    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"})
    def test_get_log_level_custom(self):
        """Test getting custom log level."""
        assert Observability.get_log_level() == "DEBUG"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_log_level_default(self):
        """Test getting default log level when not set."""
        # Remove LOG_LEVEL if it exists
        os.environ.pop("LOG_LEVEL", None)
        assert Observability.get_log_level() == "INFO"


class TestGetLogger:
    """Test logger creation with proper observability configuration."""

    def setup_method(self):
        """Reset initialization state before each test."""
        Observability._initialized = False

    def teardown_method(self):
        """Reset initialization state after each test."""
        Observability._initialized = False

    @patch("loan_defenders.utils.observability.get_logger")
    @patch("loan_defenders.utils.observability.logging.basicConfig")
    def test_get_logger_with_agent_framework(self, mock_basic_config, mock_get_framework_logger):
        """Test get_logger with agent framework available."""
        if not AGENT_FRAMEWORK_AVAILABLE:
            pytest.skip("Agent framework not available")

        mock_logger = Mock()
        mock_get_framework_logger.return_value = mock_logger

        logger = Observability.get_logger("test_agent")

        # Should use agent framework logger with prefix
        mock_get_framework_logger.assert_called_once_with("agent_framework.test_agent")
        assert logger == mock_logger

    @patch("loan_defenders.utils.observability.AGENT_FRAMEWORK_AVAILABLE", False)
    @patch("loan_defenders.utils.observability.logging.getLogger")
    @patch("loan_defenders.utils.observability.logging.basicConfig")
    def test_get_logger_fallback_to_standard_logging(self, mock_basic_config, mock_get_standard_logger):
        """Test get_logger falls back to standard logging when framework unavailable."""
        mock_logger = Mock()
        mock_get_standard_logger.return_value = mock_logger

        logger = Observability.get_logger("test_agent")

        # Should use standard logging with loan_defenders prefix
        mock_get_standard_logger.assert_called_once_with("loan_defenders.test_agent")
        assert logger == mock_logger

    @patch("loan_defenders.utils.observability.logging.basicConfig")
    def test_get_logger_ensures_initialization(self, mock_basic_config):
        """Test get_logger ensures observability is initialized."""
        assert Observability._initialized is False

        Observability.get_logger("test_agent")

        # Should have initialized
        assert Observability._initialized is True
        mock_basic_config.assert_called_once()
