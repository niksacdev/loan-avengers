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

## GitHub Issue Management (MANDATORY)

### Core Principle
**NO CODE WITHOUT AN ISSUE. NO PR WITHOUT A LINKED ISSUE.**

Every code change must be tracked through a GitHub issue for transparency, traceability, and team coordination.

### When to Create Issues

#### ALWAYS Create an Issue For:
1. **New Features** - Any new loan processing functionality or agent capability
2. **Bug Fixes** - Even small bugs need tracking for audit trails
3. **Agent Updates** - Refactoring agent personas or MCP server integration
4. **Documentation** - New docs or significant updates to loan processing guides
5. **Infrastructure** - CI/CD, deployment, multi-agent system configuration changes
6. **Dependencies** - Upgrading or adding packages for Microsoft Agent Framework

#### Exception (Create Issue Retroactively):
- Urgent hotfixes (create issue immediately after deploying)
- Typo fixes in comments (optional)

### Issue Structure Best Practices

#### 1. Use `/pm-requirements` Chatmode BEFORE Creating Issues
**MANDATORY for all feature/enhancement issues:**
```
Use the chatmode command:
  /pm-requirements "Help me create GitHub issues for [loan processing feature].
                   Context: [user need, business value, technical constraints]"
```

The advisor will:
- Help clarify loan processing requirements
- Suggest proper issue breakdown for multi-agent system
- Define acceptance criteria with regulatory compliance
- Add business context and user impact analysis
- Recommend size estimates based on agent workflow complexity

#### 2. Issue Size Guidelines
Break down issues to keep them manageable:
- **Small** (1-3 days): Label `size: small` - Single agent/component, clear scope, minimal dependencies
- **Medium** (4-7 days): Label `size: medium` - Multiple agent changes, some complexity
- **Large** (8+ days): Label `epic` + `size: large` - Break into Epic with sub-issues

**Rule**: If an issue takes >1 week, create an Epic with sub-issues.

#### 3. Required Issue Components

**Every Issue Must Have:**
```markdown
## Overview
[1-2 sentence description of loan processing feature]

## Context
- Why is this needed for loan processing workflow?
- What problem does it solve for users/agents?
- Reference to product docs/ADRs if applicable

## Acceptance Criteria
- [ ] Specific testable criterion 1 (with agent behavior)
- [ ] Specific testable criterion 2 (with expected outcome)
- [ ] Specific testable criterion 3 (with success metric)

## Technical Requirements
- Agent/framework constraints (Microsoft Agent Framework)
- MCP server integration needs
- Performance requirements (token optimization, response time)
- Security considerations (PII protection, audit trails)

## Definition of Done
- [ ] Code implemented and tested
- [ ] Tests pass with ≥85% coverage
- [ ] Agent personas optimized (<500 lines)
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] PR merged to main

## Dependencies
- Blocked by: #XX (if applicable)
- Blocks: #YY (if applicable)

## Related Documentation
- Link to docs/product/ (business context)
- Link to docs/decisions/ (ADRs)
- Link to docs/agent-patterns.md (integration examples)
```

#### 4. Labels (Required - Minimum 3)

**Every issue MUST have at least 3 labels:**
1. **Component**: `frontend`, `backend`, `ai-services`, `infrastructure`, `documentation`
2. **Size**: `size: small`, `size: medium`, `size: large`, `epic`
3. **Phase**: `phase-1-mvp`, `phase-2-enhanced`, etc.

**Optional but Recommended:**
- **Priority**: `priority: high`, `priority: medium`, `priority: low`
- **Type**: `bug`, `enhancement`, `good first issue`
- **Agent**: `agent: intake`, `agent: credit`, `agent: risk` (for agent-specific work)

#### 5. Milestones (Required for Sprint Planning)
- Assign every issue to a milestone
- Milestones represent sprints or development phases
- Update milestone progress weekly

### Epic Management for Large Features

**When to Create an Epic:**
- Feature requires 2+ weeks of work
- Feature has 3+ sub-tasks across multiple agents
- Multiple team members will work on different parts

**Epic Structure:**
```markdown
Issue Title: [EPIC] Multi-Agent Feature Name

Labels: epic, size: large, [component], [phase]

## Overview
High-level feature description for loan processing system

## Business Value
- User impact: [loan officers, underwriters, applicants]
- Processing efficiency: [time savings, accuracy improvement]
- Strategic alignment: [Microsoft Agent Framework demonstration goals]

## Sub-Issues
- [ ] #XX - [Sub-task 1] (Est: 3 days) (Owner: @username)
- [ ] #YY - [Sub-task 2] (Est: 2 days) (Owner: @username)
- [ ] #ZZ - [Sub-task 3] (Est: 4 days) (Owner: @username)

## Progress
- Total: 3 sub-issues
- Completed: 1 (33%)
- Remaining: 2

## Definition of Done
- [ ] All sub-issues completed
- [ ] Integration testing passed across agents
- [ ] End-to-end loan processing workflow validated
- [ ] Documentation complete
```

### Pull Request Rules (ENFORCED by GitHub Actions)

#### 1. Every PR Must Link to an Issue
**Format in PR description:**
```markdown
Closes #123
Fixes #456
Relates to #789
```

**GitHub Actions will:**
- Check for issue links in PR body or title
- **Block PR merge if no issue linked** (via `.github/workflows/require-linked-issue.yml`)
- Post helpful comment with fix instructions if check fails

#### 2. PR Title Format
```
[#123] Brief description of multi-agent change

Examples:
[#24] Implement agent persona token optimization
[#31] Add MCP server integration for income verification
[#bug-456] Fix credit assessment scoring calculation
```

#### 3. PR Description Template
```markdown
## Related Issue
Closes #XXX

## Changes Made
- Updated credit agent persona for better token efficiency
- Added MCP server integration for document verification
- Modified risk assessment calculations

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass with ≥85% coverage
- [ ] Manual testing with sample loan applications

## Agent Impact
[Which agents are affected and how]

## Checklist
- [ ] Code follows project conventions
- [ ] Agent personas optimized (<500 lines)
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No merge conflicts
```

### Common Mistakes to Avoid

❌ **DON'T**:
- Start coding multi-agent features without creating an issue first
- Create vague issues ("Improve agent performance")
- Skip acceptance criteria for loan processing requirements
- Forget to link PRs to issues (will fail GitHub Actions check)
- Create issues that are too large (>2 weeks without Epic breakdown)
- Work on issues without assigning yourself

✅ **DO**:
- Use `/pm-requirements` chatmode to create well-structured issues
- Break large multi-agent features into Epic + sub-issues
- Link all related issues (blocks/blocked-by)
- Assign issues to yourself when starting work
- Update issue with progress comments
- Close issues only when Definition of Done is met
- Consider agent workflow implications in issue planning