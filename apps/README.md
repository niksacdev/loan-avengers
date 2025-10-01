# Loan Avengers - Apps Directory

This directory contains all deployable applications in the Loan Avengers monorepo.

## Directory Structure

```
apps/
├── api/              # FastAPI backend (Python)
├── ui/               # React/TypeScript frontend
└── agents/           # Azure Agent Service configurations
```

## Applications

### API (`apps/api/`)

**Technology**: Python 3.11+ with FastAPI
**Package Manager**: uv
**Deployment**: Azure Container Apps

FastAPI backend that orchestrates the multi-agent loan processing system.

**Quick Start:**
```bash
cd apps/api
uv sync
uv run uvicorn loan_avengers.api.app:app --reload
```

See [apps/api/README.md](api/README.md) for detailed documentation.

### UI (`apps/ui/`)

**Technology**: React 18+ with TypeScript + Vite
**Package Manager**: npm
**Deployment**: Azure Container Apps (nginx)

React-based user interface for loan application submission and processing.

**Quick Start:**
```bash
cd apps/ui
npm install
npm run dev
```

See [apps/ui/README.md](ui/README.md) for detailed documentation.

### Agents (`apps/agents/`)

**Purpose**: Azure Agent Service deployment configurations
**Note**: This is NOT agent implementation code

Contains YAML manifests and deployment settings for Azure Agent Service. The actual agent code lives in `apps/api/loan_avengers/agents/`.

See [apps/agents/README.md](agents/README.md) for detailed documentation.

## Development Workflows

### Local Development

**Option 1: Run services individually**
```bash
# Terminal 1: API
cd apps/api && uv run uvicorn loan_avengers.api.app:app --reload

# Terminal 2: UI
cd apps/ui && npm run dev
```

**Option 2: Use Docker Compose**
```bash
# From repository root
docker-compose up

# Or run specific services
docker-compose up api
docker-compose up ui
```

### Building Docker Images

```bash
# Build API image
docker build -t loan-avengers-api:latest ./apps/api

# Build UI image
docker build -t loan-avengers-ui:latest ./apps/ui
```

### Running Tests

```bash
# API tests (from root)
uv run pytest tests/ -v

# UI tests
cd apps/ui && npm test
```

## Deployment

Each app has its own Dockerfile and can be deployed independently:

- **API**: Azure Container Apps (FastAPI + uvicorn)
- **UI**: Azure Container Apps (nginx serving static assets)
- **Agents**: Azure Agent Service (managed agent orchestration)

See deployment guides:
- [API Deployment](api/README.md#azure-deployment)
- [UI Deployment](ui/README.md)
- [Azure Architecture](../docs/diagrams/azure-deployment-architecture.md)

## Package Management

### API (Python)
- **Tool**: [uv](https://github.com/astral-sh/uv)
- **Config**: `apps/api/pyproject.toml`
- **Lock**: `apps/api/uv.lock`

### UI (TypeScript)
- **Tool**: npm
- **Config**: `apps/ui/package.json`
- **Lock**: `apps/ui/package-lock.json`

## Shared Resources

Resources shared across apps are located in the repository root:

- `/docs` - Documentation
- `/tests` - Test suites (primarily for API)
- `/.env.example` - Environment variable template
- `/docker-compose.yml` - Local development orchestration

## CI/CD

GitHub Actions workflows are configured to:
1. Test each app independently
2. Build Docker images
3. Push to Azure Container Registry
4. Deploy to Azure Container Apps

See `.github/workflows/` for pipeline definitions.

## Architecture Principles

This monorepo follows these principles:

1. **Independent Deployability** - Each app can be deployed separately
2. **Technology Freedom** - Apps can use different tech stacks
3. **Clear Boundaries** - Well-defined interfaces between apps
4. **Shared Configuration** - Common settings in root `.env`
5. **Isolated Dependencies** - Each app manages its own packages

## Related Documentation

- [Project README](../README.md)
- [Development Guidelines](../CLAUDE.md)
- [Architecture Decisions](../docs/decisions/)
- [System Architecture](../docs/diagrams/system-architecture-diagram.md)
