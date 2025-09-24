"""
Simple logging utility for loan processing system.

Provides basic Python logging configuration without complex dependencies.
Perfect for business logic foundation that can work with any framework.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a simple, configured logger.

    Args:
        name: Logger name (typically __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Configure logger if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Set level from parameter or environment
        log_level = level or 'INFO'
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    return logger


def configure_basic_logging(level: str = 'INFO') -> None:
    """
    Configure basic logging for the entire application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


__all__ = [
    "get_logger",
    "configure_basic_logging"
]