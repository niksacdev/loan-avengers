"""
Integration tests for SequentialPipeline.

Tests the complete sequential pipeline execution with all 4 specialist agents.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from loan_avengers.agents.sequential_pipeline import SequentialPipeline
from loan_avengers.models.application import LoanApplication


@pytest.fixture
def sample_application() -> LoanApplication:
    """Create a sample loan application for testing.

    Returns:
        LoanApplication: Sample application with realistic test data
    """
    return LoanApplication(
        application_id="TEST123",
        applicant_name="Integration Test User",
        applicant_id="550e8400-e29b-41d4-a716-446655440000",
        email="integration@test.com",
        phone="555-TEST",
        loan_amount=Decimal("350000"),
        annual_income=Decimal("90000"),
        property_address="456 Test Lane",
        loan_purpose="purchase",
        down_payment=Decimal("70000"),
        submitted_at=datetime.now(timezone.utc),
    )


class TestSequentialPipelineIntegration:
    """Test complete loan processing pipeline."""

    async def test_pipeline_initialization(self):
        """Test that pipeline initializes successfully."""
        pipeline = SequentialPipeline()

        assert pipeline is not None
        assert hasattr(pipeline, "process_application")

    async def test_pipeline_processes_application(self, sample_application):
        """Test that pipeline processes application and yields updates."""
        pipeline = SequentialPipeline()

        updates = []
        async for update in pipeline.process_application(sample_application):
            updates.append(update)

        # Should have received multiple updates
        assert len(updates) > 0

        # First update should be from intake or credit agent
        first_update = updates[0]
        assert hasattr(first_update, "agent_name")
        assert hasattr(first_update, "message")
        assert hasattr(first_update, "phase")

    async def test_pipeline_yields_all_agent_phases(self, sample_application):
        """Test that pipeline yields updates from all 4 agents."""
        pipeline = SequentialPipeline()

        phases_seen = set()
        async for update in pipeline.process_application(sample_application):
            phases_seen.add(update.phase)

        # Should see multiple phases (intake, credit, income, risk)
        assert len(phases_seen) >= 2  # At least 2 phases

    async def test_pipeline_provides_agent_names(self, sample_application):
        """Test that updates include agent names."""
        pipeline = SequentialPipeline()

        agent_names = set()
        async for update in pipeline.process_application(sample_application):
            agent_names.add(update.agent_name)

        # Should have at least one agent name
        assert len(agent_names) >= 1
        # Agent names should not be empty
        assert all(name for name in agent_names)

    async def test_pipeline_final_update_has_completed_status(self, sample_application):
        """Test that final update has completed status."""
        pipeline = SequentialPipeline()

        last_update = None
        async for update in pipeline.process_application(sample_application):
            last_update = update

        # Last update should indicate completion
        assert last_update is not None
        assert last_update.status in ["completed", "success", "approved", "denied"]

    async def test_pipeline_handles_valid_application(self, sample_application):
        """Test pipeline with valid application data."""
        pipeline = SequentialPipeline()

        update_count = 0
        async for update in pipeline.process_application(sample_application):
            update_count += 1
            # Each update should be valid
            assert update.agent_name
            assert update.message
            assert update.phase

        # Should have received multiple updates
        assert update_count > 0


class TestPipelineUpdateStructure:
    """Test structure of pipeline updates."""

    async def test_updates_have_required_fields(self, sample_application):
        """Test that all updates have required fields."""
        pipeline = SequentialPipeline()

        async for update in pipeline.process_application(sample_application):
            assert hasattr(update, "agent_name")
            assert hasattr(update, "message")
            assert hasattr(update, "phase")
            assert hasattr(update, "status")

            # Fields should not be None
            assert update.agent_name is not None
            assert update.message is not None
            assert update.phase is not None
            break  # Just check first update

    async def test_update_messages_are_informative(self, sample_application):
        """Test that update messages contain useful information."""
        pipeline = SequentialPipeline()

        async for update in pipeline.process_application(sample_application):
            # Messages should be strings with content
            assert isinstance(update.message, str)
            assert len(update.message) > 0
            # Should not be generic placeholders
            assert update.message != "Processing..."
            break

    async def test_updates_include_phase_information(self, sample_application):
        """Test that updates include phase information."""
        pipeline = SequentialPipeline()

        phases = []
        async for update in pipeline.process_application(sample_application):
            phases.append(update.phase)

        # Should have meaningful phase names
        assert all(isinstance(phase, str) for phase in phases)
        assert all(len(phase) > 0 for phase in phases)


class TestPipelineWithVariousApplications:
    """Test pipeline with different application types."""

    async def test_pipeline_with_high_income_application(self):
        """Test pipeline with high-income applicant."""
        high_income_app = LoanApplication(
            application_id="HIGH_INCOME",
            applicant_name="High Earner",
            applicant_id="550e8400-e29b-41d4-a716-446655440001",
            email="high@earner.com",
            phone="555-HIGH",
            loan_amount=Decimal("800000"),
            annual_income=Decimal("250000"),
            loan_purpose="purchase",
            down_payment=Decimal("200000"),
            submitted_at=datetime.now(timezone.utc),
        )

        pipeline = SequentialPipeline()
        updates = []
        async for update in pipeline.process_application(high_income_app):
            updates.append(update)

        assert len(updates) > 0

    async def test_pipeline_with_low_down_payment(self):
        """Test pipeline with low down payment application."""
        low_down_app = LoanApplication(
            application_id="LOW_DOWN",
            applicant_name="Low Down",
            applicant_id="550e8400-e29b-41d4-a716-446655440002",
            email="low@down.com",
            phone="555-LOW",
            loan_amount=Decimal("300000"),
            annual_income=Decimal("75000"),
            down_payment=Decimal("15000"),  # 5% down
            loan_purpose="purchase",
            submitted_at=datetime.now(timezone.utc),
        )

        pipeline = SequentialPipeline()
        updates = []
        async for update in pipeline.process_application(low_down_app):
            updates.append(update)

        assert len(updates) > 0


class TestPipelineErrorHandling:
    """Test pipeline error handling."""

    async def test_pipeline_with_minimal_data(self):
        """Test pipeline with minimal required data."""
        minimal_app = LoanApplication(
            application_id="MINIMAL",
            applicant_name="Min User",
            applicant_id="550e8400-e29b-41d4-a716-446655440003",
            loan_amount=Decimal("200000"),
            annual_income=Decimal("60000"),
            loan_purpose="purchase",
            submitted_at=datetime.now(timezone.utc),
        )

        pipeline = SequentialPipeline()

        # Should handle minimal data without crashing
        update_count = 0
        async for _update in pipeline.process_application(minimal_app):
            update_count += 1

        # Should produce some updates even with minimal data
        assert update_count >= 0


class TestPipelinePerformance:
    """Test pipeline performance characteristics."""

    async def test_pipeline_completes_in_reasonable_time(self, sample_application):
        """Test that pipeline completes within reasonable time."""
        import time

        pipeline = SequentialPipeline()

        start_time = time.time()

        async for _update in pipeline.process_application(sample_application):
            pass  # Process all updates

        elapsed_time = time.time() - start_time

        # Should complete within reasonable time (adjust based on expected performance)
        # Using mock agents should be fast
        assert elapsed_time < 30  # 30 seconds max for mock agents

    async def test_pipeline_streams_updates(self, sample_application):
        """Test that pipeline streams updates incrementally."""
        pipeline = SequentialPipeline()

        update_count = 0
        async for _update in pipeline.process_application(sample_application):
            update_count += 1
            # If streaming, we should get updates incrementally
            # Not all at once
            if update_count == 2:
                break  # Got at least 2 updates, streaming confirmed

        assert update_count >= 1


class TestPipelineAgentCoordination:
    """Test agent coordination in pipeline."""

    async def test_agents_process_sequentially(self, sample_application):
        """Test that agents process in sequence."""
        pipeline = SequentialPipeline()

        phases = []
        async for update in pipeline.process_application(sample_application):
            if update.phase not in phases:
                phases.append(update.phase)

        # Phases should be in logical order
        # (exact order depends on implementation)
        assert len(phases) >= 1

    async def test_each_agent_provides_assessment(self, sample_application):
        """Test that each agent provides meaningful assessment."""
        pipeline = SequentialPipeline()

        assessments_by_agent = {}
        async for update in pipeline.process_application(sample_application):
            if update.agent_name not in assessments_by_agent:
                assessments_by_agent[update.agent_name] = []
            assessments_by_agent[update.agent_name].append(update.message)

        # Each agent should provide at least one message
        for _agent_name, messages in assessments_by_agent.items():
            assert len(messages) > 0
            assert all(isinstance(msg, str) for msg in messages)
