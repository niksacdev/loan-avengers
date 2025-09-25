# Loan Processing Workflow Patterns

Business workflow patterns for coordinating multi-agent loan processing.

## Overview

Our **Business Logic First** approach provides proven workflow patterns for loan processing:

- **Business Focus**: Agents designed around loan processing expertise
- **Configuration-Driven**: Business rules and agent roles defined in YAML
- **Progressive Enhancement**: Start with basic workflows, add sophistication as needed
- **Customer-Centric**: Agents designed around customer jobs-to-be-done

## Business Logic Foundation

### Loan Processing Workflow

Our business logic foundation provides the essential components for loan processing:

**Configuration**: [`loan_processing/config/agents.yaml`](../loan_processing/config/agents.yaml)

```yaml
agent_personas:
  intake:
    file: "intake-agent-persona.md"
    description: "Fast application triage and routing"
    mcp_servers: []  # Speed optimized
  credit:
    file: "credit-agent-persona.md"
    description: "Comprehensive credit evaluation"
    mcp_servers: ["application_verification", "financial_calculations"]
```

**MCP Servers**: [`loan_processing/config/mcp_servers.yaml`](../loan_processing/config/mcp_servers.yaml)

```yaml
servers:
  application_verification:
    host: "localhost"
    port: 8010
    url: "http://localhost:8010/sse"
    tools: ["verify_identity", "get_credit_report"]
```

```text
Application → Intake → Credit → Income → Risk → Decision
     ↓          ↓        ↓        ↓       ↓
  Context    Context  Context  Context  Final
   Init      +Intake  +Credit  +Income  Decision
```

**Business Workflow Configuration**:
```python
# Loan processing business logic
from loan_processing.utils import ConfigurationLoader, PersonaLoader
from loan_processing.config.settings import get_mcp_config
from loan_processing.models import LoanApplication, LoanDecision

# Load business configuration
config = ConfigurationLoader.load_config()
mcp_config = get_mcp_config()

# Each agent has specific business role
workflow_agents = {
    'intake': 'Fast application validation and routing',
    'credit': 'Comprehensive creditworthiness assessment',
    'income': 'Employment and income verification',
    'risk': 'Final decision synthesis and compliance'
}

for agent_name, business_role in workflow_agents.items():
    agent_config = config['agent_personas'][agent_name]
    print(f"{agent_name}: {business_role}")
    print(f"Tools: {agent_config['mcp_servers']}")
```

**Business Benefits**:
- Specialized domain expertise in each agent
- Clear separation of business responsibilities
- Audit trail through sequential processing
- Consistent evaluation standards

## Business Workflow Patterns

Different business scenarios require different workflow patterns:

### Standard Sequential Processing

**Use Case**: Most loan applications requiring comprehensive evaluation

```python
# Standard loan processing workflow
class StandardLoanWorkflow:
    def __init__(self):
        self.config = ConfigurationLoader.load_config()
        self.workflow_steps = ["intake", "credit", "income", "risk"]

    def process_application(self, application: LoanApplication) -> dict:
        """Process application through standard workflow"""
        workflow_result = {
            "application_id": application.application_id,
            "workflow_type": "standard_sequential",
            "agents_used": [],
            "business_logic": {}
        }

        for step, agent_name in enumerate(self.workflow_steps):
            agent_config = self.config['agent_personas'][agent_name]
            workflow_result["agents_used"].append({
                "step": step + 1,
                "agent": agent_name,
                "business_role": agent_config['description'],
                "tools_available": agent_config['mcp_servers']
            })

        return workflow_result
```

### Fast-Track Parallel Processing

**Use Case**: High-quality applications needing quick turnaround

```python
# Fast-track workflow for premium applications
class FastTrackLoanWorkflow:
    def __init__(self):
        self.config = ConfigurationLoader.load_config()
        self.parallel_agents = ["credit", "income"]  # Process simultaneously
        self.final_agent = "risk"

    def process_application(self, application: LoanApplication) -> dict:
        """Fast-track processing for qualified applications"""
        workflow_result = {
            "application_id": application.application_id,
            "workflow_type": "fast_track_parallel",
            "business_rationale": "High credit score enables parallel processing",
            "time_saved": "40-50% faster than standard workflow"
        }

        # Parallel assessment phase
        parallel_assessments = []
        for agent_name in self.parallel_agents:
            agent_config = self.config['agent_personas'][agent_name]
            parallel_assessments.append({
                "agent": agent_name,
                "role": agent_config['description'],
                "tools": agent_config['mcp_servers'],
                "processing": "parallel"
            })

        # Final synthesis
        risk_config = self.config['agent_personas'][self.final_agent]
        final_assessment = {
            "agent": self.final_agent,
            "role": risk_config['description'],
            "inputs": ["credit_assessment", "income_assessment"],
            "processing": "synthesis"
        }

        workflow_result["assessment_phases"] = {
            "parallel": parallel_assessments,
            "final": final_assessment
        }

        return workflow_result
```

### Adaptive Conditional Processing

**Use Case**: Applications requiring different evaluation paths based on complexity

```python
# Adaptive workflow based on application characteristics
class AdaptiveLoanWorkflow:
    def __init__(self):
        self.config = ConfigurationLoader.load_config()
        self.routing_rules = {
            'FAST_TRACK': ['credit', 'risk'],  # High credit score, simple case
            'ENHANCED': ['credit', 'income', 'employment', 'assets', 'risk'],  # Complex case
            'STANDARD': ['credit', 'income', 'risk']  # Normal processing
        }

    def determine_workflow_path(self, application: LoanApplication) -> str:
        """Business logic to determine appropriate workflow"""
        if (application.credit_score and application.credit_score > 750 and
            application.debt_to_income_ratio < 0.30):
            return 'FAST_TRACK'
        elif (application.loan_purpose == 'business' or
              application.employment_status == 'self_employed'):
            return 'ENHANCED'
        else:
            return 'STANDARD'

    def process_application(self, application: LoanApplication) -> dict:
        """Route application through appropriate workflow path"""
        workflow_path = self.determine_workflow_path(application)
        selected_agents = self.routing_rules[workflow_path]

        workflow_result = {
            "application_id": application.application_id,
            "workflow_type": "adaptive_conditional",
            "selected_path": workflow_path,
            "routing_rationale": self._get_routing_rationale(application, workflow_path),
            "agents_sequence": []
        }

        for agent_name in selected_agents:
            agent_config = self.config['agent_personas'][agent_name]
            workflow_result["agents_sequence"].append({
                "agent": agent_name,
                "business_role": agent_config['description'],
                "tools": agent_config['mcp_servers']
            })

        return workflow_result

    def _get_routing_rationale(self, application: LoanApplication, path: str) -> str:
        """Explain why this path was selected"""
        rationales = {
            'FAST_TRACK': f"High credit score ({application.credit_score}) and low DTI ratio enable expedited processing",
            'ENHANCED': f"Complex application ({application.loan_purpose}, {application.employment_status}) requires comprehensive evaluation",
            'STANDARD': "Standard evaluation criteria apply"
        }
        return rationales.get(path, "Standard processing")
```

**Routing Logic in Intake Persona**:
```markdown
# Intake Agent Persona (Example)

## Decision Framework
Based on application characteristics, route as follows:

- **FAST_TRACK**: Credit score > 750, DTI < 30%, employment > 2 years
- **ENHANCED**: First-time buyer, self-employed, or complex income
- **STANDARD**: All other applications

## Output Requirements
- routing_decision: FAST_TRACK/ENHANCED/STANDARD
- confidence_score: 0-100
- reasoning: Explanation of routing choice
```

### Custom Framework - Hierarchical Pattern

```python
# Supervisor-agent pattern with specialist teams
class HierarchicalLoanOrchestrator:
    def __init__(self):
        # Load supervisor persona
        self.supervisor = self._create_agent('loan_supervisor')

        # Create specialist teams
        self.credit_team = {
            'lead': self._create_agent('credit_lead'),
            'specialists': [
                self._create_agent('fico_specialist'),
                self._create_agent('alternative_credit_specialist')
            ]
        }

    async def process_application(self, application):
        # Supervisor makes initial assessment
        supervisor_assessment = await self.supervisor.assess(application)

        # Route to appropriate specialist teams
        if supervisor_assessment.complexity == 'HIGH':
            # Use all specialists
            return await self._full_team_review(application)
        else:
            # Standard processing
            return await self._standard_review(application)
```

**Benefits**:
- Clear escalation paths through business personas
- Specialist expertise in separate agent personas
- Supervisor logic in configuration, not code

## Context Management Patterns

### Simple Context Passing
```python
# Any framework can use this pattern
class ContextManager:
    def __init__(self):
        self.application_data = None
        self.assessments = {}

    def add_assessment(self, agent_name: str, result: dict):
        self.assessments[agent_name] = result

    def get_context_for_agent(self, agent_name: str) -> dict:
        return {
            "application": self.application_data,
            "previous_assessments": self.assessments,
            "agent_config": self._get_agent_config(agent_name)
        }
```

### Framework-Specific Context
```python
# Microsoft Agent Framework example
context = {
    "messages": [
        {"role": "system", "content": persona_instructions},
        {"role": "user", "content": f"Application: {application_json}"}
    ]
}

# OpenAI Assistants example
thread = openai.beta.threads.create()
for assessment in previous_assessments:
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Previous assessment: {assessment}"
    )
```

## Quality Control Patterns

### Business Logic Validation
```python
# Built into business models
from loan_processing.models import AgentAssessment

def validate_assessment(assessment_data: dict) -> bool:
    try:
        # Automatic validation through Pydantic
        assessment = AgentAssessment.model_validate(assessment_data)

        # Business logic validation
        if assessment.confidence_score < 0.7:
            return False
        if assessment.status != "COMPLETE":
            return False

        return True
    except ValidationError:
        return False
```

### Persona-Driven Quality Gates
```markdown
# Example from Risk Agent Persona

## Quality Requirements
Before making final decision, ensure:
- Credit assessment confidence > 80%
- Income verification completed
- All regulatory checks passed

If any requirement fails, set decision to MANUAL_REVIEW
```

## Error Handling Patterns

### Framework Error Handling
```python
# Each framework implements its own error handling
class FrameworkErrorHandler:
    async def handle_agent_error(self, agent_name: str, error: Exception, context: dict):
        # Log error with application context
        logger.error(f"Agent {agent_name} failed", extra={
            "application_id": context.get("application", {}).get("application_id"),
            "error": str(error)
        })

        # Business logic: what to do on error
        if agent_name == "intake":
            return {"decision": "MANUAL_REVIEW", "reason": "Intake validation failed"}
        elif agent_name in ["credit", "income"]:
            return {"decision": "MANUAL_REVIEW", "reason": f"{agent_name} assessment failed"}
        else:
            return {"decision": "MANUAL_REVIEW", "reason": "System error"}
```

### Business Fallback Rules
```python
# Encoded in agent personas
FALLBACK_RULES = {
    "insufficient_data": "MANUAL_REVIEW",
    "system_timeout": "RETRY_ONCE_THEN_MANUAL",
    "confidence_too_low": "MANUAL_REVIEW",
    "regulatory_concern": "IMMEDIATE_MANUAL_REVIEW"
}
```

## Observability Patterns

### Framework-Agnostic Logging
```python
# Built into business models
from loan_processing.models import AgentAssessment
from loan_processing.utils import logger

def log_agent_assessment(agent_name: str, assessment: AgentAssessment, application_id: str):
    logger.info("Agent assessment completed", extra={
        "application_id": application_id,
        "agent_name": agent_name,
        "status": assessment.status,
        "confidence": assessment.confidence_score,
        "tools_used": assessment.tools_used,
        "processing_time_ms": assessment.processing_time_ms
    })
```

### Business Audit Trail
```python
# Preserved in decision model
class LoanDecision(BaseModel):
    # ... other fields ...

    # Complete audit trail
    agent_assessments: List[AgentAssessment]
    decision_rationale: str
    regulatory_checks: Dict[str, bool]

    def get_audit_trail(self) -> Dict[str, Any]:
        """Generate compliance-ready audit trail"""
        return {
            "application_id": self.application_id,
            "decision": self.decision,
            "timestamp": self.decision_timestamp,
            "agents_involved": [a.agent_name for a in self.agent_assessments],
            "tools_used": list(set(tool for a in self.agent_assessments for tool in a.tools_used)),
            "rationale": self.decision_rationale
        }
```

## Business Implementation Examples

### Complete Loan Processing System
```python
# Complete business workflow implementation
from loan_processing.utils import ConfigurationLoader, PersonaLoader
from loan_processing.models import LoanApplication, LoanDecision
from loan_processing.config.settings import get_mcp_config

class LoanProcessingSystem:
    def __init__(self):
        self.config = ConfigurationLoader.load_config()
        self.mcp_config = get_mcp_config()
        self.workflow_manager = WorkflowManager()

    def get_business_capabilities(self) -> dict:
        """Get complete system business capabilities"""
        capabilities = {
            "agents": {},
            "tools": {},
            "workflows": ["standard", "fast_track", "enhanced", "adaptive"]
        }

        # Document each agent's business role
        for agent_name, agent_config in self.config['agent_personas'].items():
            capabilities["agents"][agent_name] = {
                "business_role": agent_config['description'],
                "mcp_servers": agent_config['mcp_servers'],
                "capabilities": agent_config.get('capabilities', [])
            }

        # Document available business tools
        for server_name, server_config in self.mcp_config.get_available_servers().items():
            capabilities["tools"][server_name] = {
                "business_purpose": self._get_business_purpose(server_name),
                "tools": server_config.get('tools', [])
            }

        return capabilities

    def _get_business_purpose(self, server_name: str) -> str:
        """Get business purpose of MCP server"""
        purposes = {
            "application_verification": "Identity, employment, and credit verification",
            "document_processing": "Document analysis and data extraction",
            "financial_calculations": "Loan affordability and risk calculations"
        }
        return purposes.get(server_name, "Business tool server")

    def process_loan_application(self, application: LoanApplication) -> dict:
        """Process loan through appropriate business workflow"""
        # Determine workflow based on business rules
        workflow_type = self.workflow_manager.determine_workflow(application)

        result = {
            "application_id": application.application_id,
            "workflow_selected": workflow_type,
            "business_rationale": self.workflow_manager.get_workflow_rationale(workflow_type),
            "processing_time_estimate": self._get_time_estimate(workflow_type),
            "agents_involved": self.workflow_manager.get_workflow_agents(workflow_type),
            "compliance_checks": self._get_required_compliance_checks(application)
        }

        return result

    def _get_time_estimate(self, workflow_type: str) -> str:
        """Estimate processing time for workflow type"""
        estimates = {
            "fast_track": "2-3 minutes",
            "standard": "3-5 minutes",
            "enhanced": "5-8 minutes",
            "adaptive": "3-8 minutes depending on routing"
        }
        return estimates.get(workflow_type, "3-5 minutes")

    def _get_required_compliance_checks(self, application: LoanApplication) -> list:
        """Get compliance checks required for this application"""
        checks = ["FCRA_COMPLIANCE", "ECOA_COMPLIANCE"]

        if application.loan_amount > 100000:
            checks.append("HIGH_VALUE_REVIEW")

        if application.loan_purpose in ['business', 'investment']:
            checks.append("COMMERCIAL_LENDING_RULES")

        return checks
```

## Benefits of Business Logic Foundation

1. **Domain Expertise**: Each agent contains specialized loan processing knowledge
2. **Business Agility**: Modify decision criteria and workflows without code changes
3. **Regulatory Compliance**: Built-in audit trails and decision transparency
4. **Cost Efficiency**: Reduce processing time from days to minutes
5. **Quality Consistency**: Standardized evaluation criteria across all applications
6. **Scalability**: Add new agents or business rules without system changes

## Implementation Files

**Business Logic Foundation**:
- **Agent Personas**: [`loan_processing/agents/agent-persona/`](../loan_processing/agents/agent-persona/) - Domain expertise
- **Configuration**: [`loan_processing/config/agents.yaml`](../loan_processing/config/agents.yaml) - Agent mappings
- **MCP Servers**: [`loan_processing/config/mcp_servers.yaml`](../loan_processing/config/mcp_servers.yaml) - Tool configurations
- **Data Models**: [`loan_processing/models/`](../loan_processing/models/) - Type-safe business models
- **Utilities**: [`loan_processing/utils/`](../loan_processing/utils/) - Configuration and persona loading

**Integration Examples**:
- **Business Case**: [`docs/business-case.md`](business-case.md) - ROI and implementation strategy
- **Agent Strategy**: [`docs/agent-strategy.md`](agent-strategy.md) - Configuration-driven architecture
- **Jobs-to-be-Done**: [`docs/jobs-to-be-done.md`](jobs-to-be-done.md) - Customer-centric agent design

Framework implementations can be built on top of this foundation using the patterns shown above.