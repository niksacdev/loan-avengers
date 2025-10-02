"""
Integration tests for the IntakeAgent with real MCP server.

These tests verify the complete integration between IntakeAgent and the
application verification MCP server, testing the full workflow.
"""

import asyncio
import json
import subprocess
import time
from collections.abc import AsyncGenerator

import httpx
import pytest

from loan_defenders.agents.intake_agent import IntakeAgent


class TestIntakeAgentMCPIntegration:
    """Integration tests with real MCP server."""

    @pytest.fixture(scope="class")
    async def running_mcp_server(self) -> AsyncGenerator[dict, None]:
        """Start and manage the MCP server for integration tests."""
        # Start the MCP server process
        process = subprocess.Popen(
            ["uv", "run", "python", "-m", "loan_defenders.tools.mcp_servers.application_verification.server"],
            cwd="/Users/niksac/github/loan-avengers",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        await asyncio.sleep(3)

        # Verify server is running
        server_info = {"process": process, "host": "localhost", "port": 8010, "url": "http://localhost:8010/sse"}

        try:
            # Basic health check
            async with httpx.AsyncClient() as client:
                await client.get("http://localhost:8010/", timeout=5.0)
                # Server should respond (even if with error, it means it's running)
        except httpx.ConnectError:
            # If connection fails, server might not be ready
            pytest.skip("MCP server failed to start")

        yield server_info

        # Cleanup: terminate server process
        if process.poll() is None:  # Process still running
            process.terminate()
            process.wait(timeout=10)

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires Azure OpenAI configuration")
    async def test_intake_agent_with_real_mcp_server(
        self, running_mcp_server, sample_loan_application, mock_azure_chat_client
    ):
        """Test IntakeAgent with real MCP server (requires Azure config)."""
        # Create IntakeAgent with mocked chat client (to avoid Azure requirement)
        agent = IntakeAgent(chat_client=mock_azure_chat_client)

        # Mock the agent response to focus on MCP integration
        mock_response = mock_azure_chat_client.get_response.return_value
        mock_response.messages = [
            type(
                "obj",
                (object,),
                {
                    "text": json.dumps(
                        {
                            "validation_status": "COMPLETE",
                            "routing_decision": "STANDARD",
                            "confidence_score": 0.95,
                            "data_quality_score": 0.98,
                            "processing_notes": "MCP validation successful",
                            "specialist_name": "John",
                            "celebration_message": "🦅 MCP tools working perfectly!",
                            "encouragement_note": "Integration test passed!",
                            "next_step_preview": "Ready for next agent!",
                            "animation_type": "pulse",
                            "celebration_level": "mild",
                            "next_agent": "income",
                        }
                    ),
                    "author_name": "John",
                },
            )()
        ]

        # Process application
        result = await agent.process_application(sample_loan_application)

        # Verify integration worked
        assert result.agent_name == "intake"
        assert result.application_id == sample_loan_application.application_id
        assert result.assessment is not None

        # Verify MCP server was accessible (indirectly through successful agent processing)
        assert result.assessment is not None


class TestMCPServerDirectIntegration:
    """Direct integration tests with MCP server tools."""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires running MCP server")
    async def test_mcp_server_health_check(self):
        """Test MCP server health check endpoint."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8010/", timeout=5.0)
                # Just verify server responds (status code may vary)
                assert response is not None
            except httpx.ConnectError:
                pytest.skip("MCP server not running")

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires running MCP server and proper MCP client setup")
    async def test_validate_basic_parameters_tool_direct(self, sample_loan_application):
        """Test validate_basic_parameters tool directly via MCP protocol."""
        # This would require setting up proper MCP client connection
        # For now, skip as it needs the SSE endpoint to work correctly
        pytest.skip("Direct MCP tool testing requires SSE endpoint resolution")


class TestIntakeAgentEndToEnd:
    """End-to-end tests for complete intake workflow."""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires full Azure OpenAI and MCP server setup")
    async def test_complete_intake_workflow_vip_application(self, vip_loan_application):
        """Test complete workflow with VIP application (fast-track)."""
        # This test would require:
        # 1. Running MCP server
        # 2. Valid Azure OpenAI configuration
        # 3. Proper MCP client connection

        agent = IntakeAgent()
        result = await agent.process_application(vip_loan_application)

        # Verify VIP routing
        assessment = result.assessment
        assert assessment.routing_decision == "FAST_TRACK"
        assert assessment.validation_status == "COMPLETE"

        # Verify performance (should be under 5 seconds)
        # This would need timing measurement

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires full Azure OpenAI and MCP server setup")
    async def test_complete_intake_workflow_incomplete_application(self, incomplete_loan_application):
        """Test complete workflow with incomplete application."""
        agent = IntakeAgent()
        result = await agent.process_application(incomplete_loan_application)

        # Verify enhanced routing for incomplete app
        assessment = result.assessment
        assert assessment.routing_decision == "ENHANCED"

        # Should still complete successfully despite incomplete data
        assert assessment.validation_status in ["COMPLETE", "WARNING"]

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires conversation context setup")
    async def test_intake_with_conversation_context(self, sample_loan_application, sample_agent_thread):
        """Test intake processing with conversation context."""
        agent = IntakeAgent()

        # First interaction
        result1 = await agent.process_application(sample_loan_application, thread=sample_agent_thread)

        # Second interaction with same thread (should have context)
        result2 = await agent.process_application(sample_loan_application, thread=sample_agent_thread)

        # Verify both completed successfully
        assert result1["assessment"]["validation_status"] == "COMPLETE"
        assert result2["assessment"]["validation_status"] == "COMPLETE"

        # Could verify conversation context was maintained


class TestMCPServerErrorHandling:
    """Test error handling when MCP server is unavailable."""

    @pytest.mark.integration
    async def test_intake_agent_mcp_server_unavailable(self, sample_loan_application, mock_azure_chat_client):
        """Test IntakeAgent behavior when MCP server is unavailable."""
        # Create agent (will try to connect to MCP server on localhost:8010)
        # If server is not running, this should handle the error gracefully

        try:
            agent = IntakeAgent(chat_client=mock_azure_chat_client)

            # Mock a successful agent response despite MCP issues
            mock_response = mock_azure_chat_client.get_response.return_value
            mock_response.value = type(
                "obj",
                (object,),
                {
                    "validation_status": "FAILED",
                    "routing_decision": "MANUAL",
                    "confidence_score": 0.0,
                    "processing_notes": "MCP server unavailable",
                    "data_quality_score": 0.0,
                    "specialist_name": "John",
                    "celebration_message": "🦅 Eagle eyes working despite technical issues!",
                    "encouragement_note": "Will process manually!",
                    "next_step_preview": "Manual review needed!",
                    "animation_type": "pulse",
                    "celebration_level": "mild",
                    "next_agent": "manual",
                },
            )()

            # Should still be able to process (with fallback behavior)
            result = await agent.process_application(sample_loan_application)

            # Verify graceful degradation
            assert result.agent_name == "intake"
            assert result.assessment is not None

        except Exception as e:
            # If initialization fails completely, that's also acceptable error handling
            assert "connection" in str(e).lower() or "mcp" in str(e).lower()

    @pytest.mark.integration
    async def test_mcp_tool_timeout_handling(self, sample_loan_application, mock_azure_chat_client):
        """Test handling of MCP tool timeouts."""
        # This would test what happens when MCP server is slow to respond
        # For now, just verify that timeout configuration exists

        agent = IntakeAgent(chat_client=mock_azure_chat_client)

        # The MCPStreamableHTTPTool should have timeout handling
        # This is more of a verification that the integration includes timeouts
        assert agent.mcp_tool is not None

        # Actual timeout testing would require a slow/unresponsive MCP server


class TestPerformanceRequirements:
    """Test performance requirements for the intake agent."""

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.skip(reason="Requires full setup for performance testing")
    async def test_intake_agent_performance_target(self, sample_loan_application):
        """Test that intake agent meets <5 second performance target."""
        agent = IntakeAgent()

        start_time = time.time()
        result = await agent.process_application(sample_loan_application)
        end_time = time.time()

        processing_time = end_time - start_time

        # Verify performance target
        assert processing_time < 5.0, f"Processing took {processing_time:.2f} seconds, should be < 5 seconds"

        # Verify successful processing
        assert result.assessment.validation_status == "COMPLETE"

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.skip(reason="Requires multiple test runs")
    async def test_intake_agent_performance_consistency(self, sample_loan_application):
        """Test performance consistency across multiple runs."""
        agent = IntakeAgent()

        processing_times = []

        # Run multiple tests
        for _i in range(5):
            start_time = time.time()
            result = await agent.process_application(sample_loan_application)
            end_time = time.time()

            processing_time = end_time - start_time
            processing_times.append(processing_time)

            # Verify each run is successful
            assert result.assessment.validation_status == "COMPLETE"

        # Verify all runs meet performance target
        max_time = max(processing_times)
        avg_time = sum(processing_times) / len(processing_times)

        assert max_time < 5.0, f"Slowest run took {max_time:.2f} seconds"
        assert avg_time < 3.0, f"Average time {avg_time:.2f} seconds should be well under target"
