"""
Test the Observability.extract_tool_calls_from_response helper function.
"""

from unittest.mock import Mock

import pytest

from loan_avengers.utils.observability import Observability


class TestToolCallExtraction:
    """Test the tool call extraction helper function."""

    def test_extract_tool_calls_with_valid_messages(self):
        """Test extracting tool calls from valid response messages."""
        # Mock message structure similar to AgentRunResponse
        mock_content1 = Mock()
        mock_content1.type = "function_call"
        mock_content1.name = "validate_basic_parameters"

        mock_content2 = Mock()
        mock_content2.type = "text"
        # No name attribute for text content

        mock_message1 = Mock()
        mock_message1.contents = [mock_content1, mock_content2]

        mock_content3 = Mock()
        mock_content3.type = "function_call"
        mock_content3.name = "another_function"

        mock_message2 = Mock()
        mock_message2.contents = [mock_content3]

        messages = [mock_message1, mock_message2]

        # Extract tool calls
        tool_calls = Observability.extract_tool_calls_from_response(messages)

        assert tool_calls == ["validate_basic_parameters", "another_function"]

    def test_extract_tool_calls_with_empty_messages(self):
        """Test extracting tool calls from empty messages list."""
        tool_calls = Observability.extract_tool_calls_from_response([])
        assert tool_calls == []

    def test_extract_tool_calls_with_no_contents(self):
        """Test extracting tool calls from messages without contents."""
        mock_message = Mock()
        del mock_message.contents  # Remove contents attribute

        messages = [mock_message]
        tool_calls = Observability.extract_tool_calls_from_response(messages)
        assert tool_calls == []

    def test_extract_tool_calls_with_malformed_content(self):
        """Test extracting tool calls handles malformed content gracefully."""
        mock_content1 = Mock()
        mock_content1.type = "function_call"
        del mock_content1.name  # Missing name attribute

        mock_content2 = Mock()
        del mock_content2.type  # Missing type attribute

        mock_message = Mock()
        mock_message.contents = [mock_content1, mock_content2]

        messages = [mock_message]
        tool_calls = Observability.extract_tool_calls_from_response(messages)
        
        # Should handle missing name gracefully
        assert tool_calls == ["unknown"]

    def test_extract_tool_calls_with_non_function_types(self):
        """Test that only function-type content is extracted."""
        mock_content1 = Mock()
        mock_content1.type = "text"
        mock_content1.name = "should_not_be_extracted"

        mock_content2 = Mock()
        mock_content2.type = "function_result"
        mock_content2.name = "validate_basic_parameters"

        mock_message = Mock()
        mock_message.contents = [mock_content1, mock_content2]

        messages = [mock_message]
        tool_calls = Observability.extract_tool_calls_from_response(messages)
        
        # Only function-type content should be extracted
        assert tool_calls == ["validate_basic_parameters"]

    def test_extract_tool_calls_handles_exceptions(self):
        """Test that the function handles exceptions gracefully."""
        # Create a mock that raises an exception when accessing contents
        mock_message = Mock()
        mock_message.contents = Mock(side_effect=AttributeError("Test error"))

        messages = [mock_message]
        tool_calls = Observability.extract_tool_calls_from_response(messages)
        
        # Should return empty list without raising exception
        assert tool_calls == []

    def test_extract_tool_calls_with_none_input(self):
        """Test that the function handles None input gracefully."""
        tool_calls = Observability.extract_tool_calls_from_response(None)
        assert tool_calls == []