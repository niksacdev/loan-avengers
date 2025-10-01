# Agent Framework Setup Guide

## Overview

The `agent-framework` Python package is properly configured in this project using a **shared virtual environment** approach.

## Setup Details

### Virtual Environment Structure
- The `/workspaces/loan-avengers/apps/api/.venv` directory is a **symbolic link** to the parent project's virtual environment at `/workspaces/loan-avengers/.venv`
- This allows all agent-framework packages to be shared across the monorepo

### Installed Packages
The following agent-framework packages are available:
- `agent-framework` (v0.1.0b1) - Core framework
- `agent-framework-azure` - Azure integration
- `agent-framework-foundry` - Foundry client integration

## Importing agent_framework

All imports work correctly with the shared venv setup:

```python
# Core imports
from agent_framework import AgentRunResponse, AgentThread, ChatAgent
from agent_framework import SequentialBuilder, WorkflowEvent, SharedState

# MCP tools
from agent_framework._mcp import MCPStreamableHTTPTool

# Foundry client
from agent_framework_foundry import FoundryChatClient

# Application agents
from loan_avengers.agents.intake_agent import IntakeAgent
from loan_avengers.agents.sequential_pipeline import SequentialPipeline
from loan_avengers.agents.sequential_workflow import SequentialLoanWorkflow
```

## Running Code

### From the API directory:
```bash
cd /workspaces/loan-avengers/apps/api
.venv/bin/python your_script.py
```

### Using uv (from parent):
```bash
cd /workspaces/loan-avengers
uv run python apps/api/your_script.py
```

### Using uv (from API directory):
```bash
cd /workspaces/loan-avengers/apps/api
uv run python your_script.py
```

## Troubleshooting

### If imports fail:
1. **Check the symlink exists:**
   ```bash
   cd /workspaces/loan-avengers/apps/api
   ls -la .venv
   # Should show: .venv -> ../../.venv
   ```

2. **Recreate the symlink if needed:**
   ```bash
   cd /workspaces/loan-avengers/apps/api
   rm -rf .venv
   ln -s ../../.venv .venv
   ```

3. **Ensure parent dependencies are installed:**
   ```bash
   cd /workspaces/loan-avengers
   uv sync
   ```

### Verify imports work:
```bash
cd /workspaces/loan-avengers/apps/api
.venv/bin/python -c "from agent_framework import ChatAgent; print('✅ Success')"
```

## Notes

- The `agent-framework` package is installed from PyPI (currently v0.1.0b1)
- The package requires Python >=3.10
- Azure and Foundry extras are included for full functionality
- The shared venv approach simplifies dependency management across the monorepo

## Status

✅ **agent_framework imports are working correctly**
- All core imports tested
- Workflow components tested
- MCP tools tested
- Foundry client tested
- Application agents tested

Last verified: 2025-10-01
