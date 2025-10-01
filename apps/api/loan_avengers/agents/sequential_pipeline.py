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

from agent_framework import AgentThread
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
                    "intake": ["8010"],
                    "credit": ["8010", "8012"],
                    "income": ["8010", "8011", "8012"],
                    "risk": ["8010", "8011", "8012"],
                },
            },
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
        import asyncio

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

            # Create a new thread for conversation context across agents
            thread = AgentThread()

            # Agent processing phases with handoff logging
            phases = [
                ("Intake_Validator", "intake", "validating", 25),
                ("Credit_Assessor", "credit", "assessing_credit", 50),
                ("Income_Verifier", "income", "verifying_income", 75),
                ("Risk_Analyzer", "risk", "deciding", 100),
            ]

            # Log start of sequential workflow
            logger.info(
                "Agent handoff",
                extra={
                    "from_agent": "START",
                    "to_agent": "intake",
                    "application_id": Observability.mask_application_id(application.application_id),
                    "workflow_phase": "validating",
                },
            )

            # Store assessments from each agent for context passing
            previous_assessments = []

            # Phase 1: Intake Agent - Validates application data
            yield ProcessingUpdate(
                agent_name="Intake_Validator",
                message="🔄 Intake Validator is analyzing your application...",
                phase="validating",
                completion_percentage=25,
                status="in_progress",
                assessment_data={"application_id": application.application_id},
                metadata={"stage": "intake", "agent": "Intake_Validator"},
            )
            await asyncio.sleep(0.5)

            intake_result = await self.intake_agent.process_application(application, thread=thread)
            previous_assessments.append(intake_result)

            # Log handoff to credit agent
            logger.info(
                "Agent handoff",
                extra={
                    "from_agent": "intake",
                    "to_agent": "credit",
                    "application_id": Observability.mask_application_id(application.application_id),
                    "workflow_phase": "assessing_credit",
                },
            )

            # Phase 2: Credit Agent - Analyzes creditworthiness
            yield ProcessingUpdate(
                agent_name="Credit_Assessor",
                message="🔄 Credit Assessor is analyzing your application...",
                phase="assessing_credit",
                completion_percentage=50,
                status="in_progress",
                assessment_data={"application_id": application.application_id},
                metadata={"stage": "credit", "agent": "Credit_Assessor"},
            )
            await asyncio.sleep(0.5)

            credit_result = await self.credit_agent.process_application(
                application, thread=thread, previous_assessments=previous_assessments
            )
            previous_assessments.append(credit_result)

            # Log handoff to income agent
            logger.info(
                "Agent handoff",
                extra={
                    "from_agent": "credit",
                    "to_agent": "income",
                    "application_id": Observability.mask_application_id(application.application_id),
                    "workflow_phase": "verifying_income",
                },
            )

            # Phase 3: Income Agent - Verifies employment and income
            yield ProcessingUpdate(
                agent_name="Income_Verifier",
                message="🔄 Income Verifier is analyzing your application...",
                phase="verifying_income",
                completion_percentage=75,
                status="in_progress",
                assessment_data={"application_id": application.application_id},
                metadata={"stage": "income", "agent": "Income_Verifier"},
            )
            await asyncio.sleep(0.5)

            income_result = await self.income_agent.process_application(
                application, thread=thread, previous_assessments=previous_assessments
            )
            previous_assessments.append(income_result)

            # Log handoff to risk agent
            logger.info(
                "Agent handoff",
                extra={
                    "from_agent": "income",
                    "to_agent": "risk",
                    "application_id": Observability.mask_application_id(application.application_id),
                    "workflow_phase": "deciding",
                },
            )

            # Phase 4: Risk Agent - Makes final recommendation
            yield ProcessingUpdate(
                agent_name="Risk_Analyzer",
                message="🔄 Risk Analyzer is analyzing your application...",
                phase="deciding",
                completion_percentage=100,
                status="in_progress",
                assessment_data={"application_id": application.application_id},
                metadata={"stage": "risk", "agent": "Risk_Analyzer"},
            )
            await asyncio.sleep(0.5)

            risk_result = await self.risk_agent.process_application(
                application, thread=thread, previous_assessments=previous_assessments
            )

            # Process workflow result and log completion
            logger.info(
                "Sequential workflow completed",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "total_agents": len(phases),
                    "final_recommendation": risk_result.assessment.loan_recommendation,
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
                metadata={
                    "final_recommendation": risk_result.assessment.loan_recommendation,
                    "overall_risk": risk_result.assessment.overall_risk,
                },
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
