# Loan Defenders Agent Patterns

Personality-driven agent personas with superhero themes for autonomous loan processing business logic.

## Overview

Our **Business Logic First** approach provides business-focused agent personas that embody loan processing domain expertise. Each persona contains the specialized knowledge needed for their role in the loan evaluation workflow.

## Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Business Config  │──▶│ Framework Agent  │──▶│   MCP Servers   │
│ (agents.yaml)    │    │ + Persona File   │    │ (Tool Servers)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↓                      ↓                      ↓
  Framework-Agnostic      Domain Logic           Framework
   Configuration         in Personas           Orchestration
```

## Business Logic Foundation

Agent configuration and personas are separated from framework implementation:

```yaml
# loan_processing/config/agents.yaml
agent_personas:
  intake:
    file: "intake-agent-persona.md"
    description: "Fast application triage and routing"
    mcp_servers: []  # Optimized for speed

  credit:
    file: "credit-agent-persona.md"
    description: "Comprehensive credit evaluation"
    mcp_servers: ["application_verification", "financial_calculations"]
```

```python
# Business configuration loading
from loan_processing.utils import PersonaLoader, ConfigurationLoader

# Load business configuration
config = ConfigurationLoader.load_config()
credit_persona = PersonaLoader.load_persona('credit')
risk_persona = PersonaLoader.load_persona('risk')

# Business personas contain all domain expertise
print(f"Credit agent capabilities: {config['agent_personas']['credit']['capabilities']}")
```

## Adding New Agents

### Step 1: Define Agent Configuration

Add your agent to `loan_processing/config/agents.yaml`:

```yaml
agent_personas:
  your_new_agent:
    file: "your-agent-persona.md"
    description: "What this agent does"
    mcp_servers:
      - "application_verification"  # Which tools it can access
      - "document_processing"
    capabilities:
      - "Specific capability 1"
      - "Specific capability 2"
```

**Key Changes from Complex Approach**:
- No provider-specific config (framework handles this)
- No output format specification (defined in persona)
- Simplified to essential business mappings

### Step 2: Create Agent Persona

Create `loan_processing/agents/agent-persona/your-agent-persona.md`:

```markdown
# Your Agent Name

## Jobs-to-be-Done Focus
**Primary Customer Job**: "When I [situation], I want [motivation], so I [outcome]"

## Role and Responsibilities
You are a specialized agent responsible for [specific domain task] in the loan processing workflow.

## Domain Expertise
[Describe the specific domain knowledge and decision-making expertise]

## Available Tools
You have access to the following MCP servers:
- **application_verification**: Identity, employment, and credit checks
- **document_processing**: Document analysis and data extraction

## Decision Framework
[Provide clear decision-making criteria based on domain expertise]

## Output Requirements
Provide structured assessment with:
- Primary assessment result
- Confidence score (0-100)
- Risk factors identified
- Recommendations for next steps
- Tools used during assessment
```

### Step 3: Use Your Agent

```python
# Using your new agent in business workflow
from loan_processing.utils import PersonaLoader, ConfigurationLoader
from loan_processing.models import LoanApplication

# Load agent configuration
config = ConfigurationLoader.load_config()
if "your_new_agent" in config['agent_personas']:
    agent_config = config['agent_personas']['your_new_agent']
    persona_content = PersonaLoader.load_persona('your_new_agent')

    # Agent is ready with business logic and tool access
    available_tools = agent_config['mcp_servers']
    print(f"Agent has access to: {available_tools}")
```

## Current Agent Personas

### Jobs-to-be-Done Focused Agents

1. **Intake Agent** ([persona](../loan_processing/agents/agent-persona/intake-agent-persona.md))
   - **Primary Job**: "Make this process smooth and complete the first time"
   - No MCP tools (speed optimized)
   - Creates confidence through immediate feedback

2. **Credit Agent** ([persona](../loan_processing/agents/agent-persona/credit-agent-persona.md))
   - **Primary Job**: "Get fair credit evaluation considering my full story"
   - Uses verification and calculation tools
   - Provides holistic assessment with improvement guidance

3. **Income Agent** ([persona](../loan_processing/agents/agent-persona/income-agent-persona.md))
   - **Primary Job**: "Have my earning capacity properly recognized and valued"
   - Handles diverse income patterns
   - Recognizes gig economy and non-traditional income

4. **Risk Agent** ([persona](../loan_processing/agents/agent-persona/risk-agent-persona.md))
   - **Primary Job**: "Get loan terms that match my actual risk level"
   - Synthesizes all assessments with context from other agents
   - Provides clear rationale and optimal terms

5. **Orchestrator Agent** ([persona](../loan_processing/agents/agent-persona/orchestrator-agent-persona.md))
   - Coordinates workflow and makes final decisions
   - Ensures comprehensive evaluation and audit trail
   - Handles edge cases and escalation

## MCP Server Integration

Business capabilities exposed as independent tool servers:

**Configuration**: `loan_processing/config/mcp_servers.yaml`
```yaml
servers:
  application_verification:
    host: "localhost"
    port: 8010
    url: "http://localhost:8010/sse"
    tools:
      - "verify_identity"
      - "get_credit_report"
      - "verify_employment"
      - "get_bank_account_data"

  document_processing:
    host: "localhost"
    port: 8011
    tools:
      - "extract_text_from_document"
      - "classify_document_type"
      - "validate_document_format"

  financial_calculations:
    host: "localhost"
    port: 8012
    tools:
      - "calculate_debt_to_income_ratio"
      - "calculate_loan_affordability"
      - "analyze_income_stability"
```

**Business Tool Integration**: Agents access MCP servers based on their business role - Credit Agent uses verification tools, Income Agent uses employment services, Risk Agent synthesizes all data.

## Business Workflow Examples

### Loan Processing Workflow
```python
from loan_processing.utils import ConfigurationLoader, PersonaLoader
from loan_processing.models import LoanApplication, LoanDecision

class LoanProcessingWorkflow:
    def __init__(self):
        self.config = ConfigurationLoader.load_config()
        self.personas = {
            agent_name: PersonaLoader.load_persona(agent_name)
            for agent_name in self.config['agent_personas'].keys()
        }

    def get_agent_capabilities(self, agent_name: str) -> dict:
        """Get agent's business capabilities and tool access"""
        agent_config = self.config['agent_personas'][agent_name]
        return {
            'description': agent_config['description'],
            'mcp_servers': agent_config['mcp_servers'],
            'capabilities': agent_config.get('capabilities', []),
            'persona_length': len(self.personas[agent_name].split('\n'))
        }

    def process_application(self, application: LoanApplication) -> dict:
        """Process loan application through business workflow"""
        workflow = {
            'application_id': application.application_id,
            'agents_involved': [],
            'assessments': {},
            'business_logic': {}
        }

        # Each agent has specific business role
        for agent_name in ["intake", "credit", "income", "risk"]:
            capabilities = self.get_agent_capabilities(agent_name)
            workflow['agents_involved'].append({
                'name': agent_name,
                'role': capabilities['description'],
                'tools': capabilities['mcp_servers']
            })

        return workflow
```

## Benefits of Business Logic Foundation

- **Domain Expertise**: Each agent contains specialized loan processing knowledge
- **Customer-Focused**: Agents designed around customer jobs-to-be-done
- **Business Maintainable**: Domain experts can modify agent personas directly
- **Regulatory Compliant**: Built-in audit trails and decision transparency
- **Scalable**: Add new agents or capabilities without changing existing business logic
- **Cost Effective**: Reduces processing time from days to minutes
- **Quality Consistent**: Standardized evaluation criteria across all applications

## Progressive Enhancement Strategy

Our multi-agent architecture enables progressive enhancement without refactoring:

**Current State (3 MCP Servers)**:
- Application verification
- Document processing
- Financial calculations

**Planned Expansion (20+ MCP Servers)**:

**Enhanced Intake Capabilities**:
- Document OCR and fraud detection
- Application deduplication
- Public records enrichment
- Real-time identity verification

**Advanced Credit Assessment**:
- Multiple credit bureau APIs
- Alternative credit data sources
- International credit databases
- ML-based credit scoring

**Comprehensive Income Verification**:
- Payroll service integrations
- Tax transcript APIs
- Bank account aggregation
- Gig economy platform APIs

**Sophisticated Risk Management**:
- Advanced risk scoring models
- Regulatory compliance automation
- Property valuation services
- Insurance verification

**Key Benefit**: Agents evolve independently - Credit Agent can add new capabilities while Income Agent remains unchanged.

## Implementation Files

**Business Logic Foundation**:
- **Agent Personas**: [`loan_processing/agents/agent-persona/`](../loan_processing/agents/agent-persona/) - Domain expertise in markdown
- **Agent Configuration**: [`loan_processing/config/agents.yaml`](../loan_processing/config/agents.yaml) - Simple persona mappings
- **MCP Configuration**: [`loan_processing/config/mcp_servers.yaml`](../loan_processing/config/mcp_servers.yaml) - Tool server definitions
- **Data Models**: [`loan_processing/models/`](../loan_processing/models/) - Type-safe business models
- **Utilities**: [`loan_processing/utils/`](../loan_processing/utils/) - Configuration and persona loading

**Tool Implementation**:
- **MCP Servers**: [`loan_processing/tools/mcp_servers/`](../loan_processing/tools/mcp_servers/) - Business capability servers
- **Business Services**: [`loan_processing/tools/services/`](../loan_processing/tools/services/) - Core business logic

**Documentation**:
- **Agent Strategy**: [`docs/agent-strategy.md`](agent-strategy.md) - Configuration-driven architecture
- **Jobs-to-be-Done**: [`docs/jobs-to-be-done.md`](jobs-to-be-done.md) - Customer-centric design principles
- **Business Case**: [`docs/business-case.md`](business-case.md) - ROI and implementation strategy

This foundation provides all the business logic needed for loan processing automation.