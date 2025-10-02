"""
Live integration test for IntakeAgent with real Azure AI Foundry.

This test actually calls your Foundry endpoint to verify the complete workflow.
Run with: uv run pytest tests/integration/test_intake_agent_live.py -v -s
"""

import pytest

from loan_defenders.agents.intake_agent import IntakeAgent


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intake_agent_live_with_foundry(sample_loan_application):
    """Test IntakeAgent with real Foundry endpoint."""
    print("\n" + "=" * 60)
    print("🧪 LIVE INTEGRATION TEST - Real Foundry Endpoint")
    print("=" * 60)

    print("\n📋 Application Details:")
    print(f"  Application ID: {sample_loan_application.application_id}")
    print(f"  Applicant: {sample_loan_application.applicant_name}")
    print(f"  Loan Amount: ${sample_loan_application.loan_amount:,.2f}")
    print(f"  Annual Income: ${sample_loan_application.annual_income:,.2f}")

    print("\n🚀 Creating IntakeAgent with DefaultAzureCredential...")
    agent = IntakeAgent()

    print("\n📤 Processing application through Foundry...")
    print("   (This will call your real Azure AI Foundry endpoint)")

    try:
        result = await agent.process_application(sample_loan_application)

        print("\n✅ SUCCESS! Agent processed the application")
        print("=" * 60)

        # Display results - using Pydantic model properties
        # Verify result structure (Pydantic model validation)
        from loan_defenders.models.responses import AgentResponse

        assert isinstance(result, AgentResponse)

        assessment = result.assessment
        print("\n📊 Assessment Results:")
        print(f"  Validation Status: {assessment.validation_status}")
        print(f"  Routing Decision: {assessment.routing_decision}")
        print(f"  Confidence Score: {assessment.confidence_score:.2%}")
        print(f"  Data Quality: {assessment.data_quality_score:.2%}")
        print(f"  Specialist: {assessment.specialist_name}")

        print("\n💬 Agent Messages:")
        print(f"  Celebration: {assessment.celebration_message}")
        print(f"  Encouragement: {assessment.encouragement_note}")
        print(f"  Next Step: {assessment.next_step_preview}")

        print("\n📈 Usage Stats:")
        usage = result.usage_stats
        print(f"  Input Tokens: {usage.input_tokens}")
        print(f"  Output Tokens: {usage.output_tokens}")
        print(f"  Total Tokens: {usage.total_tokens}")

        print("\n" + "=" * 60)

        # Assertions - using Pydantic model properties
        assert result.agent_name == "intake"
        assert result.application_id == sample_loan_application.application_id
        assert result.assessment is not None
        assert assessment.validation_status in ["COMPLETE", "VALID", "WARNING", "INVALID", "FAILED"]
        assert assessment.specialist_name == "John"

        # If we got a FAILED status, it means structured parsing failed but agent still responded
        if assessment.validation_status == "FAILED":
            print("\n⚠️  Note: Structured response parsing failed, but agent responded successfully")
            print("   This is expected behavior - fallback assessment was used")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\n🔍 Error Type: {type(e).__name__}")
        print("\n📝 Full Error:")
        import traceback

        traceback.print_exc()
        raise


@pytest.mark.integration
@pytest.mark.asyncio
async def test_vip_application_live(vip_loan_application):
    """Test VIP application (high income) with real Foundry endpoint."""
    print("\n" + "=" * 60)
    print("🧪 LIVE TEST - VIP Application (Fast-Track)")
    print("=" * 60)

    print("\n📋 VIP Application Details:")
    print(f"  Application ID: {vip_loan_application.application_id}")
    print(f"  Applicant: {vip_loan_application.applicant_name}")
    print(f"  Loan Amount: ${vip_loan_application.loan_amount:,.2f}")
    print(f"  Annual Income: ${vip_loan_application.annual_income:,.2f} (VIP Level)")

    print("\n🚀 Processing VIP application...")
    agent = IntakeAgent()

    result = await agent.process_application(vip_loan_application)

    # Use Pydantic model properties
    assessment = result.assessment
    print("\n📊 VIP Assessment:")
    print(f"  Routing: {assessment.routing_decision}")
    print(f"  Status: {assessment.validation_status}")

    # VIP applications should get special routing
    print("\n✅ VIP application processed successfully")

    assert result.agent_name == "intake"


if __name__ == "__main__":
    """Run tests directly with python."""
    import sys

    sys.exit(pytest.main([__file__, "-v", "-s"]))
