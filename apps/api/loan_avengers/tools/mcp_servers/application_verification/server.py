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
from loan_avengers.config.mcp_config import MCPServerConfig  # noqa: E402
from loan_avengers.utils.observability import Observability  # noqa: E402

from .service import ApplicationVerificationServiceImpl  # noqa: E402

# Initialize logging (observability auto-initializes)
logger = Observability.get_logger("application_verification_server")

# Create MCP server with environment-based configuration
mcp = FastMCP("application-verification")
mcp.settings.host = MCPServerConfig.get_host()
mcp.settings.port = MCPServerConfig.get_port("APPLICATION_VERIFICATION", 8010)

# Initialize service implementation
service = ApplicationVerificationServiceImpl()

logger.info("Application Verification MCP Server initialized on port 8010")


@mcp.tool()
async def retrieve_credit_report(applicant_id: str, full_name: str, address: str) -> str:
    """Return a credit report summary as JSON string."""
    logger.info("Credit report request received", extra={"applicant_id": applicant_id[:8] + "***"})
    result = await service.retrieve_credit_report(applicant_id, full_name, address)
    return json.dumps(result)


@mcp.tool()
async def verify_employment(applicant_id: str, employer_name: str, position: str) -> str:
    """Return employment verification as JSON string."""
    logger.info(
        "Employment verification request received",
        extra={"employer_name": employer_name, "position": position},
    )
    result = await service.verify_employment(applicant_id, employer_name, position)
    return json.dumps(result)


@mcp.tool()
async def get_bank_account_data(account_number: str, routing_number: str) -> str:
    """Return bank account details and balance as JSON string."""
    logger.info(
        "Bank account data request received",
        extra={"account_last_4": account_number[-4:]},
    )
    result = await service.get_bank_account_data(account_number, routing_number)
    return json.dumps(result)


@mcp.tool()
async def get_tax_transcript_data(applicant_id: str, tax_year: int) -> str:
    """Return tax transcript summary as JSON string."""
    logger.info("Tax transcript data request received", extra={"tax_year": tax_year})
    result = await service.get_tax_transcript_data(applicant_id, tax_year)
    return json.dumps(result)


@mcp.tool()
async def verify_asset_information(asset_type: str, asset_details_json: str) -> str:
    """Return asset verification results as JSON string."""
    logger.info("Asset verification request received", extra={"asset_type": asset_type})
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
    from loan_avengers.utils.mcp_transport import parse_mcp_transport_args, get_transport_info

    transport = parse_mcp_transport_args()

    logger.info(f"Starting Application Verification MCP Server with {get_transport_info(transport, 8010)}")

    mcp.run(transport=transport)
