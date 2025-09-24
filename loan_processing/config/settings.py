"""
Simple configuration settings for MCP servers.

This module provides configuration loading for MCP (Model Context Protocol)
servers from mcp_servers.yaml with environment variable overrides.
"""

import os
from pathlib import Path
from typing import Dict, Any

import yaml

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional
    pass


class MCPServerConfig:
    """Configuration for MCP server connections loaded from YAML."""

    def __init__(self, servers_config: Dict[str, Any]):
        """Initialize with servers configuration dictionary."""
        self.servers = servers_config
        self.connection_timeout = int(os.getenv("MCP_CONNECTION_TIMEOUT", "30"))

    @classmethod
    def load_from_yaml(cls, config_path: Path = None) -> "MCPServerConfig":
        """Load MCP server configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent / "mcp_servers.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"MCP servers config not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        servers = config.get("servers", {})

        # Apply environment variable overrides
        for server_name, server_config in servers.items():
            # Override host if environment variable exists
            env_host = os.getenv(f"MCP_{server_name.upper()}_HOST")
            if env_host:
                server_config["host"] = env_host

            # Override port if environment variable exists
            env_port = os.getenv(f"MCP_{server_name.upper()}_PORT")
            if env_port:
                server_config["port"] = int(env_port)
                # Rebuild URL with new port
                server_config["url"] = f"http://{server_config['host']}:{server_config['port']}/sse"

        return cls(servers)

    def get_server_config(self, server_name: str) -> Dict[str, Any]:
        """Get configuration for a specific MCP server."""
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")

        return self.servers[server_name]

    def get_server_url(self, server_name: str) -> str:
        """Get the full URL for an MCP server."""
        server_config = self.get_server_config(server_name)
        return server_config["url"]

    def get_available_servers(self) -> list:
        """Get list of available MCP server names."""
        return list(self.servers.keys())

    def get_server_tools(self, server_name: str) -> list:
        """Get list of tools available on a specific server."""
        server_config = self.get_server_config(server_name)
        return server_config.get("tools", [])


def get_mcp_config() -> MCPServerConfig:
    """Get MCP server configuration from YAML file."""
    return MCPServerConfig.load_from_yaml()


__all__ = [
    "MCPServerConfig",
    "get_mcp_config"
]