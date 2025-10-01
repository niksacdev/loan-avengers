# ADR-009: Azure Container Apps Deployment Strategy

**Status**: Accepted
**Date**: 2025-09-28 (Updated: 2025-10-01)

## Context

Need cloud-native, serverless deployment on Azure with auto-scaling and seamless integration with Azure services. Additionally, before public release, we need to ensure proper CI/CD security and deployment safeguards are in place.

## Decision

### Infrastructure Components

- **Azure Container Apps** for API hosting (serverless, auto-scaling)
- **Azure Cache for Redis** for AgentThread state management
- **Azure Blob Storage** for document storage
- **Cosmos DB** for completed applications persistence
- **Azure Key Vault** for secrets management
- **Entra ID (Managed Identity)** for authentication

### Pre-Deployment Requirements

Before deploying to production:

1. **Security Configuration** (see ADR-017):
   - All secrets in Azure Key Vault
   - CORS origins restricted to production domains
   - Debug mode disabled (`APP_DEBUG=false`)
   - HTTPS enforced (automatic with Azure Container Apps)
   - Azure Managed Identity configured
   - Application Insights for security monitoring
   - Session timeout configured
   - Input validation on all endpoints
   - Rate limiting enabled
   - Security headers (CSP, HSTS, X-Frame-Options)

2. **Branch Protection** (see ADR-015):
   - Main branch protected with required approvals
   - All CI/CD checks must pass before merge
   - CODEOWNERS configured for workflow files
   - No direct pushes to main

3. **GitHub Actions Security** (see ADR-016):
   - All workflows follow security best practices
   - Secrets properly configured
   - Dependabot enabled for dependency updates
   - CodeQL scanning enabled

### Deployment Process

1. **Build**: GitHub Actions builds Docker image
2. **Test**: Automated tests run in CI/CD
3. **Security Scan**: Container scanned for vulnerabilities
4. **Deploy**: Push to Azure Container Registry
5. **Release**: Container Apps pulls and deploys
6. **Monitor**: Application Insights tracks performance

## Consequences

### Positive
- **Serverless**: No infrastructure management required
- **Auto-scaling**: Scales based on demand (0 to N instances)
- **Native Azure Integration**: Managed Identity, Key Vault, etc.
- **Cost-effective**: Pay only for usage
- **Secure**: Multiple layers of security protection
- **CI/CD Automated**: GitHub Actions handles build and deploy

### Negative
- **Azure-specific**: Not multi-cloud portable
- **Cold start**: Initial request may have latency
- **Azure dependency**: Requires Azure subscription
- **Learning curve**: Azure-specific services and concepts

### Mitigation
- Use Azure credits for initial deployment
- Document all Azure-specific configurations
- Consider multi-cloud support in future if needed
- Pre-warm containers for production use

## Implementation

### Phase 1: Infrastructure Setup
1. Create Azure resources (Container Apps, Redis, Key Vault, etc.)
2. Configure Managed Identity
3. Set up Application Insights

### Phase 2: Security Hardening
1. Complete all pre-deployment security requirements
2. Configure branch protection (ADR-015)
3. Fix GitHub Actions security issues (ADR-016)
4. Enable all security features (ADR-017)

### Phase 3: Deployment Pipeline
1. Configure GitHub Actions for Azure deployment
2. Set up Container Registry
3. Implement deployment workflow
4. Test with staging environment

### Phase 4: Go Live
1. Verify all security checks pass
2. Deploy to production
3. Monitor for issues
4. Make repository public (if applicable)

## References
- ADR-015: Branch Protection Strategy
- ADR-016: GitHub Actions Security Standards
- ADR-017: Public Release Readiness Standards
- ADR-005: API Architecture with Agent Framework
- Azure Container Apps Documentation
- Azure Deployment Guide: `docs/deployment/azure-deployment.md`
- Security Checklist: `docs/deployment/deployment-checklist.md`

## Related ADRs
- ADR-005: API Architecture with Agent Framework
- ADR-015: Branch Protection Strategy (pre-deployment requirement)
- ADR-016: GitHub Actions Security (CI/CD requirement)
- ADR-017: Public Release Readiness (overall standards)

---

**Last Updated**: 2025-10-01
**Author**: Original decision 2025-09-28, Security additions 2025-10-01
