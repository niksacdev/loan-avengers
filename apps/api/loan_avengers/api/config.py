"""
FastAPI configuration module using Pydantic Settings.

Provides environment-based configuration for:
- CORS settings
- API server settings
- Azure OpenAI/AI Foundry settings
- Logging and observability settings
"""

from __future__ import annotations

from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """
    API configuration loaded from environment variables.

    All settings can be overridden via environment variables with APP_ prefix.
    For production deployment in Azure, set these via App Service Configuration.
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Server Settings
    title: str = "Loan Avengers API"
    description: str = "Multi-agent loan processing system"
    version: str = "1.0.0"
    debug: bool = False

    # CORS Settings
    cors_origins: list[str] | str = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://localhost:5180",
        "http://localhost:3000",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Azure AI Foundry Settings (for agent framework)
    foundry_project_endpoint: str | None = None
    foundry_model_deployment_name: str | None = None

    # Azure OpenAI Settings (alternative to Foundry)
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: str | None = None

    # Logging Settings
    log_level: str = "INFO"
    enable_observability: bool = True

    # Session Management
    session_timeout_hours: int = 24
    session_cleanup_interval_hours: int = 6

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list.

        Args:
            v: Value to parse (string with comma-separated URLs or list)

        Returns:
            list[str]: List of CORS origin URLs
        """
        if isinstance(v, str):
            # Split comma-separated string
            return [origin.strip() for origin in v.split(",")]
        return v

    def get_cors_config(self) -> dict[str, Any]:
        """Get CORS configuration for FastAPI CORSMiddleware.

        Returns:
            dict: Configuration dictionary for CORSMiddleware
        """
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_allow_methods,
            "allow_headers": self.cors_allow_headers,
        }


# Global settings instance
settings = APISettings()

__all__ = ["settings", "APISettings"]
