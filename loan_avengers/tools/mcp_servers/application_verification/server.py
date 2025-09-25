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
    logger.info(f"Credit report request for applicant: {applicant_id}")
    result = await service.retrieve_credit_report(applicant_id, full_name, address)
    return json.dumps(result)


@mcp.tool()
async def verify_employment(applicant_id: str, employer_name: str, position: str) -> str:
    """Return employment verification as JSON string."""
    logger.info("Application server processing request")
    result = await service.verify_employment(applicant_id, employer_name, position)
    return json.dumps(result)


@mcp.tool()
async def get_bank_account_data(account_number: str, routing_number: str) -> str:
    """Return bank account details and balance as JSON string."""
    logger.info("Application server processing request")
    result = await service.get_bank_account_data(account_number, routing_number)
    return json.dumps(result)


@mcp.tool()
async def get_tax_transcript_data(applicant_id: str, tax_year: int) -> str:
    """Return tax transcript summary as JSON string."""
    logger.info("Application server processing request")
    result = await service.get_tax_transcript_data(applicant_id, tax_year)
    return json.dumps(result)


@mcp.tool()
async def verify_asset_information(asset_type: str, asset_details_json: str) -> str:
    """Return asset verification results as JSON string."""
    logger.info("Application server processing request")
    try:
        asset_details = json.loads(asset_details_json) if asset_details_json else {}
    except json.JSONDecodeError:
        asset_details = {"raw": asset_details_json}
    result = await service.verify_asset_information(asset_type, asset_details)
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
    # Default to SSE transport as recommended by architect
    transport = "sse"
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        transport = "stdio"  # Allow stdio override for development

    if transport == "sse":
        logger.info("Processing request")
    else:
        logger.info("Application server processing request")

    mcp.run(transport=transport)
