"""
Loan Processing Pipeline - Automated loan assessment workflow.

Sequential agent pipeline: Intake → Credit → Income → Risk

Pattern: Sequential Orchestration
- Accepts validated LoanApplication as input
- Executes specialized agents in predefined order
- Each agent passes context to next stage
- Produces structured assessment and final decision
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from agent_framework import AgentThread, ChatAgent, SequentialBuilder, WorkflowEvent
from agent_framework_foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import FinalDecisionResponse, ProcessingUpdate
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

logger = Observability.get_logger("loan_processing_pipeline")


class LoanProcessingPipeline:
    """
    Sequential agent pipeline for loan application assessment.

    Pipeline Stages:
    1. Intake Agent - Validates application data
    2. Credit Agent - Analyzes creditworthiness
    3. Income Agent - Verifies employment and income
    4. Risk Agent - Makes final recommendation

    Input: LoanApplication (validated data model)
    Output: ProcessingUpdate events → FinalDecisionResponse

    Attributes:
        chat_client: Azure AI Foundry client for agent execution
        intake_agent: Application validation specialist
        credit_agent: Credit risk assessment specialist
        income_agent: Income verification specialist
        risk_agent: Final decision maker
        workflow: Sequential workflow orchestrator
    """

    def __init__(
        self,
        chat_client: FoundryChatClient | None = None,
    ):
        """
        Initialize the processing workflow.

        Args:
            chat_client: Azure AI Foundry chat client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = FoundryChatClient(async_credential=DefaultAzureCredential())

        # Create specialized processing agents
        self.intake_agent = self._create_intake_agent()
        self.credit_agent = self._create_credit_agent()
        self.income_agent = self._create_income_agent()
        self.risk_agent = self._create_risk_agent()

        # Build the sequential processing workflow
        self.workflow = self._build_sequential_workflow()

        logger.info("LoanProcessingPipeline initialized")

    def _create_intake_agent(self) -> ChatAgent:
        """Create intake agent for application validation."""
        persona = PersonaLoader.load_persona("intake")

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=persona,
            name="Intake_Validator",
            description="Application validator",
            temperature=0.1,
            max_tokens=500,
        )

    def _create_credit_agent(self) -> ChatAgent:
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

    def _create_income_agent(self) -> ChatAgent:
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

    def _create_risk_agent(self) -> ChatAgent:
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
        """Build the sequential processing workflow using SequentialBuilder."""
        return (
            SequentialBuilder()
            .participants(
                [
                    self.intake_agent,  # Phase 1: Validation
                    self.credit_agent,  # Phase 2: Credit assessment
                    self.income_agent,  # Phase 3: Income verification
                    self.risk_agent,  # Phase 4: Final decision
                ]
            )
            .build()
        )

    async def process_application(
        self, application: LoanApplication
    ) -> AsyncGenerator[ProcessingUpdate | FinalDecisionResponse, None]:
        """
        Process loan application through automated assessment workflow.

        This method runs the application through the sequential processing
        pipeline and yields status updates as each agent completes their assessment.

        Args:
            application: Validated LoanApplication to process

        Yields:
            ProcessingUpdate events during processing
            FinalDecisionResponse when processing is complete
        """
        try:
            logger.info(
                "Starting application processing",
                extra={
                    "application_id": application.application_id,
                    "applicant_name": application.applicant_name,
                },
            )

            # Create a new thread for this processing execution
            processing_thread = AgentThread()

            # Format application data as input message for the workflow
            application_input = f"""Process this loan application:

Application ID: {application.application_id}
Applicant: {application.applicant_name}
Email: {application.email}
Loan Amount: ${application.loan_amount:,.2f}
Purpose: {application.loan_purpose}
Annual Income: ${application.annual_income:,.2f}
Employment: {application.employment_status}
Down Payment: ${application.down_payment:,.2f if application.down_payment else 0.00}

Please assess this application and provide your recommendation."""

            # Run the sequential workflow with progress updates
            logger.info("Running sequential processing workflow")

            # Agent processing phases
            phases = [
                ("Intake_Validator", "intake", 25),
                ("Credit_Assessor", "credit", 50),
                ("Income_Verifier", "income", 75),
                ("Risk_Analyzer", "risk", 100),
            ]

            # Yield start updates for each agent
            for agent_name, phase, completion in phases:
                yield ProcessingUpdate(
                    agent_name=agent_name,
                    message=f"🔄 {agent_name.replace('_', ' ')} is analyzing your application...",
                    phase=phase,
                    completion_percentage=completion,
                    status="in_progress",
                    assessment_data={"application_id": application.application_id},
                    metadata={"stage": phase},
                )

                # Simulate agent processing time for smooth UX
                import asyncio
                await asyncio.sleep(2)

            # Execute the actual workflow (all agents run)
            logger.info("Executing workflow with all agents")
            result = await self.workflow.run(application_input, thread=processing_thread)

            # Process workflow result
            logger.info("Processing workflow completed", extra={"result_type": type(result).__name__})

            # Yield final completion
            yield ProcessingUpdate(
                agent_name="Risk_Analyzer",
                message="✅ All assessments complete! Your loan decision is ready.",
                phase="completed",
                completion_percentage=100,
                status="completed",
                assessment_data={"application_id": application.application_id},
                metadata={"workflow_result": str(result)[:200]},
            )

            logger.info("Application processing completed")

        except Exception as e:
            logger.error("Application processing failed", extra={"error": str(e)}, exc_info=True)

            # Yield error update
            yield ProcessingUpdate(
                agent_name="System",
                message=f"Processing failed: {str(e)}",
                phase="error",
                completion_percentage=0,
                status="error",
                assessment_data={},
                metadata={"error": str(e)},
            )

    async def _transform_workflow_event(
        self, event: WorkflowEvent, application: LoanApplication, current_phase: str
    ) -> ProcessingUpdate | None:
        """
        Transform workflow event to ProcessingUpdate format.

        Args:
            event: WorkflowEvent from the sequential workflow
            application: LoanApplication being processed
            current_phase: Current processing phase

        Returns:
            ProcessingUpdate or None if event cannot be transformed
        """
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

            # Calculate completion percentage based on phase
            phase_completion = {
                "validating": 25,
                "assessing_credit": 50,
                "verifying_income": 75,
                "deciding": 100,
            }

            completion = phase_completion.get(current_phase, 0)

            return ProcessingUpdate(
                agent_name=agent_name,
                message=message_content or f"Processing in {current_phase} phase...",
                phase=current_phase,
                completion_percentage=completion,
                status="processing" if completion < 100 else "completed",
                assessment_data={},
                metadata={"event_type": type(event).__name__, "phase": current_phase},
            )

        except Exception as e:
            logger.warning(
                "Failed to transform workflow event", extra={"error": str(e), "event_type": type(event).__name__}
            )
            return None


__all__ = ["LoanProcessingPipeline"]
