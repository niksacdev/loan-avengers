"""
Shared utilities for the loan processing business logic foundation.

This module provides essential utilities for:
- Configuration loading from YAML files
- Agent persona loading from markdown files
- Simple logging without complex dependencies

These utilities are framework-agnostic and can be used with any agent system.
"""

from .config_loader import ConfigurationLoader
from .persona_loader import PersonaLoader, load_persona
from .logger import get_logger, configure_basic_logging

# Export public API
__all__ = [
    # Configuration utilities
    "ConfigurationLoader",

    # Agent persona utilities
    "PersonaLoader",
    "load_persona",

    # Simple logging
    "get_logger",
    "configure_basic_logging",
]