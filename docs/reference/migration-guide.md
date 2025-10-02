# Repository Restructuring Migration Plan

## Overview

The repository is being restructured from a Python package-centric layout to an apps-based monorepo suitable for multi-container Azure deployment.

## Current Status: ✅ Structure Created, ⏳ Migration In Progress

### Completed ✅
- [x] Created `apps/` directory structure
- [x] Moved UI to `apps/ui/`
- [x] Copied API code to `apps/api/`
- [x] Created `pyproject.toml` for API with uv
- [x] Created Dockerfiles for API and UI
- [x] Created docker-compose.yml for local development
- [x] Created Azure Agent Service config templates
- [x] Created comprehensive README files

### Pending ⏳
- [ ] Remove original `loan_defenders/` directory
- [ ] Update all import paths throughout codebase
- [ ] Update GitHub Actions workflows
- [ ] Update CLAUDE.md and documentation
- [ ] Test all components
- [ ] Update .gitignore for new structure
- [ ] Create ADR documenting this restructuring

## Directory Structure Comparison

### Before (Current)
```
loan-defenders/
├── loan_defenders/        # Python package
│   ├── api/
│   ├── agents/
│   ├── models/
│   ├── tools/
│   ├── utils/
│   └── ui/              # ❌ UI nested in Python package
├── tests/
├── pyproject.toml       # Root-level Python config
└── README.md
```

### After (Target)
```
loan-defenders/
├── apps/                 # ✅ All deployable applications
│   ├── api/             # FastAPI Container App
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── loan_defenders/
│   ├── ui/              # React Container App
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── src/
│   └── agents/          # Azure Agent Service configs
├── tests/
├── docker-compose.yml   # Local development
└── README.md
```

## Migration Steps

### Step 1: Import Path Updates (IN PROGRESS)

All Python imports remain unchanged because the package structure inside `apps/api/` is identical:
- ✅ `from loan_defenders.api.app import app`
- ✅ `from loan_defenders.models.application import LoanApplication`
- ✅ `from loan_defenders.agents.conversation_orchestrator import ConversationOrchestrator`

**Files that need updates:**
- Test files in `tests/` (update sys.path if needed)
- GitHub Actions workflows
- Documentation references

### Step 2: GitHub Actions Updates

Update `.github/workflows/` to:
1. Run API tests from `apps/api/`
2. Build Docker images for both apps
3. Push to Azure Container Registry
4. Deploy to Azure Container Apps

**Files to update:**
- `.github/workflows/test.yml`
- `.github/workflows/build-and-deploy.yml` (if exists)

### Step 3: Documentation Updates

Update references in:
- [ ] `README.md` - Update quick start instructions
- [ ] `CLAUDE.md` - Update directory structure references
- [ ] `docs/` - Update all architectural diagrams
- [ ] `apps/*/README.md` - Already created ✅

### Step 4: Configuration Updates

Update:
- [ ] `.gitignore` - Add apps-specific patterns
- [ ] Root `pyproject.toml` - Either remove or make it a workspace config
- [ ] `.env.example` - Already updated ✅

### Step 5: Remove Old Structure

Once everything is working:
```bash
# Backup first!
mv loan_defenders loan_defenders.backup

# Test everything works

# If successful, remove backup
rm -rf loan_defenders.backup
```

## Testing Plan

### Phase 1: API Tests
```bash
cd apps/api
uv sync
uv run pytest ../../tests/unit/api/ -v
uv run pytest ../../tests/integration/ -v
```

### Phase 2: Local Docker Build
```bash
# Build images
docker build -t loan-defenders-api:test ./apps/api
docker build -t loan-defenders-ui:test ./apps/ui

# Test with docker-compose
docker-compose up
```

### Phase 3: End-to-End Testing
1. Start API: `cd apps/api && uv run uvicorn loan_defenders.api.app:app --reload`
2. Start UI: `cd apps/ui && npm run dev`
3. Test full user flow through UI

## Rollback Plan

If issues arise:
1. Keep original `loan_defenders/` directory intact
2. Original structure still works as-is
3. Can continue development in original structure
4. Complete migration later

## Benefits of New Structure

### For Development
- ✅ Clear separation of concerns
- ✅ Independent deployment of apps
- ✅ Technology-agnostic (API in Python, UI in TypeScript)
- ✅ Better Docker layer caching

### For Deployment
- ✅ Azure Container Apps - one container per app
- ✅ Independent scaling of API and UI
- ✅ Separate CI/CD pipelines
- ✅ Azure Agent Service ready

### For Team Collaboration
- ✅ Clear app boundaries
- ✅ Easier code ownership
- ✅ Reduced merge conflicts
- ✅ Better monorepo practices

## Timeline

- **Day 1**: Structure created ✅ (COMPLETED)
- **Day 2**: Test migration, update imports
- **Day 3**: Update CI/CD, documentation
- **Day 4**: Remove old structure, final testing
- **Day 5**: Deploy to Azure with new structure

## Current Working Commands

### Running Locally (Old Structure - Still Works)
```bash
# API
uv run uvicorn loan_defenders.api.app:app --reload

# UI
cd loan_defenders/ui && npm run dev
```

### Running Locally (New Structure - Testing)
```bash
# API
cd apps/api && uv run uvicorn loan_defenders.api.app:app --reload

# UI
cd apps/ui && npm run dev

# Or use Docker Compose
docker-compose up
```

## Questions & Decisions

### Q: Keep root pyproject.toml?
**Decision**: Keep it for now as workspace config, update later to use uv workspaces

### Q: How to handle tests?
**Decision**: Keep tests in `/tests` but update paths. Consider moving to `/apps/api/tests` later

### Q: Where do docs live?
**Decision**: Keep `/docs` at root since they apply to entire system

### Q: What about scripts/?
**Decision**: Keep at root for now, these are repo-level utilities

## Support

For issues during migration:
1. Check this document
2. Refer to `apps/README.md` for new structure
3. Check GitHub Issues
4. Reach out to team

## ADR Reference

This restructuring will be documented in:
- `docs/decisions/adr-006-monorepo-apps-structure.md` (TODO: Create)

---

**Status**: 🟡 Migration In Progress
**Last Updated**: 2025-10-01
**Next Steps**: Test imports and update paths
