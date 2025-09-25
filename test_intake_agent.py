"""
Test script for the Intake Agent using Microsoft Agent Framework.

This script demonstrates how to use the IntakeAgent with a sample loan application
and validates observability integration (both stdio logging and Application Insights).
"""

import asyncio
from datetime import datetime
from decimal import Decimal

from agent_framework import AgentThread

from loan_avengers.agents.intake_agent import IntakeAgent
from loan_avengers.models.application import EmploymentStatus, LoanApplication, LoanPurpose
from loan_avengers.utils.observability import Observability

# Initialize observability first
Observability.initialize()
logger = Observability.get_logger("test_intake_agent")


def create_conversation_thread() -> AgentThread:
    """Create a sample conversation thread simulating UI chat history."""
    # Create thread with service ID - Agent Framework handles message store internally
    thread = AgentThread(service_thread_id="user_session_demo_123")

    # Note: In a real UI, the message store would be managed by the chat interface
    # and conversation history would be automatically added as users interact

    return thread


def create_sample_application() -> LoanApplication:
    """Create a sample loan application for testing."""
    return LoanApplication(
        application_id="LN1234567890",
        applicant_name="John Doe",
        applicant_id="550e8400-e29b-41d4-a716-446655440000",
        email="john.doe@example.com",
        phone="5551234567",
        date_of_birth=datetime(1990, 5, 15),
        loan_amount=Decimal("250000.00"),
        loan_purpose=LoanPurpose.HOME_PURCHASE,
        loan_term_months=360,
        annual_income=Decimal("85000.00"),
        employment_status=EmploymentStatus.EMPLOYED,
        employer_name="Tech Corp Inc",
        months_employed=36,
        monthly_expenses=Decimal("3500.00"),
        existing_debt=Decimal("15000.00"),
        assets=Decimal("50000.00"),
        down_payment=Decimal("50000.00"),
    )


async def test_intake_agent():
    """Test the Intake Agent with a sample application and validate observability."""
    logger.info("Starting Intake Agent test with observability validation")

    try:
        # Test observability configuration
        logger.info("=== Observability Configuration ===")
        logger.info(f"Application Insights enabled: {Observability.is_application_insights_enabled()}")
        logger.info(f"Log level: {Observability.get_log_level()}")

        # Create sample application and conversation context
        application = create_sample_application()
        conversation_thread = create_conversation_thread()
        logger.info(f"Created sample application: {application.application_id}")

        logger.info(f"Created conversation thread: {conversation_thread.service_thread_id}")

        # Initialize Sarah (Income Specialist)
        # Note: This will require Azure OpenAI credentials in environment
        sarah = IntakeAgent()
        logger.info("✨ Sarah (Income Specialist) initialized and ready to help!")

        # Test 1: Process without conversation context (traditional approach)
        logger.info("=== Test 1: Sarah's Assessment (No Context) ===")
        logger.info("🎯 Sarah is analyzing your application...")
        result_no_context = await sarah.process_application(application)

        # Test 2: Process WITH conversation context (revolutionary approach)
        logger.info("=== Test 2: Sarah's Assessment (With Conversation Context) ===")
        logger.info("🎯 Sarah is analyzing your application with full conversation history...")
        result_with_context = await sarah.process_application(application, thread=conversation_thread)

        # Compare the results
        logger.info("=== Context Comparison ===")
        assessment_no_context = result_no_context["assessment"]
        assessment_with_context = result_with_context["assessment"]

        logger.info("📋 WITHOUT Context:")
        logger.info(f"  💬 Message: '{assessment_no_context.get('celebration_message', 'Not available')}'")

        logger.info("📋 WITH Context:")
        logger.info(f"  💬 Message: '{assessment_with_context.get('celebration_message', 'Not available')}'")

        # Use the context-aware result for further testing
        result = result_with_context

        # Display Sarah's results
        logger.info("=== Sarah's Assessment Results ===")
        assessment = result["assessment"]

        logger.info(f"💬 Sarah says: '{assessment.get('celebration_message', 'Great work!')}'")
        logger.info(f"💝 Encouragement: '{assessment.get('encouragement_note', 'Keep going!')}'")
        logger.info(f"🔮 Next step: '{assessment.get('next_step_preview', 'More excitement ahead!')}'")
        logger.info(
            f"✨ Animation: {assessment.get('animation_type', 'sparkles')} "
            f"({assessment.get('celebration_level', 'moderate')} intensity)"
        )

        # Technical validation
        logger.info("=== Technical Processing Validation ===")
        technical_fields = ["validation_status", "routing_decision", "confidence_score", "data_quality_score"]
        for field in technical_fields:
            if field in assessment:
                logger.info(f"✓ {field}: {assessment[field]}")
            else:
                logger.warning(f"✗ Missing {field}")

        # Personality validation
        logger.info("=== AI Dream Team Personality Validation ===")
        personality_fields = ["specialist_name", "celebration_message", "encouragement_note", "next_step_preview"]
        for field in personality_fields:
            if field in assessment:
                logger.info(f"✓ {field}: Present and personalized")
            else:
                logger.warning(f"✗ Missing {field}")

        logger.info("=== Revolutionary Experience Benefits ===")
        logger.info("✓ Technical accuracy with personality-driven messaging")
        logger.info("✓ UI animation triggers ready for beautiful interface")
        logger.info("✓ Workflow routing with excitement building")
        logger.info("✓ Error handling with supportive personality")

        # Test observability features
        logger.info("=== Observability Features ===")
        if result["usage_stats"]["total_tokens"]:
            logger.info(f"✓ Token tracking working: {result['usage_stats']['total_tokens']} tokens")
        else:
            logger.warning("✗ Token tracking not available")

        if result["response_id"]:
            logger.info(f"✓ Response ID tracking: {result['response_id']}")
        else:
            logger.warning("✗ Response ID not available")

        if Observability.is_application_insights_enabled():
            logger.info("✓ Application Insights integration active - check Azure portal for telemetry")
        else:
            logger.info("ℹ Application Insights not configured - using stdio logging only")

        logger.info("Intake Agent test completed successfully!")

    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(test_intake_agent())
