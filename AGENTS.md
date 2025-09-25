# Multi-Agent Loan Processing System - Universal AI Agent Guide

> **🤖 Universal AI Agent Instructions**: This file provides AI agent guidance in a universal format compatible with any AI development tool or IDE.

## Project Overview

This is a **Multi-Agent Loan Processing System** demonstration using **Microsoft Agent Framework** with 5 specialized autonomous agents that process loan applications through a coordinated workflow from intake to final decision.

### System Architecture
```
Loan Application → [Intake Agent] → [Credit Agent] → [Income Agent] → [Risk Agent] → [Orchestrator] → Loan Decision
                                          ↓
                               [MCP Tool Servers: Verification, Documents, Calculations]
```

## AI Agent Quick Reference

### Available Agent Personas
- **Intake Agent**: Fast data completeness check and routing (`loan_processing/agents/agent-persona/intake-agent-persona.md`)
- **Credit Agent**: Credit risk assessment and scoring (`loan_processing/agents/agent-persona/credit-agent-persona.md`)
- **Income Agent**: Income and employment verification (`loan_processing/agents/agent-persona/income-agent-persona.md`)
- **Risk Agent**: Final decision synthesis and recommendations (`loan_processing/agents/agent-persona/risk-agent-persona.md`)
- **Orchestrator Agent**: Workflow coordination and context management (`loan_processing/agents/agent-persona/orchestrator-agent-persona.md`)

### MCP Tool Servers
- **Application Verification** (Port 8010): Identity verification, employment checks, credit reports
- **Document Processing** (Port 8011): OCR, document classification, data extraction
- **Financial Calculations** (Port 8012): DTI calculations, affordability analysis, risk scoring

### Data Models (Pydantic v2)
- **LoanApplication**: Complete loan application with automatic validation
- **Assessment Models**: CreditAssessment, IncomeAssessment, RiskAssessment
- **LoanDecision**: Final decision with reasoning and audit trail

## Universal AI Agent Integration Patterns

### Pattern 1: Load Agent Persona
```python
# Load specialized agent instructions from markdown files
from pathlib import Path
persona_path = Path("loan_processing/agents/agent-persona/credit-agent-persona.md")
persona_content = persona_path.read_text()

# Use persona_content as system prompt for any AI framework
```

### Pattern 2: Use Business Models
```python
# Import type-safe business models for validation
from loan_processing.models import LoanApplication, LoanDecision
from decimal import Decimal
from datetime import datetime

# Create validated loan application
application = LoanApplication(
    application_id="LN1234567890",
    applicant_name="John Doe",
    loan_amount=Decimal("250000.00"),
    annual_income=Decimal("80000.00")
    # ... other validated fields
)
```

### Pattern 3: Access Configuration
```python
# Load agent and MCP server configuration
import yaml
from pathlib import Path

config_path = Path("loan_processing/config/agents.yaml")
config = yaml.safe_load(config_path.read_text())

# Use config to set up agent-tool mappings
```

## Key Development Principles

### 1. Agent Autonomy
- Each agent decides which MCP tools to use based on their assessment needs
- Agent instructions are loaded from persona markdown files
- No hardcoded business logic in orchestrator code
- Agents designed around customer jobs-to-be-done, not internal processes

### 2. Token Optimization (CRITICAL for Performance)
- Keep agent personas under 500 lines for 75% token reduction and 10x speed improvement
- Focus on WHAT agents should do, not verbose HOW explanations
- Reference external documentation instead of inline explanations
- Use file references instead of embedded code examples

### 3. Microsoft Agent Framework Integration
```python
# Example: Create agent with persona loading
from microsoft_agent_framework import ChatClientAgent

# Load agent persona
persona = open("loan_processing/agents/agent-persona/credit-agent-persona.md").read()

# Create Microsoft Agent Framework agent
agent = ChatClientAgent(
    name="Credit Assessment Agent",
    instructions=persona
)

# Process loan application
result = await agent.run(application.model_dump())
```

### 4. Sequential Workflow Processing
- **Intake → Credit → Income → Risk → Orchestrator**: Required processing order
- Each agent processes LoanApplication and produces typed assessments
- Context and results passed between agents in the workflow
- Final orchestrator produces LoanDecision with complete audit trail

## Security & Compliance Requirements

### Critical Security Rules
1. **NEVER use SSN** in tool calls - always use `applicant_id` (UUID)
2. **Secure all PII** - encrypt sensitive data in transit and at rest
3. **Maintain audit logging** - track all agent decisions for regulatory compliance
4. **Access control** - limit MCP server access to authorized agents only

### Fair Lending Compliance
- Implement bias prevention in all agent assessments
- Maintain audit trails for regulatory review
- Document decision rationale for transparency
- Regular bias testing and model validation

## Quality Standards

### Pre-Commit Validation (Required)
```bash
# Use uv package manager for all operations (never pip, poetry, conda)
uv run ruff check . --fix          # Auto-fix linting issues
uv run ruff format .               # Auto-format code
uv run pytest tests/ -v --cov=loan_processing  # Run tests with coverage
uv run python scripts/validate_ci_fix.py       # Quick validation script

# Coverage requirement: ≥85% on core loan processing modules
```

### Performance Standards
- Agent personas optimized to <500 lines each for token efficiency
- MCP server response times monitored and optimized
- Complete loan workflow processing within acceptable timeframes
- Memory usage optimized for production deployment

## File Structure Reference

```
loan_processing/
├── models/                  # Pydantic v2 business data models
├── agents/agent-persona/    # Agent instruction markdown files
├── tools/mcp_servers/       # MCP server implementations
├── config/agents.yaml       # Agent and MCP server configuration
└── utils/                   # Shared business logic utilities
```

## Documentation for AI Agents

### Business Context
- **[Business Context](docs/product/business-context.md)**: Domain overview and system context
- **[Business Case](docs/product/business-case.md)**: ROI analysis and financial justification
- **[User Personas](docs/ux/user-personas.md)**: Target users and success metrics

### Technical Architecture
- **[Agent Strategy](docs/agent-strategy.md)**: Multi-agent architecture approach
- **[Agent Patterns](docs/agent-patterns.md)**: Integration patterns and examples
- **[Data Models](docs/data-models.md)**: Business entity specifications
- **[Architecture Decisions](docs/decisions/)**: ADRs documenting key technical choices

## Common AI Agent Tasks

### 1. Implement New Agent
```python
# 1. Create agent persona markdown file
# 2. Add configuration in agents.yaml
# 3. Load persona into your AI framework
# 4. Test with sample loan applications
```

### 2. Modify Agent Behavior
- Update persona files in `loan_processing/agents/agent-persona/`
- Keep personas focused and under 500 lines
- Test with demo applications to verify behavior
- Maintain regulatory compliance requirements

### 3. Add MCP Server Integration
- Agents select tools autonomously based on persona instructions
- Configure MCP servers in `agents.yaml` for each agent type
- Ensure secure parameter usage (applicant_id, not SSN)
- Test tool integration with agent workflows

### 4. Process Loan Application Workflow
```python
# Complete multi-agent processing example
# 1. Load all agent personas
# 2. Create agents with your AI framework
# 3. Process through sequential workflow
# 4. Generate final LoanDecision with audit trail
```

## AI Framework Compatibility

This system is designed to work with multiple AI frameworks:

- ✅ **Microsoft Agent Framework** (primary, demonstrated)
- ✅ **OpenAI Assistants API** (persona as system messages)
- ✅ **LangChain Multi-Agent** (persona as agent instructions)
- ✅ **Custom Agent Frameworks** (persona as prompts)

### Adaptation Notes
- Agent personas are framework-agnostic markdown instructions
- MCP servers provide standardized tool interfaces
- Pydantic models ensure type safety across frameworks
- Business logic isolated in utils/ for reusability

## Getting Started with Any AI Tool

1. **Load Agent Personas**: Use markdown files as system prompts/instructions
2. **Import Data Models**: Use Pydantic models for type-safe data handling
3. **Configure Tools**: Set up MCP servers as external tool integrations
4. **Test Workflow**: Process sample loan applications through 5-agent sequence
5. **Customize**: Modify agent personas and business logic as needed

---

**Goal**: Provide universal AI agent guidance for building multi-agent loan processing systems with any AI development tool or framework.