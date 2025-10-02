"""
Orchestrators - Coordination and workflow management.

This module contains orchestration logic that coordinates multiple agents
and manages conversation flow. Orchestrators bridge different layers:

- ConversationOrchestrator: Conversation → LoanApplication → Processing
- ConversationStateMachine: Deterministic conversation flow state machine
- SequentialPipeline: Multi-agent workflow using Microsoft Agent Framework

Orchestrators are NOT agents themselves - they coordinate agents.
"""

from loan_defenders.orchestrators.conversation_orchestrator import ConversationOrchestrator
from loan_defenders.orchestrators.conversation_state_machine import (
    ConversationState,
    ConversationStateMachine,
)
from loan_defenders.orchestrators.sequential_pipeline import SequentialPipeline

__all__ = [
    "ConversationOrchestrator",
    "ConversationState",
    "ConversationStateMachine",
    "SequentialPipeline",
]
