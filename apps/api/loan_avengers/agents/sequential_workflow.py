"""
Unified Loan Processing Workflow using Microsoft Agent Framework SequentialBuilder.

This module creates a single continuous workflow that handles the entire loan application
journey from conversational data collection through final decision using the framework's
built-in conversation chaining and state management capabilities.

Architecture:
- Uses SequentialBuilder for automatic conversation chaining
- Leverages AgentThread for conversation persistence
- Utilizes SharedState for application data sharing
- Eliminates the need for separate coordinator and WorkflowOrchestrator
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import Any

from agent_framework import AgentThread, ChatAgent, SequentialBuilder, SharedState, WorkflowEvent
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential
from pydantic import BaseModel

from loan_avengers.models.application import LoanApplication
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("sequential_workflow")


class WorkflowResponse(BaseModel):
    """Response model for unified workflow streaming events."""

    agent_name: str
    message: str
    phase: str  # "collecting", "validating", "assessing", "deciding"
    completion_percentage: int
    collected_data: dict[str, Any] = {}
    action: str = "processing"  # "collect_info", "processing", "completed", "error"
    metadata: dict[str, Any] = {}


class SequentialLoanWorkflow:
    """
    Unified loan processing workflow using SequentialBuilder.

    This class combines conversational data collection and formal processing
    into a single continuous workflow using Microsoft Agent Framework's
    SequentialBuilder for automatic conversation chaining.

    Workflow Phases:
    1. Collection Phase (Coordinator persona) - Conversational data gathering
    2. Validation Phase (Intake agent) - Data validation and completeness
    3. Assessment Phase (Credit/Income) - Financial analysis
    4. Decision Phase (Risk agent) - Final loan decision

    Key Features:
    - Single AgentThread carries conversation throughout entire journey
    - SharedState manages application data across all agents
    - Built-in framework persistence and serialization
    - Natural conversation flow with context preservation
    """

    def __init__(
        self,
        chat_client: FoundryChatClient | None = None,
    ):
        """
        Initialize the unified workflow.

        Args:
            chat_client: Azure AI Foundry chat client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = FoundryChatClient(async_credential=DefaultAzureCredential())

        # Create specialized agents for different workflow phases
        self.coordinator_collector = self._create_coordinator_collector()
        self.intake_validator = self._create_intake_validator()
        self.credit_assessor = self._create_credit_assessor()
        self.income_verifier = self._create_income_verifier()
        self.risk_analyzer = self._create_risk_analyzer()

        # Build the sequential workflow
        self.workflow = self._build_sequential_workflow()

        logger.info("SequentialLoanWorkflow initialized with SequentialBuilder")

    def _create_coordinator_collector(self) -> ChatAgent:
        """Create loan coordinator agent for conversational data collection."""
        persona = PersonaLoader.load_persona("coordinator")

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=persona,
            name="Coordinator_Collector",
            description="Coordinator for conversational loan data collection",
            temperature=0.7,  # More conversational
            max_tokens=800,  # Longer responses for explanation
        )

    def _create_intake_validator(self) -> ChatAgent:
        """Create intake agent for data validation."""
        persona = PersonaLoader.load_persona("intake")

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=persona,
            name="Intake_Validator",
            description="Application validator",
            temperature=0.1,  # More precise
            max_tokens=500,  # Focused responses
        )

    def _create_credit_assessor(self) -> ChatAgent:
        """Create credit assessment agent."""
        # TODO: Load credit persona when created
        credit_instructions = """
        You are a Credit Assessment Specialist. Analyze the applicant's creditworthiness
        based on the loan application data in the conversation history.

        Focus on:
        - Loan amount vs. income ratio
        - Employment stability
        - Debt-to-income considerations

        Provide a structured assessment of credit risk level.
        """

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=credit_instructions,
            name="Credit_Assessor",
            description="Credit risk analysis specialist",
            temperature=0.2,
            max_tokens=600,
        )

    def _create_income_verifier(self) -> ChatAgent:
        """Create income verification agent."""
        # TODO: Load income persona when created
        income_instructions = """
        You are an Income Verification Specialist. Verify the applicant's income
        and employment information based on the conversation history.

        Focus on:
        - Income documentation requirements
        - Employment verification needs
        - Income stability assessment

        Provide verification status and requirements.
        """

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=income_instructions,
            name="Income_Verifier",
            description="Income and employment verification specialist",
            temperature=0.1,
            max_tokens=500,
        )

    def _create_risk_analyzer(self) -> ChatAgent:
        """Create final risk analysis agent."""
        # TODO: Load risk persona when created
        risk_instructions = """
        You are the Final Risk Analysis Specialist. Make the final loan decision
        based on all the assessments and information gathered in the conversation.

        Review:
        - Initial application data
        - Credit assessment results
        - Income verification status
        - Overall risk profile

        Provide FINAL loan decision: APPROVED, REJECTED, or NEEDS_MORE_INFO.
        """

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=risk_instructions,
            name="Risk_Analyzer",
            description="Final loan decision maker",
            temperature=0.1,
            max_tokens=600,
        )

    def _build_sequential_workflow(self):
        """Build the sequential workflow using SequentialBuilder."""
        return (
            SequentialBuilder()
            .participants(
                [
                    self.coordinator_collector,  # Phase 1: Conversational collection
                    self.intake_validator,  # Phase 2: Validation
                    self.credit_assessor,  # Phase 3: Credit assessment
                    self.income_verifier,  # Phase 4: Income verification
                    self.risk_analyzer,  # Phase 5: Final decision
                ]
            )
            .build()
        )

    async def process_conversation(
        self, user_message: str, thread: AgentThread, shared_state: SharedState | None = None
    ) -> AsyncGenerator[WorkflowResponse, None]:
        """
        Process user message through the unified workflow.

        This method handles both conversational data collection and formal
        processing in a single continuous flow using SequentialBuilder.

        Args:
            user_message: User's message to process
            thread: AgentThread for conversation continuity
            shared_state: SharedState for cross-agent data sharing

        Yields:
            WorkflowResponse events for real-time UI updates
        """
        try:
            if not shared_state:
                shared_state = SharedState()

            # Store shared state reference for agents to access
            await shared_state.set("application_data", {})
            await shared_state.set("workflow_phase", "collecting")

            logger.info(
                "Starting unified workflow processing",
                extra={
                    "user_message_length": len(user_message),
                    "thread_id": getattr(thread, "service_thread_id", "local"),
                },
            )

            # Process through the sequential workflow
            # SequentialBuilder automatically chains conversation between agents
            current_phase = 0
            phase_names = ["collecting", "validating", "assessing_credit", "verifying_income", "deciding"]

            async for workflow_event in self.workflow.run(user_message, thread=thread):
                # Transform workflow events to our response format
                response = await self._transform_workflow_event(
                    workflow_event, shared_state, phase_names[min(current_phase, len(phase_names) - 1)]
                )

                if response:
                    yield response

                    # Update phase tracking
                    if hasattr(workflow_event, "executor_id"):
                        if "Coordinator" in str(workflow_event.executor_id):
                            current_phase = 0
                        elif "Intake" in str(workflow_event.executor_id):
                            current_phase = 1
                        elif "Credit" in str(workflow_event.executor_id):
                            current_phase = 2
                        elif "Income" in str(workflow_event.executor_id):
                            current_phase = 3
                        elif "Risk" in str(workflow_event.executor_id):
                            current_phase = 4

            logger.info("Unified workflow processing completed", extra={"final_phase": phase_names[current_phase]})

        except Exception as e:
            logger.error("Unified workflow processing failed", extra={"error": str(e)}, exc_info=True)

            # Return error response
            yield WorkflowResponse(
                agent_name="System",
                message="I apologize, but I encountered a technical issue. Let me help you restart the process.",
                phase="error",
                completion_percentage=0,
                action="error",
                metadata={"error": str(e)},
            )

    async def _transform_workflow_event(
        self, event: WorkflowEvent, shared_state: SharedState, current_phase: str
    ) -> WorkflowResponse | None:
        """Transform workflow event to our response format."""
        try:
            # Extract agent information from event
            agent_name = "Assistant"
            message_content = ""

            # Handle different event types
            if hasattr(event, "executor_id"):
                agent_name = str(event.executor_id).replace("_", " ")

            if hasattr(event, "data") and event.data:
                if isinstance(event.data, str):
                    message_content = event.data
                elif hasattr(event.data, "text"):
                    message_content = event.data.text
                elif hasattr(event.data, "content"):
                    message_content = str(event.data.content)
                else:
                    message_content = str(event.data)

            # Get current application data from shared state
            try:
                app_data = await shared_state.get("application_data")
            except KeyError:
                app_data = {}

            # Calculate completion percentage based on phase
            phase_completion = {
                "collecting": 20,
                "validating": 40,
                "assessing_credit": 60,
                "verifying_income": 80,
                "deciding": 100,
            }

            completion = phase_completion.get(current_phase, 0)

            # Determine action based on phase and content
            action = "processing"
            if current_phase == "collecting" and message_content:
                action = "collect_info"
            elif current_phase == "deciding":
                action = "completed" if "APPROVED" in message_content or "REJECTED" in message_content else "processing"

            return WorkflowResponse(
                agent_name=agent_name,
                message=message_content or f"Processing in {current_phase} phase...",
                phase=current_phase,
                completion_percentage=completion,
                collected_data=app_data,
                action=action,
                metadata={"event_type": type(event).__name__, "phase": current_phase},
            )

        except Exception as e:
            logger.warning(
                "Failed to transform workflow event", extra={"error": str(e), "event_type": type(event).__name__}
            )
            return None

    def create_loan_application(self, collected_data: dict[str, Any]) -> LoanApplication:
        """
        Convert collected data into validated LoanApplication.

        This method can be called when the workflow indicates sufficient
        data has been collected for formal processing.

        Args:
            collected_data: Data collected through conversation

        Returns:
            Validated LoanApplication instance

        Raises:
            ValueError: If required data is missing or invalid
        """
        try:
            # Generate proper UUID for applicant_id
            applicant_id = str(uuid.uuid4())

            # Generate application_id in format LN + 10 digits
            # Use uuid4's int to get a stable 10-digit number
            app_id_num = abs(uuid.uuid4().int) % 10000000000  # Ensure 10 digits
            application_id = f"LN{app_id_num:010d}"

            # Implementation similar to coordinator's create_loan_application
            # but extracted for reuse in unified workflow
            application_data = {
                "application_id": application_id,
                "applicant_name": collected_data.get("applicant_name"),
                "applicant_id": applicant_id,
                "email": collected_data.get("email"),
                "phone": collected_data.get("phone"),
                "date_of_birth": collected_data.get("date_of_birth"),
                "loan_amount": collected_data.get("loan_amount"),
                "loan_purpose": collected_data.get("loan_purpose"),
                "loan_term_months": collected_data.get("loan_term_months", 360),
                "annual_income": collected_data.get("annual_income"),
                "employment_status": collected_data.get("employment_status"),
                "employer_name": collected_data.get("employer_name"),
                "months_employed": collected_data.get("months_employed"),
            }

            application = LoanApplication(**application_data)

            logger.info(
                "LoanApplication created from workflow data",
                extra={
                    "application_id": application.application_id,
                    "applicant_name": application.applicant_name,
                },
            )

            return application

        except Exception as e:
            logger.error(
                "Failed to create LoanApplication from workflow data",
                extra={"collected_data": collected_data},
                exc_info=True,
            )
            raise ValueError(f"Invalid workflow data for loan application: {str(e)}") from e


__all__ = ["SequentialLoanWorkflow", "WorkflowResponse"]
