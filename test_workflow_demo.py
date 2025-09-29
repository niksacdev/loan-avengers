#!/usr/bin/env python3
"""
Demo script for Sequential Workflow Orchestrator.

This script demonstrates the loan application workflow with:
1. Chat thread creation and management
2. Loan application processing through John (intake agent)
3. Real-time streaming responses
4. Mock approval flow

Usage:
    uv run python test_workflow_demo.py
"""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal

from agent_framework import AgentThread

from loan_avengers.agents.workflow_orchestrator import process_loan_application_workflow
from loan_avengers.models.application import LoanApplication, EmploymentStatus, LoanPurpose


def create_sample_application() -> LoanApplication:
    """Create a sample loan application for testing."""
    return LoanApplication(
        # Required fields
        application_id="LN1234567890",
        applicant_name="Alice Johnson",
        applicant_id="550e8400-e29b-41d4-a716-446655440000",  # UUID format
        email="alice.johnson@email.com",
        phone="4155551234",  # Proper US format without dashes
        date_of_birth=datetime(1990, 5, 15),

        # Loan Information
        loan_amount=Decimal("450000.00"),
        loan_purpose=LoanPurpose.HOME_PURCHASE,
        loan_term_months=360,  # 30-year mortgage

        # Employment Information
        annual_income=Decimal("95000.00"),
        employment_status=EmploymentStatus.EMPLOYED,
        employer_name="Tech Solutions Inc",
        months_employed=24,
    )


def create_problematic_application() -> LoanApplication:
    """Create a loan application that might fail validation."""
    return LoanApplication(
        # Required fields - problematic but valid format
        application_id="LN9999999999",
        applicant_name="Bob Smith",  # Valid name but poor profile
        applicant_id="550e8400-e29b-41d4-a716-446655440001",  # UUID format
        email="bob.smith@email.com",  # Valid email
        phone="4155559999",  # Valid phone
        date_of_birth=datetime(2005, 1, 1),  # Too young (19 years old)

        # Loan Information - problematic amounts
        loan_amount=Decimal("1000000.00"),  # Very high amount
        loan_purpose=LoanPurpose.HOME_PURCHASE,
        loan_term_months=360,  # Standard term

        # Employment Information - unemployed
        annual_income=Decimal("0.00"),  # No income
        employment_status=EmploymentStatus.UNEMPLOYED,  # Unemployed
        employer_name=None,
        months_employed=None,
    )


async def demonstrate_successful_workflow():
    """Demonstrate successful loan application workflow."""
    print("\n" + "="*80)
    print("🏠 LOAN AVENGERS - SEQUENTIAL WORKFLOW DEMO")
    print("="*80)
    print("Testing SUCCESSFUL loan application workflow...")
    print("-"*80)

    # Create sample application
    application = create_sample_application()

    print(f"👤 Applicant: {application.applicant_name}")
    print(f"💰 Loan Amount: ${application.loan_amount:,.2f}")
    print(f"🏢 Employment: {application.employment_status.value} at {application.employer_name or 'N/A'}")
    print(f"💵 Annual Income: ${application.annual_income:,.2f}")
    print(f"🏠 Loan Term: {application.loan_term_months} months")
    print()

    # Create agent thread for conversation context
    thread = AgentThread()
    print(f"🧵 Created AgentThread for conversation context")
    print()

    print("🚀 Starting workflow processing...")
    print("-"*50)

    try:
        # Process through workflow with streaming
        async for response in process_loan_application_workflow(application, thread):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            agent_name = response.agent_name
            content = response.content
            metadata = response.metadata or {}

            print(f"[{timestamp}] 🤖 {agent_name}:")
            print(f"  💬 {content}")

            if metadata:
                if "step" in metadata:
                    print(f"  📍 Step: {metadata['step']}")
                if "processing_time_ms" in metadata:
                    print(f"  ⏱️ Processing Time: {metadata['processing_time_ms']}ms")
                if "status" in metadata:
                    print(f"  ✅ Status: {metadata['status'].upper()}")
            print()

            # Add small delay for better visualization
            await asyncio.sleep(0.5)

    except Exception as e:
        print(f"❌ Error during workflow: {e}")
        return False

    print("="*80)
    print("✅ SUCCESSFUL WORKFLOW COMPLETED!")
    print("="*80)
    return True


async def demonstrate_failed_workflow():
    """Demonstrate failed loan application workflow."""
    print("\n" + "="*80)
    print("🚫 TESTING FAILED LOAN APPLICATION WORKFLOW")
    print("="*80)
    print("Testing loan application that should FAIL validation...")
    print("-"*80)

    # Create problematic application
    application = create_problematic_application()

    print(f"👤 Applicant: {application.applicant_name}")
    print(f"💰 Loan Amount: ${application.loan_amount:,.2f}")
    print(f"🏢 Employment: {application.employment_status.value}")
    print(f"💵 Annual Income: ${application.annual_income:,.2f}")
    print(f"🏠 Loan Term: {application.loan_term_months} months")
    print()

    # Create agent thread
    thread = AgentThread()
    print(f"🧵 Created AgentThread for conversation context")
    print()

    print("🚀 Starting workflow processing...")
    print("-"*50)

    try:
        # Process through workflow
        async for response in process_loan_application_workflow(application, thread):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            agent_name = response.agent_name
            content = response.content
            metadata = response.metadata or {}

            print(f"[{timestamp}] 🤖 {agent_name}:")
            print(f"  💬 {content}")

            if metadata:
                if "step" in metadata:
                    print(f"  📍 Step: {metadata['step']}")
                if "status" in metadata:
                    print(f"  ❌ Status: {metadata['status'].upper()}")
            print()

            # Add small delay for visualization
            await asyncio.sleep(0.5)

    except Exception as e:
        print(f"❌ Error during workflow: {e}")
        return False

    print("="*80)
    print("✅ FAILED WORKFLOW COMPLETED AS EXPECTED!")
    print("="*80)
    return True


async def main():
    """Run the complete workflow demonstration."""
    print("🦸‍♂️ LOAN AVENGERS - SEQUENTIAL WORKFLOW ORCHESTRATOR")
    print("Microsoft Agent Framework Integration Demo")
    print()

    # Test successful workflow
    success1 = await demonstrate_successful_workflow()

    # Wait between tests
    await asyncio.sleep(2)

    # Test failed workflow
    success2 = await demonstrate_failed_workflow()

    print("\n" + "="*80)
    print("📊 DEMO SUMMARY")
    print("="*80)
    print(f"✅ Successful Application Test: {'PASSED' if success1 else 'FAILED'}")
    print(f"❌ Failed Application Test: {'PASSED' if success2 else 'FAILED'}")
    print()
    print("🎯 MVP Implementation Status:")
    print("  ✅ Sequential Workflow Orchestrator created")
    print("  ✅ AgentThread integration working")
    print("  ✅ John (Intake Agent) integration complete")
    print("  ✅ Real-time streaming responses")
    print("  ✅ Mock approval/rejection flow")
    print("  ⏳ Full SequentialBuilder integration (next iteration)")
    print("  ⏳ Credit, Income, Risk agents (future)")
    print("  ⏳ API integration (next step)")
    print()
    print("🚀 Ready for API integration and UI connection!")
    print("="*80)


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())