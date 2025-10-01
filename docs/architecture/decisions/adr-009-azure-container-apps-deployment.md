# ADR-009: Azure Container Apps Deployment

**Status**: Accepted
**Date**: 2025-09-28

**Decision**: Deploy API on Azure Container Apps with auto-scaling and managed identity.

**Context**:
Need cloud-native, serverless deployment on Azure with auto-scaling and seamless integration with Azure services.

**Decision**:
- Azure Container Apps for API hosting
- Azure Cache for Redis for AgentThread state
- Azure Blob Storage for documents
- Cosmos DB for completed applications
- Azure Key Vault for secrets
- Entra ID (Managed Identity) for authentication

**Consequences**:
*Positive*: Serverless, auto-scaling, native Azure integration, cost-effective
*Negative*: Azure-specific (not multi-cloud)

**Related**: ADR-005
