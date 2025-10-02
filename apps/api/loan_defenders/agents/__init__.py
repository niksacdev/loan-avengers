"""
Agent personas for loan processing system.

This module contains only the agent persona definitions that can be used
with any agent framework, particularly Microsoft Agent Framework.
"""

# Agent personas are stored as markdown files in agent-persona/ directory
# These can be loaded by any agent framework implementation

AGENT_PERSONAS = {
    "coordinator": "coordinator-persona.md",
    "intake": "intake-agent-persona.md",
    "credit": "credit-agent-persona.md",
    "income": "income-agent-persona.md",
    "risk": "risk-agent-persona.md",
}


def get_persona_path(agent_type: str) -> str:
    """Get the path to an agent persona file."""
    if agent_type not in AGENT_PERSONAS:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return f"loan_defenders/agents/agent-persona/{AGENT_PERSONAS[agent_type]}"


def get_available_agents() -> list:
    """Get list of available agent types."""
    return list(AGENT_PERSONAS.keys())


__all__ = ["AGENT_PERSONAS", "get_persona_path", "get_available_agents"]
