"""
Logging utilities for masking sensitive data.

Provides consistent data masking across agents for privacy compliance.
"""


def mask_application_id(app_id: str) -> str:
    """
    Mask application ID for secure logging.

    Shows first 8 characters followed by *** to preserve some context
    while protecting full identifiers in logs.

    Args:
        app_id: The application ID to mask

    Returns:
        str: Masked application ID in format "XXXXXXXX***"

    Examples:
        >>> mask_application_id("LN1234567890ABCD")
        "LN123456***"
    """
    if not app_id or len(app_id) <= 8:
        return f"{app_id}***"
    return f"{app_id[:8]}***"


def extract_tool_call_names(response_messages) -> list[str]:
    """
    Extract tool call names from agent response messages.

    Simplifies the complex nested structure traversal for better readability.

    Args:
        response_messages: List of messages from agent response

    Returns:
        List of tool names that were called
    """
    tool_calls = []

    for msg in response_messages:
        if not hasattr(msg, "contents"):
            continue

        for content in msg.contents:
            if not hasattr(content, "type"):
                continue

            content_type = str(getattr(content, "type", "")).lower()
            if "function" in content_type:
                tool_name = getattr(content, "name", "unknown")
                tool_calls.append(tool_name)

    return tool_calls


__all__ = ["mask_application_id", "extract_tool_call_names"]
