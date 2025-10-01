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

import os
from collections.abc import AsyncGenerator

from agent_framework import AgentThread, ChatAgent, SequentialBuilder, WorkflowEvent
from agent_framework._mcp import MCPStreamableHTTPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from loan_avengers.models.application import LoanApplication
from loan_avengers.models.responses import (
    CreditAssessment,
    FinalDecisionResponse,
    IncomeAssessment,
    ProcessingUpdate,
    RiskAssessment,
)
from loan_avengers.utils.observability import Observability
from loan_avengers.utils.persona_loader import PersonaLoader

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
        workflow: Sequential workflow orchestrator
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

        # Create specialized processing agents
        self.intake_agent = self._create_intake_agent()
        self.credit_agent = self._create_credit_agent()
        self.income_agent = self._create_income_agent()
        self.risk_agent = self._create_risk_agent()

        # Build the sequential processing workflow
        self.workflow = self._build_sequential_workflow()

        logger.info(
            "SequentialPipeline initialized",
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
        """Create credit assessment agent with MCP tools for credit verification and calculations."""
        # Load credit persona from markdown file
        persona = PersonaLoader.load_persona("credit")

        # MCP Tool 1: Application verification for credit reports
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Credit report and identity verification services",
            load_tools=True,
            load_prompts=False,
        )

        # MCP Tool 2: Financial calculations for DTI and affordability
        calculations_url = os.getenv("MCP_FINANCIAL_CALCULATIONS_URL")
        calculations_tool = MCPStreamableHTTPTool(
            name="financial-calculations",
            url=calculations_url,
            description="Financial calculations for credit analysis",
            load_tools=True,
            load_prompts=False,
        )

        logger.info("Credit agent created with MCP tools", extra={"mcp_servers": ["8010", "8012"]})

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=persona,
            name="Credit_Assessor",
            description="Credit risk analysis specialist",
            temperature=0.2,
            max_tokens=600,
            response_format=CreditAssessment,
            tools=[verification_tool, calculations_tool],
        )

    def _create_income_agent(self) -> ChatAgent:
        """Create income verification agent with comprehensive MCP tools for verification and analysis."""
        # Load income persona from markdown file
        persona = PersonaLoader.load_persona("income")

        # MCP Tool 1: Application verification for employment and bank data
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Employment verification and bank account data services",
            load_tools=True,
            load_prompts=False,
        )

        # MCP Tool 2: Document processing for paystubs and tax returns
        documents_url = os.getenv("MCP_DOCUMENT_PROCESSING_URL")
        documents_tool = MCPStreamableHTTPTool(
            name="document-processing",
            url=documents_url,
            description="Document extraction and validation for income verification",
            load_tools=True,
            load_prompts=False,
        )

        # MCP Tool 3: Financial calculations for income stability analysis
        calculations_url = os.getenv("MCP_FINANCIAL_CALCULATIONS_URL")
        calculations_tool = MCPStreamableHTTPTool(
            name="financial-calculations",
            url=calculations_url,
            description="Income stability and affordability calculations",
            load_tools=True,
            load_prompts=False,
        )

        logger.info("Income agent created with MCP tools", extra={"mcp_servers": ["8010", "8011", "8012"]})

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=persona,
            name="Income_Verifier",
            description="Income and employment verification specialist",
            temperature=0.1,
            max_tokens=500,
            response_format=IncomeAssessment,
            tools=[verification_tool, documents_tool, calculations_tool],
        )

    def _create_risk_agent(self) -> ChatAgent:
        """Create final risk analysis agent with comprehensive MCP tools for holistic assessment."""
        # Load risk persona from markdown file
        persona = PersonaLoader.load_persona("risk")

        # MCP Tools: ALL THREE for comprehensive risk synthesis
        # Tool 1: Application verification for final fraud and identity checks
        verification_url = os.getenv("MCP_APPLICATION_VERIFICATION_URL")
        verification_tool = MCPStreamableHTTPTool(
            name="application-verification",
            url=verification_url,
            description="Final verification and fraud detection services",
            load_tools=True,
            load_prompts=False,
        )

        # Tool 2: Document processing for comprehensive document validation
        documents_url = os.getenv("MCP_DOCUMENT_PROCESSING_URL")
        documents_tool = MCPStreamableHTTPTool(
            name="document-processing",
            url=documents_url,
            description="Comprehensive document validation and metadata analysis",
            load_tools=True,
            load_prompts=False,
        )

        # Tool 3: Financial calculations for final risk metrics
        calculations_url = os.getenv("MCP_FINANCIAL_CALCULATIONS_URL")
        calculations_tool = MCPStreamableHTTPTool(
            name="financial-calculations",
            url=calculations_url,
            description="Final financial risk calculations and metrics",
            load_tools=True,
            load_prompts=False,
        )

        logger.info(
            "Risk agent created with comprehensive MCP tools", extra={"mcp_servers": ["8010", "8011", "8012"]}
        )

        return ChatAgent(
            chat_client=self.chat_client,
            instructions=persona,
            name="Risk_Analyzer",
            description="Final loan decision maker",
            temperature=0.1,
            max_tokens=600,
            response_format=RiskAssessment,
            tools=[verification_tool, documents_tool, calculations_tool],
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

            # Yield start updates for each agent with handoff logging
            for idx, (agent_name, phase, phase_name, completion) in enumerate(phases):
                # Log agent handoff (except for first agent, already logged above)
                if idx > 0:
                    prev_agent = phases[idx - 1][1]  # Previous agent phase name
                    logger.info(
                        "Agent handoff",
                        extra={
                            "from_agent": prev_agent,
                            "to_agent": phase,
                            "application_id": Observability.mask_application_id(application.application_id),
                            "workflow_phase": phase_name,
                            "completion_percentage": completion,
                        },
                    )

                yield ProcessingUpdate(
                    agent_name=agent_name,
                    message=f"🔄 {agent_name.replace('_', ' ')} is analyzing your application...",
                    phase=phase_name,
                    completion_percentage=completion,
                    status="in_progress",
                    assessment_data={"application_id": application.application_id},
                    metadata={"stage": phase, "agent": agent_name},
                )

                # Small delay for smooth UX
                import asyncio

                await asyncio.sleep(1)

            # Execute the actual workflow (all agents run sequentially via SequentialBuilder)
            logger.info(
                "Executing SequentialBuilder workflow",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "agents_count": len(phases),
                },
            )
            result = await self.workflow.run(application_input)

            # Process workflow result and log completion
            logger.info(
                "Sequential workflow completed",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                    "result_type": type(result).__name__,
                    "total_agents": len(phases),
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
                metadata={"workflow_result": str(result)[:200]},
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


__all__ = ["SequentialPipeline"]
