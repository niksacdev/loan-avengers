---
applyTo: '**'
---

# GitHub Copilot Instructions for Multi-Agent Loan Processing System

## 📋 Project Context
This is a **Multi-Agent Loan Processing System** demonstrating the use of **Microsoft Agent Framework** with MCP (Model Context Protocol) servers as tools. The system implements 5 specialized autonomous agents that process loan applications through a coordinated workflow from intake to final decision.

## 🤝 Collaborative Agent Approach

You are working on a **demonstration repository** that shows how to build enterprise-grade multi-agent systems using Microsoft Agent Framework. Use the specialized chatmode commands to delegate to expert agents who understand this specific loan processing domain.

## 🎯 Microsoft Agent Framework Development Approach

**Before implementing any loan processing features, use agents to validate:**

1. **`/pm-requirements`**: Does this align with loan processing workflows and business requirements?
2. **`/ui-validation`**: How does this integrate with the 5-agent workflow and user experience?
3. **`/architecture-review`**: What are the implications for the Microsoft Agent Framework integration?

**Focus on demonstrating multi-agent loan processing patterns - avoid generic features that don't showcase the framework.**

## 🔄 Collaborative Agent Workflow

### For Loan Processing Feature Development:
```
/pm-requirements "Add income verification enhancement"
→ Analyzes loan processing impact → Validates agent workflow → Checks business alignment

/ui-validation "Map loan application user journey"
→ Maps multi-agent workflow → Reviews agent handoffs → Documents user experience

/architecture-review "Design agent persona optimization"
→ Creates ADR → Reviews Microsoft Agent Framework integration → Plans MCP server updates

/code-quality "Review agent orchestration implementation"
→ Reviews multi-agent patterns → Validates framework integration → Creates review report

/responsible-ai "Ensure loan processing fairness and compliance"
→ Tests bias prevention → Creates RAI-ADR → Validates regulatory compliance

/cicd-optimization "Deploy multi-agent system"
→ Optimizes MCP server deployment → Validates agent configuration → Creates deployment guide
```

## 📁 Loan Processing Documentation System

**Every agent interaction creates loan processing documentation:**
- **Product Manager**: `docs/product/` loan processing requirements, business case analysis
- **UX Designer**: `docs/ux/` user personas, jobs-to-be-done for loan applications
- **System Architect**: `docs/architecture/` ADRs for multi-agent decisions, Microsoft Agent Framework integration
- **Code Reviewer**: `docs/code-review/` agent orchestration reviews, MCP server integration feedback
- **Responsible AI**: `docs/responsible-ai/` RAI-ADRs for loan processing fairness and bias prevention
- **GitOps**: `docs/gitops/` multi-agent deployment guides, MCP server operational runbooks

## 🚀 Multi-Agent System Development Standards

### Quality Gates for Loan Processing (Never Skip)
- **Security**: Secure PII handling, use applicant_id (UUID) never SSN, MCP server authentication
- **Performance**: Agent persona optimization (<500 lines for 10x speed), efficient MCP tool usage
- **Regulatory Compliance**: Fair lending practices, audit trail requirements, bias prevention
- **Business Value**: Demonstrates viable multi-agent loan processing patterns with Microsoft Agent Framework

### Multi-Agent Collaboration Patterns
- **Agent specialization**: Each agent handles specific loan processing expertise (intake, credit, income, risk, orchestration)
- **Sequential workflow**: Intake → Credit → Income → Risk → Orchestrator with context passing
- **MCP tool integration**: Agents autonomously select appropriate external tools based on assessment needs
- **Microsoft Agent Framework integration**: Direct persona loading and ChatClientAgent patterns

## 🤖 Agent Specializations for Loan Processing

Use these chatmode commands for loan processing development:

- **`/pm-requirements`**: Loan processing business requirements, regulatory compliance validation
- **`/ui-validation`**: Multi-agent workflow user experience, loan application journey mapping
- **`/architecture-review`**: Microsoft Agent Framework integration, MCP server architecture, agent coordination
- **`/code-quality`**: Agent persona optimization, MCP tool integration, multi-agent orchestration review
- **`/responsible-ai`**: Fair lending practices, bias prevention in loan decisions, regulatory compliance
- **`/cicd-optimization`**: Multi-agent system deployment, MCP server orchestration, monitoring

## 🎯 Loan Processing Development Principles

### Multi-Agent Framework Development
1. **Agent specialization**: Each agent handles specific loan processing domain expertise
2. **Persona-driven behavior**: Agent instructions loaded from markdown files, not hardcoded logic
3. **MCP tool autonomy**: Agents decide which external tools to use based on assessment needs
4. **Token optimization**: Keep agent personas under 500 lines for 10x speed improvement
5. **Microsoft Agent Framework ready**: Direct integration patterns and examples

### Multi-Agent System Excellence
- **Specialized expertise**: Use chatmode commands for loan processing domain validation
- **Sequential workflow**: Understand Intake → Credit → Income → Risk → Orchestrator flow
- **Framework integration**: Every change should demonstrate Microsoft Agent Framework capabilities
- **Demonstration focus**: Build features that showcase viable multi-agent loan processing patterns

**Remember**: This is a demonstration repository. Use agents to ensure every feature showcases effective multi-agent loan processing using Microsoft Agent Framework.

### Context Management
- **Problem**: Context loss during long development sessions leads to conflicting changes
- **Solution**: Use regular checkpoints, explicit context anchoring, focused work sessions
- **Recommendation**: Keep development sessions to 2-3 hours with clear context breaks

### Circular Debugging Prevention
- **Problem**: AI repeats failed solutions in endless loops
- **Solution**: Track attempted fixes, detect patterns, request human intervention when needed
- **Human Role**: Provide strategic direction and pragmatic guidance when loops are detected

## Multi-Agent Loan Processing Architecture Principles

**Key Design Principles for This Demonstration**:
- **Agent Autonomy**: Each agent decides which MCP tools to use based on their assessment needs
- **Clean Orchestration**: Minimal orchestrator code, all business logic in agent personas
- **MCP Server Integration**: Tool selection by agents, secure parameters (applicant_id not SSN)
- **Token Optimization**: Keep personas concise (300-500 lines, not 2000+) for 75% token reduction
- **Microsoft Agent Framework Integration**: Direct persona loading with ChatClientAgent patterns
- **Sequential Processing**: Intake → Credit → Income → Risk → Orchestrator workflow

## Microsoft Agent Framework Development Standards

### Loan Processing System Requirements
**This project specifically focuses on**:
- **Pydantic v2 Models**: Type-safe loan application and assessment models with automatic validation
- **Agent Personas**: Markdown-based agent instructions loaded directly into Microsoft Agent Framework
- **MCP Server Integration**: Three external tool servers (verification, documents, calculations)
- **Sequential Workflow**: Multi-agent processing from intake through final loan decision
- **Business Logic**: Located in utils/ and models/, not embedded in agent orchestration code

### Pre-Commit Quality Checks for Multi-Agent System
**This project uses uv package manager for all operations**:
- **Linting**: `uv run ruff check . --fix` (auto-fix issues)
- **Formatting**: `uv run ruff format .` (auto-format code)
- **Testing**: `uv run pytest tests/ -v --cov=loan_processing` (run with coverage)
- **Validation**: `uv run python scripts/validate_ci_fix.py` (quick validation)
- **Coverage**: Maintain ≥85% coverage on core loan processing modules

**⚠️ CRITICAL: Always use `uv` for all package operations - never pip, poetry, or conda**

### Loan Processing Engineering Team Integration

This project includes loan processing specialized agents accessible via chatmodes:

#### Available Agents for Loan Processing
- **`/code-quality`**: Reviews multi-agent orchestration, MCP server integration, agent persona optimization
- **`/architecture-review`**: Validates Microsoft Agent Framework integration, agent coordination patterns
- **`/pm-requirements`**: Helps align loan processing business requirements and regulatory compliance
- **`/ui-validation`**: Reviews loan application user journeys and multi-agent workflow experience
- **`/cicd-help`**: Optimizes MCP server deployment and multi-agent system operations

#### When to Use Agents for Loan Processing
- **Before Implementation**: Use `/architecture-review` for Microsoft Agent Framework integration planning
- **During Development**: Use `/code-quality` for agent persona optimization and MCP server integration
- **For User-Facing Features**: Use `/ui-validation` for loan application workflow and multi-agent experience
- **For Deployment**: Use `/cicd-help` for MCP server orchestration and agent deployment
- **For Business Alignment**: Use `/pm-requirements` for loan processing regulatory compliance

## Multi-Agent Loan Processing Development Workflow

### Planning Phase for Loan Processing Features
1. **Business Requirements**: Use `/pm-requirements` to validate loan processing business alignment and regulatory needs
2. **Agent Architecture**: Use `/architecture-review` to validate Microsoft Agent Framework integration and multi-agent coordination
3. **User Experience**: Use `/ui-validation` for loan application workflows and agent handoff experience

### Implementation Phase for Multi-Agent System
1. **Agent Personas**: Update markdown files in `loan_processing/agents/agent-persona/` following token optimization
2. **Quality Validation**: Run `uv run ruff check . --fix` and `uv run pytest` with coverage validation
3. **Agent Review**: Use `/code-quality` for multi-agent orchestration and MCP server integration feedback
4. **Framework Integration**: Ensure Microsoft Agent Framework ChatClientAgent compatibility

### Deployment Phase for Multi-Agent System
1. **MCP Servers**: Use `/cicd-help` to optimize deployment of all 3 MCP tool servers
2. **Quality Gates**: Ensure agent personas load correctly and MCP servers respond to tool calls
3. **Documentation**: Update loan processing documentation and agent integration examples
4. **Monitoring**: Implement observability for multi-agent workflow processing times and success rates

## Loan Processing Context Discovery

**When first activated, agents will understand**:

### Multi-Agent Loan Processing Domain
- **Business Context**: 5-agent loan processing system (intake, credit, income, risk, orchestrator)
- **User Personas**: Loan applicants, underwriters, loan officers (see `docs/ux/user-personas.md`)
- **Key Workflows**: Sequential agent processing with MCP tool integration
- **Success Metrics**: Loan processing accuracy, regulatory compliance, processing time

### Microsoft Agent Framework Architecture
- **Languages**: Python with Pydantic v2 for type-safe data models
- **Framework**: Microsoft Agent Framework with ChatClientAgent pattern
- **MCP Servers**: 3 external tool servers (verification, documents, calculations)
- **Tools**: uv package manager, ruff for linting/formatting, pytest for testing

### Loan Processing Quality Standards
- **Test Coverage**: ≥85% coverage on core loan processing modules
- **Performance**: Agent personas optimized for token efficiency (<500 lines each)
- **Security**: PII protection (applicant_id not SSN), audit trail requirements
- **Compliance**: Fair lending practices, bias prevention, regulatory documentation

## Multi-Agent System Activation
**Loan processing agents automatically understand** when chatmodes are used:
1. **Analyze Multi-Agent System**: Understand current agent personas, MCP server integration, workflow patterns
2. **Adapt to Microsoft Agent Framework**: Customize recommendations for ChatClientAgent patterns and persona optimization
3. **Apply Loan Processing Expertise**: Provide domain-specific guidance for regulatory compliance and business alignment
4. **Learn from Demonstrations**: Improve recommendations based on multi-agent loan processing effectiveness

## Multi-Agent Loan Processing Best Practices

1. **Agent Specialization**: Use chatmode agents for loan processing domain validation and Microsoft Agent Framework guidance
2. **Token Optimization**: Keep agent personas under 500 lines for 75% token reduction and 10x speed improvement
3. **Sequential Workflow Understanding**: Maintain clear context of Intake → Credit → Income → Risk → Orchestrator flow
4. **MCP Tool Integration**: Focus on how agents autonomously select appropriate external tools for assessments
5. **Microsoft Agent Framework Patterns**: Emphasize ChatClientAgent integration and direct persona loading
6. **Demonstration Focus**: Every feature should showcase viable multi-agent loan processing capabilities

Remember: This is a demonstration repository for Microsoft Agent Framework. Use chatmode agents to ensure every change showcases effective multi-agent loan processing patterns and framework integration.