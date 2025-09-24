# Multi-Agent Loan Processing System Architecture

**Framework:** Microsoft Agent Framework
**Version:** 2.0
**Date:** 2024-09-24
**Status:** Active Development

## Executive Summary

This document consolidates the architectural decisions from ADR-002, ADR-005, ADR-007, and ADR-015 into a comprehensive architecture guide for the multi-agent loan processing system using Microsoft Agent Framework.

The system implements a strategic multi-agent architecture designed for **progressive autonomy** and future extensibility, transitioning from OpenAI Agent SDK to Microsoft Agent Framework while preserving business logic and data models.

## Core Architecture Principles

### 1. Multi-Agent Strategic Foundation (ADR-015)
- **Decision**: Keep multi-agent architecture as strategic foundation
- **Rationale**: Investment in progressive enhancement without refactoring
- **Key Benefits**:
  - Agents gain intelligence as MCP servers expand (current: 3 → planned: 20+)
  - Independent team evolution without coordination
  - Clean integration points for new capabilities
  - Regulatory compliance with audit trails

### 2. Agent Base Architecture (ADR-002)
- **Framework**: Microsoft Agent Framework ChatClientAgent patterns
- **Pattern**: Abstract Base Class with Framework Composition
- **Components**:
  - `LoanProcessingAgent` base class
  - Composed ChatClientAgent internally
  - Standardized tool initialization and response parsing
  - Development-friendly placeholder implementations

### 3. Configuration-Driven Orchestration (ADR-005)
- **Problem Solved**: Eliminated hardcoded agent handoffs and circular dependencies
- **Solution**: Externalized workflow logic to YAML configuration
- **Architecture**:
  - **AgentRegistry**: Centralized agent factory without handoffs
  - **OrchestrationEngine**: Dynamic pattern execution
  - **Pattern Files**: YAML-based workflow definitions (sequential, parallel, collaborative)

### 4. Layered Configuration System (ADR-007)
- **Pattern**: Dependency injection with multiple providers
- **Components**:
  - **ConfigurationService**: Abstract provider interface
  - **DependencyContainer**: Application dependency management
  - **Multi-Provider Support**: OpenAI, Azure OpenAI, Microsoft Agent Framework
  - **Environment-Specific**: Development, staging, production configurations

## System Architecture

### High-Level Component View
```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │ Console App     │  │      Web API (Future)           │  │
│  │                 │  │                                  │  │
│  └─────────────────┘  └──────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                 Orchestration Engine                        │
│  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │ Pattern Loader  │  │    Agent Registry                │  │
│  │ (YAML Based)    │  │    (Framework Agnostic)          │  │
│  └─────────────────┘  └──────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Agent Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  Intake Agent   │  │  Credit Agent   │  │ Risk Agent  │  │
│  │                 │  │                 │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Income Agent    │  │ Future Agents   │                   │
│  │                 │  │                 │                   │
│  └─────────────────┘  └─────────────────┘                   │
├─────────────────────────────────────────────────────────────┤
│                      Tool Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ MCP Server 1    │  │ MCP Server 2    │  │ MCP Server  │  │
│  │ App Verification│  │ Document Proc   │  │ Financial   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Business Services                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Financial Calc  │  │ App Verification│  │ Document    │  │
│  │ Service         │  │ Service         │  │ Processing  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Data Models                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ LoanApplication │  │ Assessment      │  │ LoanDecision│  │
│  │                 │  │ Models          │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
loan_processing/
├── agents/
│   ├── base.py                      # Base agent class (Microsoft Agent Framework)
│   ├── registry.py                  # Agent factory and registry
│   ├── specialized/                 # Specialized agent implementations
│   │   ├── intake_agent.py
│   │   ├── credit_agent.py
│   │   ├── income_agent.py
│   │   └── risk_agent.py
│   └── personas/                    # Agent instruction files
│       ├── intake.md
│       ├── credit.md
│       ├── income.md
│       └── risk.md
├── orchestration/
│   ├── engine.py                    # Orchestration engine
│   ├── context.py                   # Shared context management
│   └── patterns/                    # YAML workflow patterns
│       ├── sequential.yaml
│       ├── parallel.yaml
│       └── collaborative.yaml
├── models/                          # Core business models
│   ├── application.py               # Loan application model
│   ├── assessment.py                # Assessment result models
│   └── decision.py                  # Decision outcome models
├── tools/
│   ├── mcp_servers/                 # MCP server implementations
│   │   ├── application_verification/
│   │   ├── document_processing/
│   │   └── financial_calculations/
│   └── services/                    # Business service interfaces
│       ├── financial_calculations.py
│       ├── application_verification.py
│       └── document_processing.py
├── config/
│   ├── agents.yaml                  # Agent configurations
│   ├── settings.py                  # System settings
│   └── app_config.yaml             # Application configuration
└── utils/                           # Shared utilities
    ├── config_loader.py
    ├── logger.py
    ├── correlation.py
    └── safe_evaluator.py
```

## Key Components

### 1. Agent Registry Pattern
**Purpose**: Create workflow-agnostic agents without hardcoded dependencies

```python
class AgentRegistry:
    @classmethod
    def create_agent(cls, agent_type: str, model: str | None = None) -> ChatClientAgent:
        """Create agent instance using Microsoft Agent Framework"""
```

**Capabilities**:
- Framework-agnostic agent creation
- MCP server configuration management
- Structured output format definition
- Persona loading and enhancement

### 2. Orchestration Engine
**Purpose**: Execute different workflow patterns dynamically

```python
class OrchestrationEngine:
    async def execute_pattern(
        self,
        pattern_name: str,
        application: LoanApplication,
        model: str | None = None
    ) -> LoanDecision:
```

**Supported Patterns**:
- **Sequential**: Agents execute in order with context passing
- **Parallel**: Agents execute simultaneously with result merging
- **Collaborative**: Future pattern for agent-to-agent communication

### 3. Business Data Models
**Preserved Components**:
- `LoanApplication`: Immutable application data with validation
- `CreditAssessment`, `IncomeVerification`, `RiskAssessment`: Structured assessment results
- `LoanDecision`: Final decision with audit trail
- `ComprehensiveAssessment`: Aggregated assessment state

### 4. MCP Server Integration
**Tool Architecture**:
- **Application Verification**: Identity, employment, credit verification
- **Document Processing**: OCR, classification, data extraction
- **Financial Calculations**: DTI, affordability, risk scoring

### 5. Configuration System
**Multi-Layer Configuration**:
- Environment variables (highest priority)
- Configuration files (YAML, JSON, .env)
- Default values (fallback)

**Provider Support**:
- Microsoft Agent Framework (primary)
- OpenAI (compatibility)
- Azure OpenAI (enterprise)

## Agent Specializations

### Intake Agent
- **Purpose**: Data completeness and routing
- **MCP Tools**: None (fast triage)
- **Output**: Validation status, routing decision

### Credit Agent
- **Purpose**: Credit risk assessment
- **MCP Tools**: Application verification, financial calculations, document processing
- **Output**: Credit score, risk category, payment history analysis

### Income Agent
- **Purpose**: Income and employment verification
- **MCP Tools**: Application verification, document processing, financial calculations
- **Output**: Verified income, employment status, stability score

### Risk Agent
- **Purpose**: Final decision synthesis
- **MCP Tools**: All available tools
- **Output**: Final recommendation, approved terms, conditions

## Migration Strategy

### Phase 1: Foundation Migration ✅
- Preserve business logic and data models
- Create consolidated architecture document
- Remove OpenAI SDK dependencies
- Clean up legacy code and tests

### Phase 2: Microsoft Agent Framework Integration
- Implement `LoanProcessingAgent` base class
- Create specialized agent implementations
- Integrate with Microsoft Agent Framework ChatClientAgent
- Update orchestration engine for new framework

### Phase 3: Enhanced Capabilities
- Add parallel orchestration pattern
- Implement collaborative agent communication
- Expand MCP server ecosystem (target: 20+ servers)
- Add machine learning integration

### Phase 4: Enterprise Features
- Multi-tenant support
- Advanced monitoring and observability
- Compliance automation
- Performance optimization

## Quality Standards

### Pre-Commit Requirements
- **Linting**: Clean code standards
- **Testing**: Unit and integration tests
- **Coverage**: ≥85% on core modules
- **Type Safety**: Full type annotations

### Monitoring and Observability
- **Audit Trails**: Complete decision tracking
- **Performance Metrics**: Agent execution times
- **Error Tracking**: Structured error handling
- **Compliance Reporting**: Regulatory audit support

## Future Extensibility

### Planned Enhancements
- **Agent Intelligence**: ML-based decision making
- **Dynamic Routing**: Context-aware agent selection
- **Real-time Processing**: Stream-based loan processing
- **Multi-Modal Agents**: Document, voice, and data processing
- **Fraud Detection**: Specialized fraud analysis agents
- **Regulatory Agents**: Compliance-specific assessment agents

### Scalability Considerations
- **Horizontal Scaling**: Agent pool management
- **Caching Layer**: Reduce repeated MCP calls
- **Load Balancing**: Distribute agent workloads
- **Microservices**: Split into specialized services

## Risk Mitigation

### Technical Risks
- **Framework Migration**: Gradual transition with compatibility layers
- **Performance**: Agent pool management and caching
- **Complexity**: Clear separation of concerns and documentation

### Business Risks
- **Regulatory Compliance**: Built-in audit trails and decision transparency
- **Data Security**: Secure parameter handling (applicant_id vs SSN)
- **Decision Quality**: Comprehensive testing and validation

## References

- ADR-002: Agent Base Architecture
- ADR-005: Configuration-Driven Orchestration
- ADR-007: Configuration System Architecture
- ADR-015: Multi-Agent vs Single Orchestrator Choice
- Microsoft Agent Framework Documentation
- MCP (Model Context Protocol) Specification

---
**Document Status**: Living document - updated as architecture evolves
**Next Review**: After Microsoft Agent Framework integration completion