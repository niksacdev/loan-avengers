# Quick Start Guide

Get the Loan Avengers system up and running in under 10 minutes!

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed
- **Node.js 18+** and npm
- **uv package manager** ([installation guide](https://docs.astral.sh/uv/))
- **Azure AI Foundry** account with GPT-4 access
- **Git** for version control

> If you experience any problems during setup, see the [Troubleshooting Guide](../reference/troubleshooting.md) for solutions to common issues.

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/niksacdev/loan-avengers.git
cd loan-avengers
```

### 2. Set Up Environment Variables

Create a `.env` file in the **project root directory**:

```bash
cp .env.example .env
```

Edit the `.env` file with your Azure credentials (only these fields are required, others have defaults):

```bash
# Azure AI Configuration
AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=your-deployment-name
```

The `.env.example` file contains all available configuration options with descriptions. For quickstart, only the Azure AI settings above need to be changed.

!!! tip "Getting Azure Credentials"
    Visit [Azure AI Foundry](https://ai.azure.com) to create a project and deploy GPT-4. Copy your project endpoint and model deployment name.

!!! warning "Keep Your .env Secure"
    The `.env` file is already in `.gitignore` to prevent committing secrets. Never commit this file to version control!

### 3. Install Backend Dependencies

```bash
# Install Python dependencies using uv
uv sync
```

### 4. Install Frontend Dependencies

```bash
# Navigate to UI directory
cd apps/ui

# Install npm packages
npm install

# Return to root
cd ../..
```

### 5. Start MCP Servers

Open three terminal windows and start the MCP servers:

**Terminal 1: Application Verification Server**
```bash
uv run python -m loan_avengers.tools.mcp_servers.application_verification.server
```

**Terminal 2: Document Processing Server**
```bash
uv run python -m loan_avengers.tools.mcp_servers.document_processing.server
```

**Terminal 3: Financial Calculations Server**
```bash
uv run python -m loan_avengers.tools.mcp_servers.financial_calculations.server
```

!!! info "MCP Server Ports"
    - Application Verification: `localhost:8010`
    - Document Processing: `localhost:8011`
    - Financial Calculations: `localhost:8012`

### 6. Start the API Server

In a new terminal:

```bash
cd apps/api
uv run python -m loan_avengers.api.app
```

The API will be available at `http://localhost:8000`

!!! success "Environment Variables Auto-Loaded"
    The API automatically loads environment variables from the root `.env` file - no manual exports needed!

### 7. Start the Frontend

In another terminal:

```bash
cd apps/ui
npm run dev
```

The UI will be available at `http://localhost:5173`

!!! note "Frontend Port May Vary"
    Vite automatically assigns available ports. If port 5173 is in use, it will try 5174, 5175, etc. Check the terminal output for the actual port and update `APP_CORS_ORIGINS` in `.env` if needed. See [CORS troubleshooting](../reference/troubleshooting.md#cors-configuration-issues) for details.

## Verify Installation

1. Open your browser to `http://localhost:5173` (or the port shown in your terminal)
2. You should see the Loan Avengers homepage with the AI Dream Team
3. Click "Try the Demo" to start processing a loan application
4. Fill in the sample data and submit
5. Watch as the AI agents process your application in real-time!

!!! warning "Connection Issues?"
    If you see "I'm sorry, I'm having trouble connecting right now", check that your frontend port is included in `APP_CORS_ORIGINS` in `.env`. See [CORS troubleshooting](../reference/troubleshooting.md#cors-configuration-issues).

## What's Next?

- [Process Your First Loan Application](first-loan.md)
- [Understand the Architecture](architecture.md)
- [Explore the Developer Guide](../developer-guide/index.md)

## Troubleshooting

Running into issues? Check the comprehensive [Troubleshooting Guide](../reference/troubleshooting.md) for solutions to common problems:

- **CORS configuration issues** - Connection errors between frontend and API
- **Port already in use** - Resolving port conflicts
- **Environment variables not loading** - Configuration setup problems
- **Azure authentication errors** - Credential and access issues
- **Module not found errors** - Dependency installation problems
- **MCP server connection failures** - Tool server connectivity issues
- **Frontend build errors** - TypeScript and build problems
- **Slow agent response times** - Performance optimization
- **Database or state issues** - Session and data consistency

### Quick Fixes

**Port conflicts:**
```bash
# Check which ports are in use
lsof -i :8000 :8010 :8011 :8012 :5173

# Kill processes if needed
kill -9 <PID>
```

**CORS errors ("I'm sorry, I'm having trouble connecting"):**
```bash
# Add your frontend port to .env
APP_CORS_ORIGINS="http://localhost:5173,http://localhost:5174,http://localhost:5175"

# Restart API server
ps aux | grep "loan_avengers.api.app" | grep -v grep | awk '{print $2}' | xargs kill
cd apps/api && uv run python -m loan_avengers.api.app
```

For detailed solutions, see the full [Troubleshooting Guide](../reference/troubleshooting.md).

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/niksacdev/loan-avengers/issues)
- **Discussions**: [GitHub Discussions](https://github.com/niksacdev/loan-avengers/discussions)
- **Documentation**: You're reading it! 📖
