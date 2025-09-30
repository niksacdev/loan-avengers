"""
Sequential Workflow Orchestrator for Loan Processing using Microsoft Agent Framework.

This orchestrator coordinates the multi-agent workflow for loan application processing,
using WorkflowBuilder to wire agents: Intake → Credit → Income → Risk.
Currently implements MVP with Intake agent and mock approval.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from agent_framework import AgentRunUpdateEvent, AgentThread, ChatAgent, WorkflowBuilder, WorkflowOutputEvent
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential
from pydantic import BaseModel

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.decision import LoanDecision, LoanDecisionStatus
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("workflow_orchestrator")


class WorkflowResponse(BaseModel):
    """Custom response for workflow streaming that matches demo script expectations."""

    agent_name: str
    content: str
    metadata: dict[str, Any] | None = None


class WorkflowOrchestrator:
    """
    Sequential workflow orchestrator for loan processing.

    Architecture:
    - Uses Microsoft Agent Framework WorkflowBuilder for agent coordination
    - Manages AgentThread state throughout the workflow
    - Streams workflow events for real-time UI updates
    - Currently implements MVP: Intake → Mock Approval
    - Future: Will expand to full workflow (Intake → Credit → Income → Risk)
    """

    def __init__(
        self,
        chat_client: FoundryChatClient | None = None,
    ):
        """
        Initialize the Workflow Orchestrator.

        Args:
            chat_client: Azure AI Foundry chat client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = FoundryChatClient(async_credential=DefaultAzureCredential())

        # Initialize Intake Agent for WorkflowBuilder
        self.intake_executor = self._create_intake_executor()

        # Initialize workflow
        self.workflow = None

        logger.info("WorkflowOrchestrator initialized")

    def _create_intake_executor(self) -> ChatAgent:
        """
        Create Intake Agent executor for WorkflowBuilder.

        Returns:
            ChatAgent configured as intake validator
        """
        # Load intake agent persona instructions from the actual persona file
        persona_instructions = PersonaLoader.load_persona("intake")

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=persona_instructions,
            name="Intake_Agent",
            description="Sharp-eyed application validator with efficient humor",
            temperature=0.1,
            max_tokens=500,
        )

    async def process_loan_application(
        self, application: LoanApplication, thread: AgentThread | None = None
    ) -> AsyncGenerator[WorkflowResponse, None]:
        """
        Process loan application through sequential agent workflow using WorkflowBuilder.

        Current MVP Implementation:
        1. Intake agent validates application using WorkflowBuilder
        2. If validation passes → Mock Approval
        3. If validation fails → Rejection with guidance

        Future: Will expand to full agent sequence using add_edge().

        Args:
            application: The loan application to process
            thread: Optional conversation thread for context

        Yields:
            WorkflowResponse: Streaming responses from agents during processing
        """
        # Create or use existing thread
        if not thread:
            thread = AgentThread()

        logger.info(
            "Starting loan application workflow",
            extra={
                "application_id": application.application_id[:8] + "***",
                "loan_amount": float(application.loan_amount),
                "thread_id": getattr(thread, "thread_id", "new"),
            },
        )

        try:
            # Build the workflow using WorkflowBuilder
            workflow = WorkflowBuilder().set_start_executor(self.intake_executor).build()

            # Convert validated Pydantic model to JSON for WorkflowBuilder
            # This preserves validation benefits while meeting framework requirements
            application_json = application.model_dump_json(indent=2)

            logger.debug(
                "Passing validated LoanApplication as JSON to workflow",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "loan_amount": float(application.loan_amount),
                }
            )

            logger.info("Processing with WorkflowBuilder - Intake Agent", extra={"step": 1})

            # Variables to track workflow results
            workflow_completed = False

            # Run the workflow with JSON string - framework requirement
            events = workflow.run_stream(application_json)

            async for event in events:
                if isinstance(event, AgentRunUpdateEvent):
                    # Stream agent updates - data field contains the streaming text chunks
                    content = str(event.data) if event.data else f"Update from {event.executor_id}"

                    yield WorkflowResponse(
                        agent_name="Intake_Agent",
                        content=content,
                        metadata={
                            "step": "intake_validation",
                            "agent": "john",
                            "event_type": "agent_update",
                            "executor_id": event.executor_id,
                        },
                    )

                elif isinstance(event, WorkflowOutputEvent):
                    # Final workflow output
                    workflow_completed = True
                    # Get workflow output - may be in different attributes depending on framework version
                    intake_result = getattr(event, "output", getattr(event, "data", str(event)))

                    logger.info("WorkflowBuilder completed - processing results")

                    # Parse the intake assessment from the workflow output
                    # For MVP, we'll do basic parsing - in production, this would be more sophisticated
                    if "FAST_TRACK" in intake_result or "STANDARD" in intake_result or "ENHANCED" in intake_result:
                        # Application passed validation - generate approval
                        logger.info("Intake validation passed - generating mock approval")

                        final_decision = LoanDecision(
                            application_id=application.application_id,
                            decision=LoanDecisionStatus.APPROVED,
                            decision_reason="Application passed intake validation",
                            confidence_score=0.85,
                            approved_amount=application.loan_amount,
                            approved_rate=0.065,  # 6.5% interest rate
                            approved_term_months=360,  # Standard 30-year mortgage
                            conditions=[],
                            decision_maker="WorkflowBuilder_Orchestrator_MVP",
                            reasoning=(
                                f"Intake Agent via WorkflowBuilder validated the application "
                                f"successfully. Assessment: {intake_result[:200]}..."
                            ),
                            agents_consulted=["Intake_Agent"],
                            processing_duration_seconds=2.0,  # Mock timing
                            review_priority="standard",
                            orchestration_pattern="sequential",
                        )

                        yield WorkflowResponse(
                            agent_name="Workflow_Orchestrator",
                            content=(
                                f"🎉 LOAN APPROVED! Intake Agent validated your "
                                f"application via WorkflowBuilder and approved your "
                                f"${application.loan_amount:,.2f} loan request. "
                                f"Full agent chaining coming next!"
                            ),
                            metadata={
                                "step": "final_decision",
                                "decision": final_decision.model_dump(),
                                "status": "approved",
                            },
                        )

                    else:
                        # Application failed validation
                        logger.info("Intake validation failed - generating rejection")

                        final_decision = LoanDecision(
                            application_id=application.application_id,
                            decision=LoanDecisionStatus.DENIED,
                            decision_reason="Failed intake validation",
                            confidence_score=0.95,
                            decision_maker="WorkflowBuilder_Orchestrator_MVP",
                            reasoning=(
                                f"Intake Agent via WorkflowBuilder could not validate the "
                                f"application. Assessment: {intake_result[:200]}..."
                            ),
                            agents_consulted=["Intake_Agent"],
                            processing_duration_seconds=2.0,
                            approved_amount=None,
                            approved_rate=None,
                            approved_term_months=None,
                            review_priority="standard",
                            orchestration_pattern="sequential",
                        )

                        yield WorkflowResponse(
                            agent_name="Workflow_Orchestrator",
                            content=(
                                "Application could not be approved at this time. "
                                "Intake Agent assessment via WorkflowBuilder "
                                "identified validation issues."
                            ),
                            metadata={
                                "step": "final_decision",
                                "decision": final_decision.model_dump(),
                                "status": "declined",
                            },
                        )

            # Log completion
            logger.info(
                "WorkflowBuilder workflow completed",
                extra={
                    "application_id": application.application_id[:8] + "***",
                    "workflow_completed": workflow_completed,
                },
            )

        except Exception as e:
            logger.error(
                "WorkflowBuilder processing failed",
                extra={
                    "application_id": application.application_id[:8] + "***",
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )

            # Yield error response
            yield WorkflowResponse(
                agent_name="Workflow_Orchestrator",
                content=(
                    f"We encountered an error processing your application with "
                    f"WorkflowBuilder. Please try again later. Error: {str(e)}"
                ),
                metadata={"step": "error", "error": str(e), "status": "error"},
            )

    async def create_sequential_workflow(self) -> WorkflowBuilder:
        """
        Create a full WorkflowBuilder workflow (Future Implementation).

        This method will be used when we expand beyond the MVP to create
        the full sequential workflow: Intake → Credit → Income → Risk.

        Returns:
            WorkflowBuilder configured with all agents
        """
        # TODO: Implement full WorkflowBuilder workflow with all agents
        # This is placeholder for future implementation

        # Example of how it will work:
        # marcus_executor = self._create_marcus_executor()  # Credit agent
        # income_executor = self._create_income_executor()  # Income agent
        # risk_executor = self._create_risk_executor()  # Risk agent
        #
        # workflow = (WorkflowBuilder()
        #     .set_start_executor(self.john_executor)
        #     .add_edge(self.john_executor, marcus_executor)
        #     .add_edge(marcus_executor, income_executor)
        #     .add_edge(income_executor, risk_executor)
        #     .build())
        #
        # return workflow

        raise NotImplementedError("Full WorkflowBuilder workflow coming in next iteration")


# Convenience function for direct usage
async def process_loan_application_workflow(
    application: LoanApplication, thread: AgentThread | None = None, chat_client: FoundryChatClient | None = None
) -> AsyncGenerator[WorkflowResponse, None]:
    """
    Convenience function to process loan application through WorkflowBuilder workflow.

    Args:
        application: The loan application to process
        thread: Optional conversation thread
        chat_client: Optional chat client (creates default if None)

    Yields:
        WorkflowResponse: Streaming responses from WorkflowBuilder workflow
    """
    orchestrator = WorkflowOrchestrator(chat_client=chat_client)
    async for response in orchestrator.process_loan_application(application, thread):
        yield response
