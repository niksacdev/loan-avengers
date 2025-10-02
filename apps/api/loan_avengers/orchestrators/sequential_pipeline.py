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

import asyncio
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
                    "applicant_name": Observability.mask_pii(application.applicant_name, "name"),
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
            loan_amount_formatted = f"{application.loan_amount:,.2f}"
            annual_income_formatted = f"{application.annual_income:,.2f}"
            down_payment_formatted = f"{application.down_payment:,.2f}" if application.down_payment else "0.00"

            application_input = f"""Process this loan application:

Application ID: {application.application_id}
Applicant: {application.applicant_name}
Email: {application.email}
Loan Amount: ${loan_amount_formatted}
Purpose: {application.loan_purpose}
Annual Income: ${annual_income_formatted}
Employment: {application.employment_status}
Down Payment: ${down_payment_formatted}

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

            # Track final agent response for decision extraction
            final_response = None
            all_risk_events = []  # Track all Risk_Analyzer events for debugging

            # Track which agents have started to avoid duplicate "starting" messages
            agents_started = set()

            # Stream workflow events with timeout protection (300s = 5 minutes)
            # Prevents DoS from long-running operations
            try:
                async with asyncio.timeout(300):
                    async for event in workflow.run_stream(application_input):
                        # Extract agent information from workflow event
                        event_type = type(event).__name__

                        # Send "starting" message when agent first appears (only once per agent)
                        if hasattr(event, "executor_id"):
                            executor_id = str(event.executor_id)
                            if executor_id in agent_names and executor_id not in agents_started:
                                phase, phase_name, completion = agent_names[executor_id]
                                agents_started.add(executor_id)

                                # Calculate previous step's completion for starting message
                                previous_completion = completion - 25 if completion > 25 else 0

                                # Send "starting" update with previous step's completion
                                # Map agent-specific icons
                                agent_emoji = {
                                    "Intake_Agent": "🦸‍♂️",
                                    "Credit_Assessor": "🦸‍♀️",
                                    "Income_Verifier": "🦸",
                                    "Risk_Analyzer": "🦹‍♂️",
                                }.get(executor_id, "⚡")

                                agent_display_name = executor_id.replace("_", " ")
                                yield ProcessingUpdate(
                                    agent_name=executor_id,
                                    message=f"{agent_emoji} {agent_display_name} is analyzing your application...",
                                    phase=phase_name,
                                    completion_percentage=previous_completion,
                                    status="in_progress",
                                    assessment_data={"application_id": application.application_id},
                                    metadata={"event_type": "agent_starting", "executor_id": executor_id},
                                )

                        # Capture final response from Risk_Analyzer
                        if hasattr(event, "executor_id") and str(event.executor_id) == "Risk_Analyzer":
                            all_risk_events.append(event)

                            # Log detailed event information
                            event_attrs = {k: v for k, v in vars(event).items() if not k.startswith("_")}
                            logger.info(
                                "Risk_Analyzer event captured",
                                extra={
                                    "event_type": event_type,
                                    "event_attributes": list(event_attrs.keys()),
                                    "has_content": hasattr(event, "content"),
                                    "has_delta": hasattr(event, "delta"),
                                    "has_data": hasattr(event, "data"),
                                },
                            )

                            # Try to capture the agent's output from various possible fields
                            # AgentRunResponseUpdate objects have a 'data' field with text content
                            if hasattr(event, "data") and event.data:
                                # Check if data is AgentRunResponseUpdate with text/delta
                                if hasattr(event.data, "text"):
                                    if not final_response:
                                        final_response = ""
                                    text_chunk = event.data.text
                                    final_response += text_chunk
                                    # Print to stdout for debugging (bypasses log formatter)
                                    print(f"[RISK TEXT CHUNK]: {text_chunk[:100]}")
                                    logger.info("Accumulating text from event.data.text")
                                elif hasattr(event.data, "delta"):
                                    if not final_response:
                                        final_response = ""
                                    final_response += str(event.data.delta)
                                    logger.info("Accumulating delta from event.data.delta")
                                else:
                                    logger.info(
                                        "event.data has no text or delta field",
                                        extra={"data_type": type(event.data).__name__},
                                    )
                            elif hasattr(event, "content") and event.content:
                                final_response = event.content
                                logger.info("Captured content from event.content")
                            elif hasattr(event, "delta") and event.delta:
                                if not final_response:
                                    final_response = ""
                                final_response += str(event.delta)
                                logger.info("Accumulating delta content")

                        # Send completion updates when agent finishes (detect by checking if it's a final event)
                        # We identify completion by the event having content/data and being from a known agent
                        if hasattr(event, "executor_id"):
                            executor_id = str(event.executor_id)
                            if executor_id in agent_names and executor_id in agents_started:
                                # Only send completion if this event has actual content (not just starting)
                                has_content = (
                                    (hasattr(event, "data") and event.data)
                                    or (hasattr(event, "content") and event.content)
                                    or (hasattr(event, "delta") and event.delta)
                                )

                                if has_content:
                                    phase, phase_name, completion = agent_names[executor_id]

                                    yield ProcessingUpdate(
                                        agent_name=executor_id,
                                        message=f"✅ {executor_id.replace('_', ' ')} completed assessment",
                                        phase=phase_name,
                                        completion_percentage=completion,
                                        status="completed",
                                        assessment_data={"application_id": application.application_id},
                                        metadata={"event_type": event_type, "executor_id": executor_id},
                                    )

            except TimeoutError:
                logger.error(
                    "Workflow execution timed out after 300 seconds",
                    extra={
                        "application_id": Observability.mask_application_id(application.application_id),
                        "timeout_seconds": 300,
                    },
                )
                # Yield error update to UI
                yield ProcessingUpdate(
                    agent_name="System",
                    message="⏱️ Processing timed out. Please try again or contact support.",
                    phase="error",
                    completion_percentage=0,
                    status="error",
                    assessment_data={"application_id": application.application_id},
                    metadata={"error": "Workflow timeout after 300 seconds"},
                )
                return

            # Log workflow completion
            logger.info(
                "Sequential workflow completed",
                extra={
                    "application_id": Observability.mask_application_id(application.application_id),
                },
            )

            # Parse Risk Agent's decision from final_response
            import json

            risk_decision = None

            logger.info(
                "Attempting to parse Risk Agent decision",
                extra={
                    "final_response_available": final_response is not None,
                    "final_response_type": type(final_response).__name__ if final_response else "None",
                    "risk_events_count": len(all_risk_events),
                },
            )

            if final_response:
                try:
                    # Try to extract JSON from the response
                    # Risk Agent should return structured JSON assessment
                    response_str = str(final_response)

                    # Print actual response for debugging
                    print(f"\n{'=' * 80}")
                    print(f"FULL RISK AGENT RESPONSE ({len(response_str)} chars):")
                    print(f"{'=' * 80}")
                    print(response_str)
                    print(f"{'=' * 80}\n")

                    logger.info(
                        "Risk Agent response string",
                        extra={
                            "response_length": len(response_str),
                            "response_preview": response_str[:300],
                        },
                    )

                    # The response is a complete JSON object - parse it directly
                    try:
                        risk_decision = json.loads(response_str)
                        logger.info(
                            "Successfully parsed Risk Agent decision",
                            extra={
                                "loan_recommendation": risk_decision.get("loan_recommendation"),
                                "overall_risk": risk_decision.get("overall_risk"),
                            },
                        )
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.warning(
                            "Failed to parse Risk Agent JSON response, using fallback",
                            extra={
                                "error": str(e),
                                "error_type": type(e).__name__,
                                "response_preview": str(final_response)[:200] if final_response else "",
                            },
                        )
                except Exception as e:
                    logger.error(
                        "Unexpected error parsing Risk Agent response",
                        extra={"error": str(e), "error_type": type(e).__name__},
                        exc_info=True,
                    )

            # Use Risk Agent's decision if available, otherwise fallback
            if risk_decision:
                # Map Risk Agent recommendation to UI status
                recommendation = risk_decision.get("loan_recommendation", "APPROVE")
                status_map = {
                    "APPROVE": "approved",
                    "DENY": "denied",
                    "CONDITIONAL_APPROVAL": "conditional",
                    "MANUAL_REVIEW": "manual_review",
                }
                status = status_map.get(recommendation, "manual_review")

                # Extract decision details from Risk Agent
                approved_amount = risk_decision.get("approved_amount", float(application.loan_amount))
                interest_rate = risk_decision.get("recommended_rate", 6.5)
                term_years = risk_decision.get("recommended_terms", 360) // 12
                conditions = risk_decision.get("conditions", [])
                # Risk Agent returns "processing_notes" field, not "reasoning"
                reasoning = risk_decision.get("processing_notes", "")

                logger.info(
                    "Using Risk Agent decision",
                    extra={
                        "status": status,
                        "recommendation": recommendation,
                        "approved_amount": approved_amount,
                        "interest_rate": interest_rate,
                        "reasoning_found": bool(reasoning),
                        "reasoning_value": reasoning[:100] if reasoning else "EMPTY",
                        "risk_decision_keys": list(risk_decision.keys()) if risk_decision else [],
                    },
                )
            else:
                # Fallback to basic calculation if Risk Agent response not available
                logger.warning("Risk Agent response not available, using fallback decision logic")
                approved_amount = float(application.loan_amount)
                interest_rate = 6.5
                term_years = 30
                status = "manual_review"  # Conservative fallback
                conditions = ["Risk assessment incomplete - manual review required"]
                reasoning = "Automated risk assessment unavailable"

            # Calculate monthly payment
            term_months = term_years * 12
            monthly_rate = interest_rate / 100 / 12
            if monthly_rate > 0:
                monthly_payment = round(
                    approved_amount
                    * (monthly_rate * (1 + monthly_rate) ** term_months)
                    / ((1 + monthly_rate) ** term_months - 1),
                    2,
                )
            else:
                monthly_payment = round(approved_amount / term_months, 2)

            # Build decision data with actual Risk Agent decision
            decision_data = {
                "status": status,
                "loanAmount": approved_amount,
                "interestRate": interest_rate,
                "monthlyPayment": monthly_payment,
                "term": term_years,
                "conditions": conditions if conditions else ["Standard income and asset verification"],
                "reasoning": reasoning if risk_decision else "Assessment based on application data",
                "nextSteps": self._get_next_steps_for_status(status),
            }

            logger.info(
                "Created decision data for final event",
                extra={
                    "loan_amount_approved": approved_amount,
                    "interest_rate": interest_rate,
                    "monthly_payment": monthly_payment,
                    "term_years": term_years,
                    "status": status,
                    "has_risk_decision": risk_decision is not None,
                    "final_response_available": final_response is not None,
                },
            )

            # Yield final completion with decision data
            final_update = ProcessingUpdate(
                agent_name="Risk_Analyzer",
                message="✅ All assessments complete! Your loan decision is ready.",
                phase="completed",
                completion_percentage=100,
                status="completed",
                assessment_data={
                    "application_id": application.application_id,
                    "decision": decision_data,
                },
                metadata={"final_response": str(final_response)[:500] if final_response else ""},
            )

            logger.info(
                "Yielding final ProcessingUpdate with decision",
                extra={
                    "assessment_data_keys": list(final_update.assessment_data.keys()),
                    "has_decision": "decision" in final_update.assessment_data,
                    "decision_loan_amount": final_update.assessment_data.get("decision", {}).get("loanAmount"),
                    "decision_interest_rate": final_update.assessment_data.get("decision", {}).get("interestRate"),
                    "decision_monthly_payment": final_update.assessment_data.get("decision", {}).get("monthlyPayment"),
                    "decision_status": final_update.assessment_data.get("decision", {}).get("status"),
                },
            )

            yield final_update

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

    def _get_next_steps_for_status(self, status: str) -> list[str]:
        """
        Get appropriate next steps based on loan decision status.

        Args:
            status: Decision status (approved, denied, conditional, manual_review)

        Returns:
            List of next step instructions for the applicant
        """
        if status == "approved":
            return [
                "Your closing coordinator will contact you within 24 hours",
                "Schedule home inspection within 2 weeks",
                "Provide final income documentation",
                "Review and sign loan documents",
            ]
        elif status == "denied":
            return [
                "Review the denial reasons provided above",
                "Consider reapplying after addressing the noted concerns",
                "Contact a loan officer to discuss alternative options",
                "Check your credit report for accuracy",
            ]
        elif status == "conditional":
            return [
                "Review the conditions listed above carefully",
                "Provide all requested documentation within 10 business days",
                "Your loan officer will contact you with specific requirements",
                "Once conditions are met, final approval will be processed",
            ]
        else:  # manual_review
            return [
                "A senior loan officer will review your application",
                "You will be contacted within 2 business days",
                "Please have supporting documentation ready",
                "Additional information may be requested",
            ]


__all__ = ["SequentialPipeline"]
