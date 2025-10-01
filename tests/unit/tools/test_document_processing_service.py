"""
Unit tests for the MCPDocumentProcessingService class.

These tests focus on testing the document processing service's MCP client
integration and error handling logic.
"""

import json
from unittest.mock import AsyncMock, Mock

import pytest

from loan_avengers.tools.mcp_servers.document_processing.service import MCPDocumentProcessingService


class TestMCPDocumentProcessingService:
    """Test MCPDocumentProcessingService methods."""

    @pytest.fixture
    def mock_mcp_client(self) -> Mock:
        """Create mock MCP client for testing.

        Returns:
            Mock: Mock MCP client with async call_tool method
        """
        client = Mock()
        client.call_tool = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_mcp_client: Mock) -> MCPDocumentProcessingService:
        """Create service instance with mock client.

        Args:
            mock_mcp_client: Mock MCP client fixture

        Returns:
            MCPDocumentProcessingService: Service instance for testing
        """
        return MCPDocumentProcessingService(mcp_client=mock_mcp_client)

    async def test_init_with_client(self, mock_mcp_client):
        """Test service initialization with MCP client."""
        service = MCPDocumentProcessingService(mcp_client=mock_mcp_client)
        assert service.mcp_client == mock_mcp_client

    async def test_init_without_client(self):
        """Test service initialization without MCP client."""
        service = MCPDocumentProcessingService(mcp_client=None)
        assert service.mcp_client is None

    async def test_extract_text_from_document_success(self, service, mock_mcp_client):
        """Test successful text extraction from document.

        Note: MCP client can return responses in two formats:
        1. JSON string (most common) - parsed with json.loads()
        2. Dictionary object (less common) - used directly
        """
        # Mock response as JSON string (most common format)
        mock_response = {
            "type": "text_extraction",
            "document_path": "/path/to/doc.pdf",
            "extracted_text": "Sample document text",
            "pages": 1,
            "confidence": 0.95,
        }
        mock_mcp_client.call_tool.return_value = json.dumps(mock_response)

        result = await service.extract_text_from_document("/path/to/doc.pdf", "auto")

        # Verify MCP client was called correctly
        mock_mcp_client.call_tool.assert_called_once_with(
            "extract_text_from_document", {"document_path": "/path/to/doc.pdf", "document_type": "auto"}
        )

        # Verify result
        assert result == mock_response
        assert result["extracted_text"] == "Sample document text"

    async def test_extract_text_from_document_with_dict_response(self, service, mock_mcp_client):
        """Test text extraction when MCP returns dict instead of JSON string.

        Note: Some MCP clients may return dict objects directly instead of JSON strings.
        The service should handle both formats gracefully.
        """
        # Mock response as dict (alternative format)
        mock_response = {"type": "text_extraction", "extracted_text": "Text content"}
        mock_mcp_client.call_tool.return_value = mock_response

        result = await service.extract_text_from_document("/path/to/doc.pdf")

        # Should handle dict response
        assert result == mock_response

    async def test_extract_text_from_document_json_error(self, service, mock_mcp_client):
        """Test text extraction with JSON parse error."""
        # Mock invalid JSON response
        mock_mcp_client.call_tool.return_value = "invalid json {{"

        result = await service.extract_text_from_document("/path/to/doc.pdf")

        # Should return empty dict on error
        assert result == {}

    async def test_extract_text_from_document_exception(self, service, mock_mcp_client):
        """Test text extraction with MCP client exception."""
        # Mock exception
        mock_mcp_client.call_tool.side_effect = Exception("Connection error")

        result = await service.extract_text_from_document("/path/to/doc.pdf")

        # Should return empty dict on exception
        assert result == {}

    async def test_classify_document_type_success(self, service, mock_mcp_client):
        """Test successful document type classification."""
        # Mock response
        mock_response = {"type": "classification", "document_type": "W2", "confidence": 0.92}
        mock_mcp_client.call_tool.return_value = json.dumps(mock_response)

        result = await service.classify_document_type("Sample document content")

        # Verify MCP client was called
        mock_mcp_client.call_tool.assert_called_once_with(
            "classify_document_type", {"document_content": "Sample document content"}
        )

        # Verify result
        assert result == mock_response
        assert result["document_type"] == "W2"

    async def test_classify_document_type_error(self, service, mock_mcp_client):
        """Test document classification with error."""
        # Mock invalid response
        mock_mcp_client.call_tool.return_value = "not json"

        result = await service.classify_document_type("content")

        # Should return empty dict on error
        assert result == {}

    async def test_validate_document_format_success(self, service, mock_mcp_client):
        """Test successful document format validation."""
        # Mock response
        mock_response = {"type": "validation", "is_valid": True, "expected_format": "PDF", "actual_format": "PDF"}
        mock_mcp_client.call_tool.return_value = json.dumps(mock_response)

        result = await service.validate_document_format("/path/to/doc.pdf", "PDF")

        # Verify MCP client was called
        mock_mcp_client.call_tool.assert_called_once_with(
            "validate_document_format", {"document_path": "/path/to/doc.pdf", "expected_format": "PDF"}
        )

        # Verify result
        assert result == mock_response
        assert result["is_valid"] is True

    async def test_validate_document_format_error(self, service, mock_mcp_client):
        """Test document validation with error."""
        # Mock JSON decode error
        mock_mcp_client.call_tool.return_value = "invalid json"

        result = await service.validate_document_format("/path/to/doc.pdf", "PDF")

        # Should return empty dict on error
        assert result == {}

    async def test_extract_structured_data_success(self, service, mock_mcp_client):
        """Test successful structured data extraction."""
        # Mock schema and response
        schema = {"fields": ["name", "ssn", "income"]}
        mock_response = {"type": "structured_data", "extracted": {"name": "John Doe", "ssn": "***-**-1234"}}
        mock_mcp_client.call_tool.return_value = json.dumps(mock_response)

        result = await service.extract_structured_data("/path/to/doc.pdf", schema)

        # Verify MCP client was called with schema as JSON string
        call_args = mock_mcp_client.call_tool.call_args[0]
        assert call_args[0] == "extract_structured_data"
        assert call_args[1]["document_path"] == "/path/to/doc.pdf"
        assert json.loads(call_args[1]["data_schema"]) == schema

        # Verify result
        assert result == mock_response

    async def test_extract_structured_data_error(self, service, mock_mcp_client):
        """Test structured data extraction with error."""
        # Mock error
        mock_mcp_client.call_tool.return_value = None

        result = await service.extract_structured_data("/path/to/doc.pdf", {})

        # Should return empty dict on error
        assert result == {}

    async def test_convert_document_format_success(self, service, mock_mcp_client):
        """Test successful document format conversion."""
        # Mock response
        mock_response = {
            "type": "conversion",
            "input_path": "/path/to/input.pdf",
            "output_path": "/path/to/output.docx",
            "output_format": "docx",
        }
        mock_mcp_client.call_tool.return_value = json.dumps(mock_response)

        result = await service.convert_document_format("/path/to/input.pdf", "docx")

        # Verify MCP client was called
        mock_mcp_client.call_tool.assert_called_once_with(
            "convert_document_format", {"input_path": "/path/to/input.pdf", "output_format": "docx"}
        )

        # Verify result
        assert result == mock_response
        assert result["output_format"] == "docx"

    async def test_convert_document_format_error(self, service, mock_mcp_client):
        """Test document conversion with error."""
        # Mock JSON decode error
        mock_mcp_client.call_tool.return_value = "{ broken json"

        result = await service.convert_document_format("/path/to/input.pdf", "docx")

        # Should return empty dict on error
        assert result == {}
