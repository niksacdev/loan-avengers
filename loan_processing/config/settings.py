"""
Simple configuration settings for MCP servers.

This module provides basic configuration for the MCP (Model Context Protocol)
servers that provide tools for loan processing business logic.
"""

import os
from dataclasses import dataclass

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional
    pass


@dataclass
class MCPServerConfig:
    """Configuration for MCP server connections."""

    # MCP server ports
    application_verification_port: int = 8010
    document_processing_port: int = 8011
    financial_calculations_port: int = 8012

    # Connection settings
    host: str = "localhost"
    connection_timeout: int = 30

    @classmethod
    def from_env(cls) -> "MCPServerConfig":
        """Load MCP server configuration from environment variables."""
        return cls(
            application_verification_port=int(os.getenv("MCP_APP_VERIFICATION_PORT", "8010")),
            document_processing_port=int(os.getenv("MCP_DOCUMENT_PROCESSING_PORT", "8011")),
            financial_calculations_port=int(os.getenv("MCP_FINANCIAL_CALCULATIONS_PORT", "8012")),
            host=os.getenv("MCP_SERVER_HOST", "localhost"),
            connection_timeout=int(os.getenv("MCP_CONNECTION_TIMEOUT", "30")),
        )

    def get_server_url(self, server_name: str) -> str:
        """Get the full URL for an MCP server."""
        port_map = {
            "application_verification": self.application_verification_port,
            "document_processing": self.document_processing_port,
            "financial_calculations": self.financial_calculations_port,
        }

        port = port_map.get(server_name)
        if not port:
            raise ValueError(f"Unknown MCP server: {server_name}")

        return f"http://{self.host}:{port}/sse"


def get_mcp_config() -> MCPServerConfig:
    """Get MCP server configuration."""
    return MCPServerConfig.from_env()


__all__ = [
    "MCPServerConfig",
    "get_mcp_config"
]