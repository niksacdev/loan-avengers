"""
MCP Test Harness - Mock MCP servers for testing.

Provides lightweight mock implementations of MCP servers that can be used
in tests without requiring actual HTTP servers or network calls.

Pattern: Test Doubles for Integration Testing
- MockMCPServer: Base class for mock MCP tool implementations
- Provides deterministic, controllable responses
- Can simulate errors, delays, and edge cases
- No network overhead - pure Python
"""

from __future__ import annotations

from typing import Any


class MockMCPServer:
    """
    Base mock MCP server for testing.

    Simulates MCPStreamableHTTPTool behavior without HTTP.
    """

    def __init__(self, name: str, responses: dict[str, Any] | None = None):
        """
        Initialize mock MCP server.

        Args:
            name: Server name (e.g., "application-verification")
            responses: Optional dict of tool_name -> response mappings
        """
        self.name = name
        self.responses = responses or {}
        self.call_history: list[tuple[str, dict]] = []

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """
        Mock tool call that returns pre-configured responses.

        Args:
            tool_name: Name of tool being called
            arguments: Tool arguments

        Returns:
            Pre-configured response or default mock data
        """
        # Record call for assertions
        self.call_history.append((tool_name, arguments))

        # Return pre-configured response if available
        if tool_name in self.responses:
            return self.responses[tool_name]

        # Default responses for common tools
        return self._default_response(tool_name, arguments)

    def _default_response(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Generate default response based on tool name."""
        # Implement per server in subclasses
        return {"status": "success", "tool": tool_name, "arguments": arguments}

    def get_call_count(self, tool_name: str | None = None) -> int:
        """
        Get number of times a tool was called.

        Args:
            tool_name: Optional tool name to filter by

        Returns:
            Number of calls
        """
        if tool_name is None:
            return len(self.call_history)
        return sum(1 for name, _ in self.call_history if name == tool_name)

    def get_last_call(self, tool_name: str | None = None) -> tuple[str, dict] | None:
        """
        Get last call made to this server.

        Args:
            tool_name: Optional tool name to filter by

        Returns:
            Tuple of (tool_name, arguments) or None
        """
        if not self.call_history:
            return None

        if tool_name is None:
            return self.call_history[-1]

        # Find last call matching tool_name
        for name, args in reversed(self.call_history):
            if name == tool_name:
                return (name, args)
        return None

    def reset(self) -> None:
        """Reset call history."""
        self.call_history = []


class MockApplicationVerificationServer(MockMCPServer):
    """Mock application verification MCP server."""

    def __init__(self, responses: dict[str, Any] | None = None):
        super().__init__("application-verification", responses)

    def _default_response(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Default responses for verification tools."""
        if tool_name == "retrieve_credit_report":
            return {
                "applicant_id": arguments.get("applicant_id"),
                "credit_score": 720,
                "credit_bureau": "Experian",
                "risk_level": "low",
                "recommendation": "approve",
                "credit_utilization": 0.25,
                "payment_history_score": 0.95,
            }
        elif tool_name == "verify_employment":
            return {
                "applicant_id": arguments.get("applicant_id"),
                "employer_name": arguments.get("employer_name", "Test Corp"),
                "verification_status": "verified",
                "employment_verified": True,
                "position": "Software Engineer",
                "months_employed": 36,
            }
        elif tool_name == "verify_bank_account":
            return {
                "applicant_id": arguments.get("applicant_id"),
                "account_verified": True,
                "account_type": "checking",
                "average_balance": 15000.0,
                "sufficient_funds": True,
            }
        return super()._default_response(tool_name, arguments)


class MockDocumentProcessingServer(MockMCPServer):
    """Mock document processing MCP server."""

    def __init__(self, responses: dict[str, Any] | None = None):
        super().__init__("document-processing", responses)

    def _default_response(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Default responses for document tools."""
        if tool_name == "extract_paystub_data":
            return {
                "applicant_id": arguments.get("applicant_id"),
                "gross_income": 8500.0,
                "net_income": 6200.0,
                "pay_period": "monthly",
                "employer": "Test Corp",
                "confidence": 0.95,
            }
        elif tool_name == "validate_document":
            return {
                "document_id": arguments.get("document_id"),
                "valid": True,
                "document_type": "paystub",
                "confidence": 0.98,
            }
        return super()._default_response(tool_name, arguments)


class MockFinancialCalculationsServer(MockMCPServer):
    """Mock financial calculations MCP server."""

    def __init__(self, responses: dict[str, Any] | None = None):
        super().__init__("financial-calculations", responses)

    def _default_response(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Default responses for calculation tools."""
        if tool_name == "calculate_dti":
            loan_amount = arguments.get("loan_amount", 300000)
            annual_income = arguments.get("annual_income", 100000)
            dti_ratio = (loan_amount * 0.004) / (annual_income / 12)  # Rough estimate
            return {
                "dti_ratio": round(dti_ratio, 2),
                "meets_guidelines": dti_ratio <= 0.43,
                "recommendation": "approve" if dti_ratio <= 0.36 else "review",
            }
        elif tool_name == "calculate_ltv":
            loan_amount = arguments.get("loan_amount", 300000)
            property_value = arguments.get("property_value", 400000)
            ltv_ratio = loan_amount / property_value
            return {
                "ltv_ratio": round(ltv_ratio, 2),
                "meets_guidelines": ltv_ratio <= 0.80,
                "recommendation": "approve" if ltv_ratio <= 0.75 else "review",
            }
        return super()._default_response(tool_name, arguments)


class MCPTestHarness:
    """
    Complete test harness for MCP-based agent testing.

    Provides mock MCP servers and utilities for testing agents
    without requiring actual HTTP servers or external dependencies.

    Usage:
        harness = MCPTestHarness()

        # Configure custom responses
        harness.verification.responses["retrieve_credit_report"] = {
            "credit_score": 800
        }

        # Create agents with mock tools
        agent = IntakeAgent(chat_client=mock_client)
        agent.mcp_tool = harness.verification

        # Run agent and assert
        result = await agent.create_agent().process(...)
        assert harness.verification.get_call_count("retrieve_credit_report") == 1
    """

    def __init__(self):
        """Initialize all mock MCP servers."""
        self.verification = MockApplicationVerificationServer()
        self.documents = MockDocumentProcessingServer()
        self.calculations = MockFinancialCalculationsServer()

    def reset_all(self) -> None:
        """Reset all mock servers."""
        self.verification.reset()
        self.documents.reset()
        self.calculations.reset()

    def configure_approval_scenario(self) -> None:
        """Configure all servers for approval scenario."""
        self.verification.responses.update(
            {
                "retrieve_credit_report": {
                    "credit_score": 760,
                    "risk_level": "low",
                    "recommendation": "approve",
                },
                "verify_employment": {
                    "employment_verified": True,
                    "months_employed": 48,
                },
                "verify_bank_account": {
                    "account_verified": True,
                    "sufficient_funds": True,
                },
            }
        )

        self.calculations.responses.update(
            {
                "calculate_dti": {
                    "dti_ratio": 0.28,
                    "meets_guidelines": True,
                    "recommendation": "approve",
                },
                "calculate_ltv": {
                    "ltv_ratio": 0.70,
                    "meets_guidelines": True,
                    "recommendation": "approve",
                },
            }
        )

    def configure_rejection_scenario(self) -> None:
        """Configure all servers for rejection scenario."""
        self.verification.responses.update(
            {
                "retrieve_credit_report": {
                    "credit_score": 580,
                    "risk_level": "high",
                    "recommendation": "reject",
                },
                "verify_employment": {
                    "employment_verified": False,
                },
            }
        )

        self.calculations.responses.update(
            {
                "calculate_dti": {
                    "dti_ratio": 0.55,
                    "meets_guidelines": False,
                    "recommendation": "reject",
                },
            }
        )

    def get_total_calls(self) -> int:
        """Get total number of tool calls across all servers."""
        return self.verification.get_call_count() + self.documents.get_call_count() + self.calculations.get_call_count()


__all__ = [
    "MCPTestHarness",
    "MockMCPServer",
    "MockApplicationVerificationServer",
    "MockDocumentProcessingServer",
    "MockFinancialCalculationsServer",
]
