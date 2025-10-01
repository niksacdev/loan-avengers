"""
Sequential Pipeline - Automated loan assessment workflow.

Sequential agent pipeline: Intake → Credit → Income → Risk

Pattern: Sequential Orchestration
- Accepts validated LoanApplication as input
- Executes specialized agents in predefined order
- Each agent passes context to next stage
- Produces structured assessment and final decision

Note: This is the sequential implementation. A parallel pipeline
will be added in the future for comparison.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from agent_framework import SequentialBuilder
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.agents.credit_agent import CreditAgent
from loan_avengers.agents.income_agent import IncomeAgent
from loan_avengers.agents.intake_agent import IntakeAgent
from loan_avengers.agents.risk_agent import RiskAgent
from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import FinalDecisionResponse, ProcessingUpdate
from loan_avengers.utils.observability import Observability

logger = Observability.get_logger("sequential_pipeline")


class SequentialPipeline:
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
    """

    def __init__(
        self,
        chat_client: AzureAIAgentClient | None = None,
    ):
        """
        Initialize the processing workflow.

        Args:
            chat_client: Azure AI Agent client. If None, creates with
                DefaultAzureCredential for Entra ID authentication.
        """
        if chat_client:
            self.chat_client = chat_client
        else:
            self.chat_client = AzureAIAgentClient(async_credential=DefaultAzureCredential())

        # Instantiate specialized processing agent classes
        # Each agent manages its own MCP tools and persona
        self.intake_agent = IntakeAgent(chat_client=self.chat_client)
        self.credit_agent = CreditAgent(chat_client=self.chat_client)
        self.income_agent = IncomeAgent(chat_client=self.chat_client)
        self.risk_agent = RiskAgent(chat_client=self.chat_client)

        logger.info(
            "SequentialPipeline initialized with standalone agent classes",
            extra={
                "agents": ["intake", "credit", "income", "risk"],
                "mcp_servers_enabled": {
                    "intake": ["application_verification"],
                    "credit": ["application_verification", "financial_calculations"],
                    "income": ["application_verification", "document_processing", "financial_calculations"],
                    "risk": ["application_verification", "document_processing", "financial_calculations"],
                },
            },
        )

    async def process_application(
        self, application: LoanApplication
    ) -> AsyncGenerator[ProcessingUpdate | FinalDecisionResponse, None]:
        """
        Process loan application through automated assessment workflow.

        This method uses Microsoft Agent Framework's SequentialBuilder to orchestrate
        the sequential processing pipeline. Each standalone agent class provides a
        ChatAgent via create_chat_agent() method with MCP tools already connected.

        Architecture:
        - Standalone agent classes manage construction (MCP tools, personas)
        - SequentialBuilder manages orchestration (sequential execution)
        - Separation of concerns maintained

        Args:
            application: Validated LoanApplication to process

        Yields:
            ProcessingUpdate events during processing
            FinalDecisionResponse when processing is complete
        """
        try:
            logger.info(
                "Starting sequential workflow processing",
                extra={
                    "correlation_id": Observability.get_correlation_id(),
                    "application_id": Observability.mask_application_id(application.application_id),
                    "applicant_name": application.applicant_name,
                    "loan_amount": application.loan_amount,
                    "annual_income": application.annual_income,
                    "workflow": "sequential",
                    "agents_sequence": ["intake", "credit", "income", "risk"],
                },
            )

            # Create ChatAgents from standalone agent classes
            # Framework handles MCP tool lifecycle automatically
            intake_chat = self.intake_agent.create_agent()
            credit_chat = self.credit_agent.create_agent()
            income_chat = self.income_agent.create_agent()
            risk_chat = self.risk_agent.create_agent()

            # Build sequential workflow using SequentialBuilder
            workflow = SequentialBuilder().participants([intake_chat, credit_chat, income_chat, risk_chat]).build()

            # Format application data as input message
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

            # Execute sequential workflow with streaming events
            logger.info(
                "Executing SequentialBuilder workflow",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "agents_count": 4,
                },
            )

            # Agent name mapping for progress updates
            agent_names = {
                "Intake_Agent": ("intake", "validating", 25),
                "Credit_Assessor": ("credit", "assessing_credit", 50),
                "Income_Verifier": ("income", "verifying_income", 75),
                "Risk_Analyzer": ("risk", "deciding", 100),
            }

            # Stream workflow events and convert to ProcessingUpdate
            async for event in workflow.run_stream(application_input):
                # Extract agent information from workflow event
                event_type = type(event).__name__

                logger.debug(
                    "Workflow event received",
                    extra={
                        "event_type": event_type,
                        "application_id": Observability.mask_application_id(application.application_id),
                    },
                )

                # Convert workflow events to ProcessingUpdate for UI
                if hasattr(event, "executor_id"):
                    executor_id = str(event.executor_id)
                    if executor_id in agent_names:
                        phase, phase_name, completion = agent_names[executor_id]

                        yield ProcessingUpdate(
                            agent_name=executor_id,
                            message=f"🔄 {executor_id.replace('_', ' ')} is analyzing your application...",
                            phase=phase_name,
                            completion_percentage=completion,
                            status="in_progress",
                            assessment_data={"application_id": application.application_id},
                            metadata={"event_type": event_type, "executor_id": executor_id},
                        )

            # Log workflow completion
            logger.info(
                "Sequential workflow completed",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                },
            )

            # Yield final completion
            yield ProcessingUpdate(
                agent_name="Risk_Analyzer",
                message="✅ All assessments complete! Your loan decision is ready.",
                phase="completed",
                completion_percentage=100,
                status="completed",
                assessment_data={"application_id": application.application_id},
                metadata={},
            )

            logger.info(
                "Application processing completed successfully",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "workflow": "sequential",
                },
            )

        except Exception as e:
            logger.error(
                "Sequential workflow processing failed",
                extra={
                    "correlation_id": Observability.get_correlation_id(),
                    "application_id": Observability.mask_application_id(application.application_id)
                    if application
                    else None,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "workflow": "sequential",
                },
                exc_info=True,
            )

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


__all__ = ["SequentialPipeline"]
