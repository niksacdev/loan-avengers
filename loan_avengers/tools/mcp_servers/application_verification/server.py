"""Application Verification MCP Server."""
# ruff: noqa: I001

from __future__ import annotations

import json
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from loan_avengers.utils.observability import Observability  # noqa: E402

from .service import ApplicationVerificationServiceImpl  # noqa: E402

# Initialize logging (observability auto-initializes)
logger = Observability.get_logger("application_verification_server")

# Create MCP server and configure optional SSE
mcp = FastMCP("application-verification")
mcp.settings.host = "localhost"
mcp.settings.port = 8010

# Initialize service implementation
service = ApplicationVerificationServiceImpl()

logger.info("Application Verification MCP Server initialized on port 8010")


@mcp.tool()
async def retrieve_credit_report(applicant_id: str, full_name: str, address: str) -> str:
    """Return a credit report summary as JSON string."""
    logger.info(f"Credit report request for applicant: {applicant_id[:8]}***")
    result = await service.retrieve_credit_report(applicant_id, full_name, address)
    return json.dumps(result)


@mcp.tool()
async def verify_employment(applicant_id: str, employer_name: str, position: str) -> str:
    """Return employment verification as JSON string."""
    logger.info(f"Employment verification request received for {employer_name} position: {position}")
    result = await service.verify_employment(applicant_id, employer_name, position)
    return json.dumps(result)


@mcp.tool()
async def get_bank_account_data(account_number: str, routing_number: str) -> str:
    """Return bank account details and balance as JSON string."""
    logger.info(f"Bank account data request received for account ending in {account_number[-4:]}")
    result = await service.get_bank_account_data(account_number, routing_number)
    return json.dumps(result)


@mcp.tool()
async def get_tax_transcript_data(applicant_id: str, tax_year: int) -> str:
    """Return tax transcript summary as JSON string."""
    logger.info(f"Tax transcript data request received for tax year {tax_year}")
    result = await service.get_tax_transcript_data(applicant_id, tax_year)
    return json.dumps(result)


@mcp.tool()
async def verify_asset_information(asset_type: str, asset_details_json: str) -> str:
    """Return asset verification results as JSON string."""
    logger.info(f"Asset verification request received for {asset_type} asset type")
    try:
        asset_details = json.loads(asset_details_json) if asset_details_json else {}
    except json.JSONDecodeError:
        asset_details = {"raw": asset_details_json}
    result = await service.verify_asset_information(asset_type, asset_details)
    return json.dumps(result)


@mcp.tool()
async def validate_basic_parameters(application_data: str) -> str:
    """
    Validate basic loan application parameters for completeness and format.

    This tool performs lightweight validation for the intake agent:
    - Required field completeness check
    - Basic data format validation
    - User profile completeness scoring
    - Simple routing recommendations based on profile strength

    Args:
        application_data: JSON string of LoanApplication data

    Returns:
        JSON validation result with status, completeness scores, and routing suggestions
    """
    logger.info("Basic parameter validation request received")
    result = await service.validate_basic_parameters(application_data)
    return json.dumps(result)


@mcp.tool()
async def application_verification_health_check() -> str:
    """Health check endpoint for application verification service."""
    from datetime import datetime, timezone

    return json.dumps(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": "application_verification",
            "version": "1.0.0",
            "port": 8010,
        }
    )


if __name__ == "__main__":
    # Use streamable-http transport for Agent Framework MCPStreamableHTTPTool compatibility
    transport = "streamable-http"
    if len(sys.argv) > 1:
        if sys.argv[1] == "stdio":
            transport = "stdio"
        elif sys.argv[1] == "sse":
            transport = "sse"

    if transport == "streamable-http":
        logger.info(
            "Starting Application Verification MCP Server with streamable-http transport on http://localhost:8010/mcp"
        )
    elif transport == "sse":
        logger.info("Starting Application Verification MCP Server with SSE transport on http://localhost:8010/sse")
    else:
        logger.info("Starting Application Verification MCP Server with stdio transport")

    mcp.run(transport=transport)
