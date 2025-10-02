# Azure Agent Service Configurations

This directory contains deployment configurations for **Azure Agent Service**, not agent implementation code.

## Overview

The actual agent code lives in `apps/api/loan_defenders/agents/`. This directory only contains:
- Azure deployment manifests
- Agent service configuration files
- Environment-specific settings (dev/staging/production)
- Workflow definitions for Azure's managed agent service

## Directory Structure

```
apps/agents/
├── README.md                    # This file
├── agent-config.yaml            # Main Azure Agent Service configuration
├── deployment/
│   ├── dev.yaml                # Development environment settings
│   ├── staging.yaml            # Staging environment settings
│   └── production.yaml         # Production environment settings
└── workflows/
    ├── loan-intake.yaml        # Intake workflow definition
    └── loan-processing.yaml    # Processing workflow definition
```

## Azure Agent Service

Azure Agent Service is a managed service for deploying and orchestrating AI agents. It handles:
- Agent lifecycle management
- Automatic scaling
- Monitoring and observability
- Integration with Azure services

## Configuration Files

### agent-config.yaml

Main configuration file that defines:
- Agent definitions and their source code locations
- Runtime requirements
- Persona files
- Tool/MCP server connections
- Resource limits

### deployment/*.yaml

Environment-specific configurations:
- API endpoints
- Azure resource connections
- Environment variables
- Scaling policies
- Monitoring settings

### workflows/*.yaml

Workflow definitions for agent orchestration:
- Agent sequencing
- Conditional logic
- Error handling
- Retry policies

## Deployment

### Prerequisites

- Azure subscription
- Azure CLI installed and configured
- Azure Container Registry with API image
- Azure Agent Service environment created

### Deploy to Azure

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Deploy agent configuration
az agent-service deploy \
  --config agent-config.yaml \
  --environment production \
  --resource-group loan-defenders-rg

# Monitor deployment
az agent-service deployment show \
  --name loan-defenders-agents \
  --resource-group loan-defenders-rg
```

## Local Development

For local development, agents run as part of the API container. Azure Agent Service is only used in cloud deployments.

## Related Documentation

- Agent implementation code: `apps/api/loan_defenders/agents/`
- API deployment: `apps/api/README.md`
- [Azure Agent Service Documentation](https://learn.microsoft.com/en-us/azure/agent-service/)

## Notes

- ⚠️ This directory is for **deployment configuration only**
- ✅ Agent **implementation code** lives in `apps/api/loan_defenders/agents/`
- 🔧 Modify these files when changing deployment settings, not agent behavior
- 📝 Agent behavior is controlled by persona markdown files in the API app
