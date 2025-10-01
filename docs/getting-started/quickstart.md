# Quick Start Guide

Get the Loan Avengers system up and running in under 10 minutes!

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed
- **Node.js 18+** and npm
- **uv package manager** ([installation guide](https://docs.astral.sh/uv/))
- **Azure AI Foundry** account with GPT-4 access
- **Git** for version control

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/niksacdev/loan-avengers.git
cd loan-avengers
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Azure AI Foundry Configuration
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=your-gpt4-deployment

# Application Configuration
LOG_LEVEL=INFO
APP_DEBUG=false
APP_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

!!! tip "Getting Azure Credentials"
    Visit [Azure AI Foundry](https://ai.azure.com) to create a project and deploy GPT-4. Copy your project endpoint and model deployment name.

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
uv run uvicorn loan_avengers.api.app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 7. Start the Frontend

In another terminal:

```bash
cd apps/ui
npm run dev
```

The UI will be available at `http://localhost:5173`

## Verify Installation

1. Open your browser to `http://localhost:5173`
2. You should see the Loan Avengers homepage with the AI Dream Team
3. Click "Try the Demo" to start processing a loan application
4. Fill in the sample data and submit
5. Watch as the AI agents process your application in real-time!

## What's Next?

- [Process Your First Loan Application](first-loan.md)
- [Understand the Architecture](architecture.md)
- [Explore the Developer Guide](../developer-guide/index.md)

## Troubleshooting

### Port Already in Use

If you see "port already in use" errors, check for existing processes:

```bash
# Check ports 8000, 8010-8012, 5173
lsof -i :8000
lsof -i :8010
lsof -i :8011
lsof -i :8012
lsof -i :5173

# Kill processes if needed
kill -9 <PID>
```

### Azure Authentication Errors

Ensure your `.env` file has correct Azure credentials:

```bash
# Test Azure connection
uv run python -c "from azure.identity import DefaultAzureCredential; DefaultAzureCredential().get_token('https://cognitiveservices.azure.com/.default')"
```

### Module Not Found Errors

Reinstall dependencies:

```bash
# Backend
uv sync --no-cache

# Frontend
cd apps/ui && npm ci
```

For more troubleshooting tips, see the [Troubleshooting Guide](../reference/troubleshooting.md).

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/niksacdev/loan-avengers/issues)
- **Discussions**: [GitHub Discussions](https://github.com/niksacdev/loan-avengers/discussions)
- **Documentation**: You're reading it! 📖
