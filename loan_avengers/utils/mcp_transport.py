"""
Shared utilities for MCP server command-line argument parsing.

Provides consistent transport selection across all MCP servers.
"""

import sys
from typing import Literal

TransportType = Literal["streamable-http", "sse", "stdio"]


def parse_mcp_transport_args() -> TransportType:
    """
    Parse command-line arguments to determine MCP transport type.

    Provides consistent command-line interface across all MCP servers:
    - Default: streamable-http (Agent Framework MCPStreamableHTTPTool compatibility)
    - stdio: For development/testing
    - sse: For legacy compatibility

    Returns:
        TransportType: The selected transport method

    Examples:
        python server.py                    # Uses streamable-http
        python server.py stdio              # Uses stdio
        python server.py sse                # Uses sse
    """
    # Use streamable-http transport for Agent Framework MCPStreamableHTTPTool compatibility
    transport: TransportType = "streamable-http"

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "stdio":
            transport = "stdio"
        elif arg == "sse":
            transport = "sse"
        # Any other argument defaults to streamable-http

    return transport


def get_transport_info(transport: TransportType, port: int) -> str:
    """
    Get descriptive information about the selected transport.

    Args:
        transport: The transport type
        port: The server port number

    Returns:
        str: Human-readable description of the transport configuration
    """
    if transport == "streamable-http":
        return f"streamable-http transport on http://localhost:{port}/mcp"
    elif transport == "sse":
        return f"SSE transport on http://localhost:{port}/sse"
    else:
        return "stdio transport"


__all__ = ["parse_mcp_transport_args", "get_transport_info", "TransportType"]
