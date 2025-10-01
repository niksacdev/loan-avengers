"""
Conversation Agent - Pure conversational AI for loan data collection.

Pattern: Agent-as-Tool
- Handles only natural language conversation
- Returns raw JSON response for code-based parsing
- No business logic, routing, or state management

Responsibilities:
- Natural language understanding and generation
- Conversational context and memory
- Personality (Cap-ital America)
- Ambiguity handling and clarification
"""

from __future__ import annotations

from agent_framework import AgentThread, ChatAgent
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("conversation_agent")


class ConversationAgent:
    """
    Pure conversational AI agent for loan data collection.

    Agent Scope:
    ✅ Natural language conversation
    ✅ Context and memory management
    ✅ Personality and empathy
    ✅ Ambiguity resolution

    ❌ JSON parsing (code handles this)
    ❌ Business logic (code handles this)
    ❌ State management (code handles this)
    ❌ Workflow routing (code handles this)

    Attributes:
        chat_client: Azure AI Foundry client for agent execution
        agent: ChatAgent with coordinator persona loaded

    Returns:
        Raw JSON string response (parsed by ConversationOrchestrator)
    """

    def __init__(
        self,
        chat_client: FoundryChatClient | None = None,
    ):
        """
        Initialize the conversation agent.

        Args:
            chat_client: Azure AI Foundry chat client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = FoundryChatClient(async_credential=DefaultAzureCredential())

        # Create the ChatAgent with coordinator persona
        self.agent = self._create_chat_agent()

        logger.info("ConversationAgent initialized")

    def _create_chat_agent(self) -> ChatAgent:
        """Create ChatAgent with coordinator persona for conversational data collection."""
        persona = PersonaLoader.load_persona("coordinator")

        # Prepend critical scope and format instructions
        critical_instructions = """
🚨🚨🚨 ABSOLUTELY CRITICAL - READ THIS FIRST 🚨🚨🚨

YOU ARE A HOME LOAN SPECIALIST FOR **NEW HOME PURCHASES ONLY**.

YOU DO NOT:
- Help with investments, tax planning, general financial advice
- Help with refinancing, HELOCs, or any non-purchase loans
- Answer questions about books, products, weather, or anything non-home-loan
- Provide general financial counseling

YOU ONLY DO:
- Collect information for NEW HOME PURCHASE loan applications
- Answer questions about the home loan application process
- Guide users through providing: home price, down payment, income, name, ID, email

IF USER ASKS ABOUT ANYTHING ELSE: Use the Thanos rejection message from your persona.

🚨 OUTPUT FORMAT: You MUST respond with valid JSON only:
{
  "agent_name": "Cap-ital America",
  "message": "your conversational response about HOME LOANS",
  "action": "collect_info" | "ready_for_processing" | "need_clarification" | "error",
  "collected_data": {},
  "completion_percentage": 0-100,
  "quick_replies": ["suggestion1", "suggestion2"],
  "next_step": "what info needed next"
}

NEVER plain text. ALWAYS valid JSON. ALWAYS stay in HOME LOAN scope.
"""

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=critical_instructions + "\n\n" + persona,  # Critical scope FIRST
            name="Cap_ital_America",
            description="HOME LOAN SPECIALIST for new home purchases only",
            temperature=0.1,  # Low temperature for consistent JSON format
            max_tokens=800,  # Adequate for conversational responses
        )

    async def chat(self, user_message: str, thread: AgentThread) -> str:
        """
        Execute conversational turn with user.

        Input: Natural language user message
        Output: Raw JSON string (not parsed)

        The orchestrator handles:
        - Parsing JSON response
        - Extracting fields (action, collected_data, etc.)
        - State management
        - Business logic

        Args:
            user_message: User's natural language input
            thread: AgentThread for maintaining conversation context

        Returns:
            str: Raw JSON response from agent (unparsed)
        """
        try:
            logger.info(
                "Processing conversational message",
                extra={
                    "user_message_length": len(user_message),
                    "thread_id": getattr(thread, "service_thread_id", "local"),
                },
            )

            # AgentRunResponse has .text property for direct access
            result = await self.agent.run(user_message, thread=thread)
            agent_response = result.text or "{}"

            logger.info("Agent responded", extra={"response_length": len(agent_response)})

            return agent_response

        except Exception as e:
            logger.error("Agent chat failed", extra={"error": str(e)}, exc_info=True)
            raise


__all__ = ["ConversationAgent"]
