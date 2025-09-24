# Loan Processing Business Logic Foundation

A simplified, framework-agnostic loan processing system that provides core business logic, data models, and agent personas for integration with Microsoft Agent Framework or any other AI agent system.

## 🎯 Philosophy: Business Logic First

This repository contains **only the essential business components** needed for loan processing:

- ✅ **Business Data Models**: Validated loan applications, assessments, and decisions
- ✅ **MCP Servers**: Tool integrations for external data (credit, documents, calculations)
- ✅ **Agent Personas**: Specialized agent instructions for loan processing tasks
- ✅ **Service Interfaces**: Abstract business service definitions

**What's NOT included** (by design):
- ❌ Agent framework implementations
- ❌ Orchestration engines
- ❌ Complex agent creation code
- ❌ Provider abstractions

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

## 🚀 Usage with Microsoft Agent Framework

### 1. Load Agent Personas
```python
from loan_processing.agents import get_persona_path

# Get persona file for framework integration
credit_persona_path = get_persona_path("credit")
with open(credit_persona_path, 'r') as f:
    credit_instructions = f.read()

# Use with Microsoft Agent Framework ChatClientAgent
```

### 2. Use Business Models
```python
from loan_processing.models import LoanApplication, LoanDecision

# Create validated loan application
application = LoanApplication(
    application_id="LN1234567890",
    applicant_name="John Doe",
    email="john.doe@example.com",
    phone="+15551234567",
    # ... other fields with automatic validation
)

# Business logic is preserved with proper validation
print(f"DTI Ratio: {application.debt_to_income_ratio}")
```

### 3. Access MCP Server Configurations
```python
import yaml

with open('loan_processing/config/agents.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Get MCP servers for credit agent
credit_servers = config['agent_personas']['credit']['mcp_servers']
# ['application_verification', 'financial_calculations', 'document_processing']
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

## 💼 Business Logic Highlights

### Comprehensive Data Models
- **LoanApplication**: Immutable application data with regex validation
- **Assessment Models**: Structured results from each agent type
- **LoanDecision**: Final decision with audit trail and reasoning

### Built-in Business Rules
- Automatic DTI ratio calculations
- Credit score validation (300-850 range)
- Loan amount and term validation
- Email and phone format validation

### Security Features
- Uses `applicant_id` (UUID) instead of SSN for privacy
- Structured audit trails for compliance
- Secure parameter handling in MCP servers

## 🔧 Integration Examples

### With Microsoft Agent Framework
```python
# Example framework integration
from microsoft_agent_framework import ChatClientAgent
from loan_processing.agents import get_persona_path
from loan_processing.models import LoanApplication

# Load agent persona
with open(get_persona_path("credit"), 'r') as f:
    persona = f.read()

# Create agent with persona
credit_agent = ChatClientAgent(
    name="Credit Assessment Agent",
    instructions=persona,
    # Add MCP tools based on config
)

# Process application
application = LoanApplication(...)
result = await credit_agent.run(application.dict())
```

### Standalone Business Logic
```python
from loan_processing.models import LoanApplication
from decimal import Decimal

# Create application with automatic validation
app = LoanApplication(
    application_id="LN1234567890",
    applicant_name="Jane Smith",
    annual_income=Decimal("75000.00"),
    loan_amount=Decimal("300000.00"),
    existing_debt=Decimal("2500.00"),
    # ... other fields
)

# Business calculations work immediately
print(f"Loan to Income Ratio: {app.loan_to_income_ratio:.2f}")
print(f"Monthly DTI: {app.debt_to_income_ratio:.2f}")
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

## 📈 Migration Benefits

### From Complex to Simple
- **Before**: 6,680+ lines with orchestration complexity
- **After**: Core business logic only, framework-agnostic
- **Result**: Easy integration with any agent framework

### Preserved Business Value
- ✅ Complete loan processing business rules
- ✅ Validated data models with proper constraints
- ✅ MCP server implementations for real-world integration
- ✅ Agent persona definitions from domain expertise

### Ready for Framework Integration
- 🔄 Microsoft Agent Framework: Load personas directly
- 🔄 OpenAI Assistants: Convert personas to instructions
- 🔄 LangChain: Use as tool definitions and prompts
- 🔄 AutoGen: Apply as agent system messages

## 🎯 Next Steps

1. **Choose Your Framework**: Microsoft Agent Framework, OpenAI, LangChain, etc.
2. **Load Agent Personas**: Use the markdown files as agent instructions
3. **Integrate MCP Servers**: Connect the three tool servers to your agents
4. **Build Workflow**: Create your own orchestration using the business models

The business logic is ready. The agent framework choice is yours.

---

**Philosophy**: Keep business logic separate from framework complexity. This foundation will work with any agent system, today and in the future.