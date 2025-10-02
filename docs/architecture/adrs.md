# Architecture Decision Records (ADRs)

This page catalogs all architectural decisions made during the development of the Loan Defenders system.

## What are ADRs?

Architecture Decision Records document significant architectural choices, their context, and consequences. They help maintain institutional knowledge and provide rationale for future developers.

## All ADRs

### Strategic Foundation
- [ADR-001: Multi-Agent Strategic Foundation](decisions/adr-001-multi-agent-strategic-foundation.md)
- [ADR-002: Business Logic First Approach](decisions/adr-002-business-logic-first-approach.md)
- [ADR-003: Configuration Separation](decisions/adr-003-configuration-separation.md)
- [ADR-004: Personality-Driven Agent Architecture](decisions/adr-004-personality-driven-agent-architecture.md)

### API & Orchestration
- [ADR-005: API Architecture with Agent Framework](decisions/adr-005-api-architecture-with-agent-framework.md)
- [ADR-006: Sequential Workflow Orchestration](decisions/adr-006-sequential-workflow-orchestration.md)
- [ADR-007: Conversation State with Agent Thread](decisions/adr-007-conversation-state-with-agent-thread.md)
- [ADR-011: Two-Endpoint API Architecture](decisions/adr-011-two-endpoint-api-architecture.md)
- [ADR-013: Orchestration Refactoring](decisions/adr-013-orchestration-refactoring.md)

### Infrastructure
- [ADR-008: Streamable HTTP Transport](decisions/adr-008-streamable-http-transport.md)
- [ADR-009: Azure Container Apps Deployment](decisions/adr-009-azure-container-apps-deployment.md)
- [ADR-010: Monorepo Restructuring](decisions/adr-010-monorepo-restructuring.md)
- [ADR-012: Observability Implementation](decisions/adr-012-observability-implementation.md)

### Assessments
- [ADR-014: Unified Workflow Architecture Assessment](decisions/adr-014-unified-workflow-architecture-assessment.md)

## ADR Categories

### 🏗️ Strategic Foundation
Foundational architectural decisions that shape the entire system.

### 🔌 API & Orchestration
Decisions about how agents communicate and coordinate workflows.

### ☁️ Infrastructure
Deployment, hosting, and operational infrastructure choices.

### 📊 Assessments
Retrospective evaluations of architectural approaches.

## Creating New ADRs

When making significant architectural decisions:

1. Copy the ADR template from `docs/architecture/decisions/adr-template.md`
2. Number sequentially (ADR-XXX)
3. Include: Status, Context, Decision, Consequences, Implementation
4. Commit with descriptive message
5. Update this index page

## Recent ADRs

The most recent architectural decisions:

1. **ADR-014**: Unified Workflow Architecture Assessment (2025-09-29)
2. **ADR-013**: Orchestration Refactoring (2025-09-30)
3. **ADR-012**: Observability Implementation (2025-09-30)
4. **ADR-011**: Two-Endpoint API Architecture (2025-09-29)
5. **ADR-010**: Monorepo Restructuring (2025-09-28)

## Related Documentation

- [System Architecture Overview](system-architecture.md)
- [Agent Framework Integration](agent-framework.md)
- [Orchestration Patterns](orchestration.md)
