# Multi-Agent Loan Processing System

A comprehensive loan processing system using Microsoft Agent Framework that implements autonomous agents for credit assessment, income verification, and risk evaluation.

## 🏗️ Architecture Overview

This system follows a **multi-agent strategic foundation** designed for progressive autonomy and future extensibility. The architecture is based on consolidated decisions from multiple ADR documents.

### Key Architectural Principles

- **Multi-Agent Strategic Foundation** (ADR-015): Agents gain intelligence as MCP servers expand
- **Configuration-Driven Orchestration** (ADR-005): No hardcoded agent handoffs
- **Agent Base Architecture** (ADR-002): Microsoft Agent Framework composition pattern
- **Layered Configuration System** (ADR-007): Dependency injection with multiple providers

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                 Application Layer                           │
├─────────────────────────────────────────────────────────────┤
│              Orchestration Engine                           │
│  Pattern Loader  │  Agent Registry  │  Context Management  │
├─────────────────────────────────────────────────────────────┤
│                    Agent Layer                              │
│  Intake Agent  │  Credit Agent  │  Income Agent  │ Risk Agent │
├─────────────────────────────────────────────────────────────┤
│                     Tool Layer                              │
│  MCP Servers: App Verification │ Document Processing │ Financial │
├─────────────────────────────────────────────────────────────┤
│                Business Services & Data Models             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Microsoft Agent Framework (when available)
- MCP (Model Context Protocol) servers

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd loan-agent-workflow

# Install dependencies
pip install -e .
```

### Basic Usage

```python
from loan_processing.agents import initialize_global_registry, get_global_registry
from loan_processing.orchestration import OrchestrationEngine
from loan_processing.models import LoanApplication

# Initialize agent registry
await initialize_global_registry("loan_processing/config/agents.yaml")

# Create orchestration engine
engine = OrchestrationEngine()
await engine.load_patterns_from_directory("loan_processing/config/patterns/")

# Create loan application
application = LoanApplication(
    application_id="LN1234567890",
    applicant_name="John Doe",
    # ... other fields
)

# Process application
decision = await engine.execute_pattern("sequential", application)
print(f"Decision: {decision.decision} - {decision.decision_reason}")
```

## 🤖 Agent Types

### Intake Agent
- **Purpose**: Data completeness check and routing assignment
- **Tools**: None (fast triage)
- **Output**: Validation status, routing decision, confidence score

### Credit Agent
- **Purpose**: Credit risk assessment and scoring
- **Tools**: Application verification, financial calculations, document processing
- **Output**: Credit score, risk category, payment history, red flags

### Income Agent
- **Purpose**: Income and employment verification
- **Tools**: Application verification, document processing, financial calculations
- **Output**: Verified income, employment status, stability scores

### Risk Agent
- **Purpose**: Final decision synthesis and recommendations
- **Tools**: All available MCP tools
- **Output**: Final recommendation, approved terms, conditions, reasoning

## 🔄 Orchestration Patterns

### Sequential Pattern
Agents execute in order with context passing between each stage:
```
Intake → Credit → Income → Risk → Decision
```

### Parallel Pattern
Agents execute simultaneously after intake:
```
      ┌─ Credit ─┐
Intake┤          ├─ Risk → Decision
      └─ Income ─┘
```

### Collaborative Pattern (Future)
Agents communicate directly with each other based on assessment needs.

## 📁 Directory Structure

```
loan_processing/
├── agents/
│   ├── base.py              # Base agent classes (Microsoft Agent Framework)
│   ├── registry.py          # Agent factory and management
│   └── specialized/         # Specialized agent implementations (future)
├── orchestration/
│   ├── engine.py            # Dynamic pattern execution engine
│   └── patterns/            # YAML workflow definitions
├── models/                  # Preserved business data models
│   ├── application.py       # Loan application model
│   ├── assessment.py        # Assessment result models
│   └── decision.py          # Final decision model
├── tools/
│   ├── mcp_servers/         # MCP server implementations
│   └── services/            # Business service interfaces
├── config/
│   └── agents.yaml          # Agent configurations
└── utils/                   # Shared utilities
```

## ⚙️ Configuration

### Agent Configuration (`config/agents.yaml`)
```yaml
agents:
  credit:
    name: "Credit Agent"
    description: "Evaluates creditworthiness and financial risk"
    mcp_servers: ["application_verification", "financial_calculations"]
    capabilities: ["Credit scoring", "Risk categorization"]
    output_format:
      credit_score:
        type: "integer"
        range: [300, 850]
```

### Pattern Configuration (`config/patterns/sequential.yaml`)
```yaml
name: "sequential_loan_processing"
pattern_type: "sequential"
agents:
  - type: "intake"
    timeout_seconds: 180
handoff_rules:
  - from: "intake"
    to: "credit"
    conditions:
      - "validation_status == 'PASSED'"
```

## 🧪 Development

### Key Preserved Components
- **Business Logic**: All loan processing business rules preserved
- **Data Models**: Complete Pydantic models with validation
- **MCP Servers**: Tool integration for external data
- **Service Interfaces**: Abstract business service definitions

### Framework Migration Status

- ✅ **Architecture Consolidation**: ADRs consolidated into single document
- ✅ **OpenAI SDK Removal**: All OpenAI-specific code removed
- ✅ **Agent Base Classes**: Framework-agnostic base implementations
- ✅ **Configuration System**: Registry and orchestration patterns
- 🔄 **Microsoft Agent Framework Integration**: Pending framework availability
- 🔄 **Specialized Agent Implementations**: To be created with new framework
- 🔄 **Test Suite**: To be regenerated for new architecture

### Next Steps

1. **Agent Implementation**: Create specialized agents using Microsoft Agent Framework
2. **Framework Integration**: Integrate with ChatClientAgent patterns
3. **Pattern Enhancement**: Add parallel and collaborative orchestration
4. **Testing**: Comprehensive test suite for new architecture
5. **Documentation**: Usage examples and integration guides

## 🔍 Migration from v1.0

This repository represents a complete migration from OpenAI Agent SDK to Microsoft Agent Framework:

### What Was Preserved
- ✅ All business logic and data models
- ✅ MCP server implementations and business services
- ✅ Configuration-driven orchestration patterns
- ✅ Architectural decisions and principles

### What Was Removed
- ❌ OpenAI Agent SDK dependencies
- ❌ Provider-specific orchestration code
- ❌ Legacy test suites (to be regenerated)
- ❌ OpenAI-specific configuration and workflows

### What's New
- 🆕 Consolidated architecture document (ARCHITECTURE.md)
- 🆕 Framework-agnostic agent base classes
- 🆕 Microsoft Agent Framework integration patterns
- 🆕 Enhanced orchestration engine with YAML configuration

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Comprehensive architecture guide
- **[ADR Documents](docs/decisions/)**: Detailed architectural decisions (preserved for reference)
- **Configuration Examples**: See `loan_processing/config/` directory

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This system is designed for progressive enhancement. Key areas for contribution:

1. **Microsoft Agent Framework Integration**
2. **Specialized Agent Implementations**
3. **Enhanced MCP Server Ecosystem**
4. **Advanced Orchestration Patterns**
5. **Machine Learning Integration**

---

**Note**: This is a strategic multi-agent architecture designed to grow with increased MCP server capabilities and agent intelligence. The current implementation provides the foundation for future autonomous loan processing capabilities.