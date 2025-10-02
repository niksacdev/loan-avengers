# ADR-010: Monorepo Restructuring with UV Workspace

**Status**: Accepted
**Date**: 2025-10-01
**Deciders**: niksacdev, Claude Code (system-architecture-reviewer)
**Tags**: architecture, deployment, monorepo, infrastructure

## Context

The Loan Defenders application started as a single Python package with mixed API and UI code. As the project grew, we identified several challenges:

1. **Deployment Complexity**: Cannot deploy API and UI independently
2. **Dependency Conflicts**: Shared dependencies between API (Python) and UI (TypeScript)
3. **Build Optimization**: Cannot optimize Docker builds for each component
4. **Scaling Issues**: Cannot scale API and UI separately based on load
5. **Development Experience**: Changes to UI require rebuilding entire project

### User Need
- **Deploy components independently** to different Azure Container Apps
- **Scale services independently** based on traffic patterns
- **Optimize CI/CD** by building only changed components
- **Improve developer experience** with faster iteration cycles

## Decision

We restructure the repository into a **monorepo with independent apps** using the following architecture:

```
loan-defenders/
├── pyproject.toml          # Workspace root (tooling config only)
├── .env                    # Shared environment variables
├── apps/
│   ├── api/                # Python FastAPI backend
│   │   ├── pyproject.toml  # API-specific dependencies
│   │   ├── uv.lock         # API dependency lock
│   │   └── loan_defenders/  # Application code
│   └── ui/                 # TypeScript React frontend
│       ├── package.json    # UI-specific dependencies
│       ├── package-lock.json
│       └── src/
├── tests/                  # Shared test suite
└── docs/
```

### Key Design Decisions

#### 1. UV Workspace Pattern
```toml
# Root pyproject.toml
[tool.uv.workspace]
members = ["apps/api"]

# Shared tooling only (ruff, black, mypy, pytest)
[tool.uv]
dev-dependencies = [...]
```

**Rationale**:
- Workspace allows shared development tools
- Each app manages its own production dependencies
- Lock files stay in app directories for independent deployment

#### 2. Shared .env at Root
```bash
# .env (root level)
AZURE_AI_PROJECT_ENDPOINT=...
AZURE_AI_MODEL_DEPLOYMENT_NAME=...
```

**Rationale**:
- Single source of truth for configuration
- Apps load from `../../.env` using python-dotenv
- Simplifies local development
- Azure Container Apps can override per-service

#### 3. Independent CI/CD
```yaml
# .github/workflows/test-apps.yml
jobs:
  test-api:
    working-directory: apps/api
  test-ui:
    working-directory: apps/ui
```

**Rationale**:
- Test each app independently
- Deploy only changed components
- Faster feedback loops

#### 4. Container-Per-App Deployment
```dockerfile
# apps/api/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY apps/api .
RUN uv sync
```

```dockerfile
# apps/ui/Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY apps/ui .
RUN npm ci && npm run build
```

**Rationale**:
- Each app builds its own optimized container
- No cross-app dependencies in containers
- Smaller image sizes (API ~300MB, UI ~50MB)

## Consequences

### Positive ✅

1. **Independent Deployment**
   - Deploy API without rebuilding UI
   - Deploy UI without restarting API
   - Hotfix one service without affecting others

2. **Independent Scaling**
   - Scale API horizontally based on request load
   - Scale UI based on CDN cache misses
   - Right-size containers per service

3. **Optimized CI/CD**
   - Run only affected tests
   - Build only changed containers
   - Faster merge-to-production time

4. **Better Developer Experience**
   - Frontend devs don't need Python environment
   - Backend devs don't need Node.js
   - Faster local iteration (only rebuild changed app)

5. **Future Extensibility**
   - Easy to add new apps (agents, workers, schedulers)
   - Each app can use different tech stack
   - Shared tooling ensures consistency

### Negative ⚠️

1. **Migration Complexity**
   - One-time cost to restructure existing code
   - Update all import paths
   - Migrate tests to new structure

2. **Coordination Overhead**
   - Breaking API changes require UI updates
   - Need versioning strategy for API contracts
   - Shared types need careful management

3. **Local Development Setup**
   - Developers run multiple services locally
   - Need docker-compose or scripts
   - More complex initial setup

4. **Testing Complexity**
   - Integration tests span multiple apps
   - Need proper test data management
   - E2E tests require all services running

### Mitigations

1. **Migration**: Created comprehensive MIGRATION.md with step-by-step guide
2. **Coordination**: Implement API versioning and OpenAPI contracts
3. **Local Dev**: Created `scripts/dev-all.sh` to start all services
4. **Testing**: Shared `tests/` directory for integration tests

## Implementation

### Phase 1: Restructure (✅ Complete)
- [x] Create `apps/api` and move Python code
- [x] Create `apps/ui` and move React code
- [x] Convert root to UV workspace
- [x] Update import paths
- [x] Move .env to root
- [x] Update documentation

### Phase 2: CI/CD (✅ Complete)
- [x] Create `test-apps.yml` workflow
- [x] Add workspace validation
- [x] Configure Codecov for each app

### Phase 3: Deployment (Pending)
- [ ] Create Azure Container Apps for each service
- [ ] Set up Azure Container Registry
- [ ] Configure deployment pipelines
- [ ] Set up monitoring and observability

## Alternatives Considered

### Alternative 1: Keep Single Package
**Rejected**: Cannot deploy components independently, violates cloud-native principles

### Alternative 2: Separate Repositories
**Rejected**: Loses benefits of shared tooling, harder to maintain consistency, complicates versioning

### Alternative 3: Nx/Turborepo
**Rejected**: Adds complexity, UV workspace sufficient for current needs, can migrate later if needed

## References

- [UV Workspace Documentation](https://docs.astral.sh/uv/concepts/workspaces/)
- [Azure Container Apps Multi-Container](https://learn.microsoft.com/en-us/azure/container-apps/containers)
- [Monorepo Best Practices](https://monorepo.tools/)
- Original Discussion: PR #78
- Migration Guide: `MIGRATION.md`

## Related Decisions

- ADR-003: Instruction File Synchronization (workspace affects all IDEs)
- ADR-005: Orchestration Refactoring (affects agent deployment)
- Future: ADR-011: API Versioning Strategy

---

**Decision Makers**: niksacdev, Claude Code
**Consultation**: system-architecture-reviewer agent (Architecture Grade: 7.9/10)
**Implementation**: PR #78 - Complete Monorepo Restructuring
