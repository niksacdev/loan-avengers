"""
MCP Server Configuration Helper.

Provides centralized configuration management for MCP servers without creating
dependencies between servers. Each MCP server independently imports and uses
this helper to read from environment variables.

Pattern: Shared configuration interface, not shared state.
"""

from __future__ import annotations

import os
from typing import Literal

TransportType = Literal["streamable-http", "sse", "stdio"]


class MCPServerConfig:
    """
    Configuration helper for MCP servers.

    This class provides static methods for reading MCP server configuration
    from environment variables. Each MCP server imports this independently,
    maintaining server decoupling while sharing configuration patterns.

    Design Principles:
    - No shared state between servers
    - Each server reads from environment independently
    - Container-ready (Docker, Azure Container Apps, Kubernetes)
    - 12-Factor App compliance
    """

    @staticmethod
    def get_host() -> str:
        """
        Get MCP server host from environment.

        Environment Variable: MCP_SERVER_HOST
        Default: 0.0.0.0 (bind to all interfaces)

        Returns:
            str: Host address for MCP server to bind to

        Examples:
            Development: 0.0.0.0 or localhost
            Azure Container Apps: 0.0.0.0 (internal networking)
            Kubernetes: 0.0.0.0 (pod networking)
        """
        return os.getenv("MCP_SERVER_HOST", "0.0.0.0")

    @staticmethod
    def get_port(server_name: str, default_port: int) -> int:
        """
        Get port for specific MCP server from environment.

        Environment Variable: MCP_{SERVER_NAME}_PORT
        Example: MCP_APPLICATION_VERIFICATION_PORT=8010

        Args:
            server_name: Name of server in UPPER_CASE (e.g., "APPLICATION_VERIFICATION")
            default_port: Default port if environment variable not set

        Returns:
            int: Port number for the MCP server

        Examples:
            >>> MCPServerConfig.get_port("APPLICATION_VERIFICATION", 8010)
            8010  # From MCP_APPLICATION_VERIFICATION_PORT env var
        """
        env_key = f"MCP_{server_name.upper()}_PORT"
        return int(os.getenv(env_key, default_port))

    @staticmethod
    def get_transport() -> TransportType:
        """
        Get MCP transport type from environment.

        Environment Variable: MCP_TRANSPORT
        Default: streamable-http
        Options: streamable-http (recommended), sse, stdio

        Returns:
            TransportType: Transport protocol for MCP communication

        Notes:
            - streamable-http: Recommended for production (agent_framework compatible)
            - sse: Legacy Server-Sent Events transport
            - stdio: For development/testing only
        """
        transport = os.getenv("MCP_TRANSPORT", "streamable-http")
        if transport not in ["streamable-http", "sse", "stdio"]:
            # Fallback to streamable-http for invalid values
            return "streamable-http"
        return transport  # type: ignore

    @staticmethod
    def get_connection_timeout() -> int:
        """
        Get MCP connection timeout in seconds.

        Environment Variable: MCP_CONNECTION_TIMEOUT
        Default: 30 seconds

        Returns:
            int: Connection timeout in seconds
        """
        return int(os.getenv("MCP_CONNECTION_TIMEOUT", "30"))

    @staticmethod
    def format_url(host: str, port: int, transport: TransportType) -> str:
        """
        Format MCP server URL based on host, port, and transport.

        Args:
            host: Server host address
            port: Server port number
            transport: Transport type (streamable-http, sse, stdio)

        Returns:
            str: Formatted URL for the MCP server

        Examples:
            >>> MCPServerConfig.format_url("localhost", 8010, "streamable-http")
            "http://localhost:8010/mcp"
            >>> MCPServerConfig.format_url("mcp-server.internal", 8010, "sse")
            "http://mcp-server.internal:8010/sse"
        """
        if transport == "streamable-http":
            return f"http://{host}:{port}/mcp"
        elif transport == "sse":
            return f"http://{host}:{port}/sse"
        else:  # stdio doesn't need URL
            return f"stdio://{host}:{port}"


__all__ = ["MCPServerConfig", "TransportType"]
