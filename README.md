# Multi-Agent Loan Processing System

A demonstration of building a multi-agent loan processing system using **Microsoft Agent Framework**. This system processes loan applications from intake to final decision using specialized AI agents working together through a coordinated workflow.

## 🎯 System Overview

This repository demonstrates a **production-ready multi-agent loan processing system** that:

- 🤖 **5 Specialized Agents**: Each agent handles specific loan processing expertise (intake, credit, income, risk, orchestration)
- 🔧 **MCP Tool Integration**: 3 external tool servers for real-world data verification and calculations
- ⚡ **End-to-End Workflow**: Complete loan application processing from start to final decision
- 📊 **Structured Data Models**: Type-safe loan processing with Pydantic validation
- 🏗️ **Microsoft Agent Framework Ready**: Direct integration patterns and examples

**System Workflow:**
```
Loan Application → [Intake Agent] → [Credit Agent] → [Income Agent] → [Risk Agent] → [Orchestrator] → Loan Decision
                                          ↓
                               [MCP Tool Servers: Verification, Documents, Calculations]
```

## 🏗️ Architecture

### Simple, Clean Structure
```
loan_processing/
├── models/                  # Business data models with Pydantic validation
│   ├── application.py       # LoanApplication model
│   ├── assessment.py        # Assessment result models
│   └── decision.py          # LoanDecision model
├── agents/
│   └── agent-persona/       # Agent instruction files (markdown)
│       ├── intake-agent-persona.md
│       ├── credit-agent-persona.md
│       ├── income-agent-persona.md
│       ├── risk-agent-persona.md
│       └── orchestrator-agent-persona.md
├── tools/
│   ├── mcp_servers/         # MCP server implementations
│   │   ├── application_verification/
│   │   ├── document_processing/
│   │   └── financial_calculations/
│   └── services/            # Business service interfaces
├── config/
│   └── agents.yaml          # Simple agent and MCP server configuration
└── utils/                   # Shared utilities
```

## 🚀 Microsoft Agent Framework Integration

### Quick Start Example
```python
from microsoft_agent_framework import ChatClientAgent
from loan_processing.agents import get_persona_path
from loan_processing.models import LoanApplication

# 1. Load specialized agent persona
credit_persona = open(get_persona_path("credit")).read()

# 2. Create Microsoft Agent Framework agent
credit_agent = ChatClientAgent(
    name="Credit Assessment Agent",
    instructions=credit_persona,
    # MCP tools will be configured based on agents.yaml
)

# 3. Process loan application
application = LoanApplication(
    application_id="LN1234567890",
    applicant_name="John Doe",
    email="john.doe@example.com",
    phone="+15551234567",
    loan_amount=250000.00,
    annual_income=80000.00,
    # ... other validated fields
)

# 4. Get agent assessment
result = await credit_agent.run(application.model_dump())
```

### Multi-Agent Orchestration Pattern
```python
# Load all 5 agents for complete loan processing
agents = {}
for agent_type in ['intake', 'credit', 'income', 'risk', 'orchestrator']:
    persona = open(get_persona_path(agent_type)).read()
    agents[agent_type] = ChatClientAgent(
        name=f"{agent_type.title()} Agent",
        instructions=persona
    )

# Process through the workflow
intake_result = await agents['intake'].run(application.model_dump())
credit_result = await agents['credit'].run(application.model_dump())
# ... continue workflow through all agents
```

## 🤖 Available Agent Personas

### Intake Agent (`intake-agent-persona.md`)
- **Purpose**: Fast data completeness check and routing assignment
- **Tools**: None (pure data validation)
- **Output**: Validation status, routing decision

### Credit Agent (`credit-agent-persona.md`)
- **Purpose**: Credit risk assessment and scoring
- **Tools**: Application verification, financial calculations, document processing
- **Output**: Credit scores, risk categories, red flags

### Income Agent (`income-agent-persona.md`)
- **Purpose**: Income and employment verification
- **Tools**: Application verification, document processing, financial calculations
- **Output**: Verified income, employment status, stability scores

### Risk Agent (`risk-agent-persona.md`)
- **Purpose**: Final decision synthesis and recommendations
- **Tools**: All available tools
- **Output**: Final recommendation, approved terms, conditions

### Orchestrator Agent (`orchestrator-agent-persona.md`)
- **Purpose**: Workflow coordination and context management
- **Tools**: None (pure coordination)
- **Output**: Workflow status, agent handoffs

## 🛠️ MCP Tool Integration

The system includes three MCP servers for external tool integration:

### Application Verification Server
- **Port**: 8010
- **Tools**: Identity verification, employment checks, credit reports
- **Usage**: Background data validation

### Document Processing Server
- **Port**: 8011
- **Tools**: OCR, document classification, data extraction
- **Usage**: Process uploaded documents and forms

### Financial Calculations Server
- **Port**: 8012
- **Tools**: DTI calculations, affordability analysis, risk scoring
- **Usage**: Mathematical loan processing operations

## 📊 Data Models & Business Logic

### Core Data Models
The system uses **Pydantic v2** for type-safe data validation:

- **`LoanApplication`**: Complete loan application with automatic validation
- **`CreditAssessment`**: Credit analysis results from Credit Agent
- **`IncomeAssessment`**: Income verification from Income Agent
- **`RiskAssessment`**: Risk analysis from Risk Agent
- **`LoanDecision`**: Final decision with reasoning and audit trail

### Built-in Validation & Calculations
```python
from loan_processing.models import LoanApplication

# Automatic validation and calculations
application = LoanApplication(
    application_id="LN1234567890",
    applicant_name="Jane Smith",
    annual_income=75000.00,
    loan_amount=300000.00,
    existing_debt=2500.00,
    # ... other fields
)

# Built-in business calculations
print(f"Debt-to-Income Ratio: {application.debt_to_income_ratio:.2f}")
print(f"Loan-to-Income Ratio: {application.loan_to_income_ratio:.2f}")
```

## 🧪 Development & Testing

### Running MCP Servers
```bash
# Start application verification server
python -m loan_processing.tools.mcp_servers.application_verification.server

# Start document processing server
python -m loan_processing.tools.mcp_servers.document_processing.server

# Start financial calculations server
python -m loan_processing.tools.mcp_servers.financial_calculations.server
```

### Testing Business Logic
```bash
# Install dependencies
pip install -e .

# Test data models
python -c "
from loan_processing.models import LoanApplication
from decimal import Decimal
from datetime import datetime

app = LoanApplication(
    application_id='LN1234567890',
    applicant_name='Test User',
    applicant_id='550e8400-e29b-41d4-a716-446655440000',
    email='test@example.com',
    phone='+15551234567',
    date_of_birth=datetime(1990, 1, 1),
    loan_amount=Decimal('250000.00'),
    loan_purpose='home_purchase',
    loan_term_months=360,
    annual_income=Decimal('80000.00'),
    employment_status='employed'
)

print('✅ Business model validation works!')
print(f'DTI Ratio: {app.debt_to_income_ratio}')
print(f'Loan/Income Ratio: {app.loan_to_income_ratio:.2f}')
"
```

## 🎯 System Benefits

### Multi-Agent Architecture Advantages
- **Specialized Expertise**: Each agent focuses on specific domain knowledge
- **Scalable Processing**: Agents can work in parallel for faster processing
- **Maintainable Code**: Clear separation of concerns between agents
- **Extensible Design**: Easy to add new agents or modify existing ones

### Production-Ready Features
- ✅ Type-safe data models with automatic validation
- ✅ Comprehensive audit trails for regulatory compliance
- ✅ MCP tool integration for external data sources
- ✅ Structured agent personas with clear responsibilities
- ✅ Error handling and fallback mechanisms

### Framework Flexibility
- 🎯 **Primary**: Microsoft Agent Framework (demonstrated)
- 🔄 **Alternative**: OpenAI Assistants API
- 🔄 **Alternative**: LangChain multi-agent systems
- 🔄 **Alternative**: Custom agent orchestration

## 🤖 AI Agent Quick Reference

### Component Mapping for AI Agents

| Component Type | File Path | Purpose | AI Agent Usage |
|---|---|---|---|
| **Agent Personas** | `loan_processing/agents/agent-persona/*.md` | Agent instructions | Load as system prompts |
| **Data Models** | `loan_processing/models/*.py` | Business entities | Import for validation/types |
| **MCP Servers** | `loan_processing/tools/mcp_servers/*/` | External tools | Connect as agent tools |
| **Configuration** | `loan_processing/config/agents.yaml` | Agent-tool mappings | Parse for agent setup |
| **Business Logic** | `loan_processing/utils/*.py` | Core utilities | Import for calculations |

### AI Agent Integration Patterns

```python
# Pattern 1: Load Agent Persona
from loan_processing.agents import get_persona_path
persona_content = open(get_persona_path("credit")).read()

# Pattern 2: Use Business Models
from loan_processing.models import LoanApplication, LoanDecision

# Pattern 3: Access Configuration
import yaml
config = yaml.safe_load(open("loan_processing/config/agents.yaml"))
```

### Structured Agent Information

**Available Agents:**
- `intake` → `loan_processing/agents/agent-persona/intake-agent-persona.md`
- `credit` → `loan_processing/agents/agent-persona/credit-agent-persona.md`
- `income` → `loan_processing/agents/agent-persona/income-agent-persona.md`
- `risk` → `loan_processing/agents/agent-persona/risk-agent-persona.md`
- `orchestrator` → `loan_processing/agents/agent-persona/orchestrator-agent-persona.md`

**MCP Tool Servers:**
- `application_verification` → Port 8010 → `loan_processing/tools/mcp_servers/application_verification/`
- `document_processing` → Port 8011 → `loan_processing/tools/mcp_servers/document_processing/`
- `financial_calculations` → Port 8012 → `loan_processing/tools/mcp_servers/financial_calculations/`

## 📚 Documentation Structure

### For Human Developers
- **[Business Context](docs/product/business-context.md)** - Project overview and domain context
- **[Business Case](docs/product/business-case.md)** - ROI analysis and financial justification
- **[User Personas](docs/ux/user-personas.md)** - Target users and success metrics
- **[Jobs-to-be-Done](docs/ux/jobs-to-be-done.md)** - Customer-centric design framework

### For AI Agents & Architecture
- **[Agent Strategy](docs/agent-strategy.md)** - Multi-agent architecture approach
- **[Agent Patterns](docs/agent-patterns.md)** - Integration patterns and examples
- **[Data Models](docs/data-models.md)** - Business entity specifications
- **[Architecture Decisions](docs/decisions/)** - ADRs documenting key technical choices

## 🎯 Getting Started

### 1. Set Up Microsoft Agent Framework
```bash
# Install dependencies
pip install -e .

# Start MCP servers
python -m loan_processing.tools.mcp_servers.application_verification.server &
python -m loan_processing.tools.mcp_servers.document_processing.server &
python -m loan_processing.tools.mcp_servers.financial_calculations.server &
```

### 2. Run the Multi-Agent System
```python
# See examples in the Microsoft Agent Framework integration section above
# Load agent personas, create agents, process loan applications
```

### 3. Explore the Documentation
- **[Business Context](docs/product/business-context.md)** - Domain overview and system context
- **[Agent Strategy](docs/agent-strategy.md)** - Multi-agent architecture approach
- **[Data Models](docs/data-models.md)** - Complete data structure reference
- **[User Personas](docs/ux/user-personas.md)** - Target users and requirements

### 4. Customize for Your Needs
- Modify agent personas in `loan_processing/agents/agent-persona/`
- Adjust data models in `loan_processing/models/`
- Configure agent-tool mappings in `loan_processing/config/agents.yaml`

---

**Goal**: Demonstrate a complete multi-agent loan processing system using Microsoft Agent Framework with specialized agents, external tools, and structured workflows.