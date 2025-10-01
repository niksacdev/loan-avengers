# Loan Avengers API 🦸‍♂️

FastAPI backend for the Loan Avengers multi-agent loan processing system.

## Overview

This API provides endpoints for:
- Conversational loan application collection
- Multi-agent loan processing workflow
- Session management
- Real-time processing updates

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# From apps/api directory
cd apps/api

# Install dependencies with uv
uv sync

# Copy environment template
cp ../../.env.example .env
```

### Running Locally

```bash
# Development server with auto-reload
uv run uvicorn loan_avengers.api.app:app --reload --host 0.0.0.0 --port 8000

# Production server
uv run uvicorn loan_avengers.api.app:app --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, access:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Architecture

### Agent System

The API orchestrates multiple specialized agents:

1. **Coordinator Agent** - Conversational data collection
2. **Intake Validator** - Application validation
3. **Credit Assessor** - Credit analysis
4. **Income Verifier** - Income and employment verification
5. **Risk Analyzer** - Final risk assessment

### Key Components

```
loan_avengers/
├── api/              # FastAPI routes and endpoints
├── agents/           # Agent implementations
│   ├── conversation_orchestrator.py
│   ├── conversation_state_machine.py
│   ├── sequential_pipeline.py
│   └── agent-persona/   # Agent instruction markdown files
├── models/           # Pydantic data models
├── tools/            # MCP servers and business services
└── utils/            # Shared utilities
```

## Configuration

Configuration is managed through environment variables. See `.env.example` for all available options.

### Key Settings

```bash
# API Configuration
APP_TITLE="Loan Avengers API"
APP_DEBUG=false
APP_CORS_ORIGINS="http://localhost:5173,http://localhost:3000"

# Session Management
APP_SESSION_TIMEOUT_HOURS=24

# Azure Deployment (production)
APP_LOG_LEVEL=INFO
```

## Testing

```bash
# Run all tests
uv run pytest ../../tests/ -v

# Run with coverage
uv run pytest ../../tests/ --cov=loan_avengers --cov-report=term-missing

# Run specific test file
uv run pytest ../../tests/unit/api/test_app.py -v
```

## Development

### Code Quality

```bash
# Linting and formatting
uv run ruff check . --fix
uv run ruff format .

# Type checking
uv run mypy loan_avengers
```

### Adding Dependencies

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

## Docker Deployment

### Build Image

```bash
docker build -t loan-avengers-api:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e APP_DEBUG=false \
  -e APP_CORS_ORIGINS="https://your-domain.com" \
  loan-avengers-api:latest
```

## Azure Deployment

This API is designed for deployment to **Azure Container Apps**.

### Prerequisites

- Azure subscription
- Azure Container Registry (ACR)
- Azure Container Apps environment

### Deployment Steps

See [Azure Deployment Guide](../../docs/deployment/azure-container-apps.md) for detailed instructions.

## API Endpoints

### Health Check

```
GET /health
```

Returns service health status and component availability.

### Chat Endpoint

```
POST /api/chat
```

Main conversational endpoint for loan application processing.

**Request:**
```json
{
  "user_message": "I need a loan for $250,000",
  "session_id": "optional-session-id",
  "current_data": {}
}
```

**Response:**
```json
{
  "agent_name": "Coordinator",
  "message": "Great! Let me help you with that...",
  "action": "collect_info",
  "collected_data": {
    "loan_amount": 250000
  },
  "completion_percentage": 20,
  "session_id": "uuid-here"
}
```

### Session Management

```
GET    /api/sessions              # List all sessions
GET    /api/sessions/{id}         # Get session details
DELETE /api/sessions/{id}         # Delete session
POST   /api/sessions/cleanup      # Clean up old sessions
```

## Environment Variables Reference

See `../../.env.example` for complete list of environment variables.

## License

MIT License - see [LICENSE](../../LICENSE) for details.
