# Claude Development Rules for Multi-Agent Loan Processing System

> **📋 Instruction Sync**: This is the **master reference** for all development practices. When updating, sync changes to `.github/instructions/copilot-instructions.md`. See `.github/sync-instructions.md` for guidelines.

## Project Overview
This is a **Multi-Agent Loan Processing System** demonstrating the use of **Microsoft Agent Framework** with MCP (Model Context Protocol) servers as tools. The system implements 5 specialized autonomous agents that process loan applications through a coordinated workflow from intake to final decision.

## Critical Lessons Learned

### Token Optimization Discovery
**Problem**: Large persona files (2000+ lines) causing excessive token consumption and 30+ second response times.
**Solution**: Reduced personas to 300-500 focused lines with clear directives.
**Result**: 75% token reduction, 10x faster agent responses.

### Prompt Optimization Best Practices
**Critical for Cost Management**: Use file references instead of inline code to minimize context window usage.

**Rules**:
1. **Never include code snippets** in instruction files - use: `See implementation: path/to/file.py:line-range`
2. **Reference documentation** instead of explaining - use: `See architecture: docs/decisions/adr-001.md`
3. **Cross-reference sections** instead of duplicating - use: `As defined in CLAUDE.md:Security-Guidelines`
4. **Keep instructions concise** - link to examples rather than embedding them

### Context Loss Prevention
**Problem**: After large refactoring sessions, Claude loses critical context and makes conflicting changes.
**Solutions**:
1. Use `/compact` command to consolidate conversations
2. Create git checkpoints after major changes
3. Provide explicit context anchoring for new sessions
4. Keep sessions to 2-3 hours instead of 8+ hour marathons

### Circular Debugging Detection
**Problem**: Agents repeat failed solutions in endless loops.
**Solution**: Track attempted fixes and request human intervention when loops detected.
**Human Role**: Provide strategic pivots and "be pragmatic" guidance.

## Development Support Agents (USE PROACTIVELY)

### Claude Agent Configuration
**Claude agents are configured in `.claude/agents/` directory**:
- This is the SOURCE OF TRUTH for Claude's agent implementations
- Use Task tool with appropriate `subagent_type` to invoke them
- Agents are loaded directly from these markdown files
- No dependency on `docs/developer-agents/` (that's reference only)

### Available Support Agents
Claude has access to specialized development agents that MUST be used proactively for brainstorming, design validation and implementation:

1. **system-architecture-reviewer** (`.claude/agents/system-architecture-reviewer.md`): 
   - USE WHEN: Designing new features, reviewing system architecture, analyzing impacts
   - PROVIDES: Architecture guidance, system design reviews, impact analysis

2. **product-manager-advisor** (`.claude/agents/product-manager-advisor.md`):
   - USE WHEN: Creating GitHub issues, defining requirements, making technical decisions
   - PROVIDES: Business value alignment, user story creation, test validation

3. **ux-ui-designer** (`.claude/agents/ux-ui-designer.md`):
   - USE WHEN: Designing UI components, validating user experience, creating interfaces
   - PROVIDES: Design validation, UI/UX improvements, usability analysis

4. **code-reviewer** (`.claude/agents/code-reviewer.md`):
   - USE WHEN: After writing significant code, before committing changes
   - PROVIDES: Best practices feedback, architecture alignment, code quality review

5. **agent-sync-coordinator** (Claude agent: `.claude/agents/`):
   - USE WHEN: **MANDATORY before ANY commit** that modifies instruction files, ADRs, or developer agents
   - PROVIDES: Ensures consistency across CLAUDE.md, GitHub Copilot instructions, and Cursor rules
   - **CRITICAL**: If you modify CLAUDE.md, ADRs, or developer agents, you MUST run this agent before committing
   - **HOW TO USE**: Use Task tool with `subagent_type: agent-sync-coordinator`

5. **gitops-ci-specialist**:
   - USE WHEN: Committing code, troubleshooting CI/CD issues, optimizing pipelines
   - PROVIDES: Git workflow guidance, CI/CD pipeline optimization, deployment strategies

6. **sync-coordinator**:
   - USE WHEN: Instruction files need synchronization, ADRs are added/changed
   - PROVIDES: Manual synchronization of instruction files across tools
   - NOTE: Developer-side only - run before committing instruction changes

### When to Use Support Agents

#### MANDATORY Usage:
- **Before Implementation**: Use system-architecture-reviewer for design validation
- **After Code Writing**: Use code-reviewer for all significant code changes
- **For UI Changes**: Use ux-ui-designer for any user-facing components
- **For Requirements**: Use product-manager-advisor when creating features or issues
- **Before ANY Commit with Instruction/ADR/Agent Changes**: Use agent-sync-coordinator to ensure consistency

#### Proactive Usage Pattern:
```
1. User requests feature → Use product-manager-advisor for requirements
2. Design solution → Use system-architecture-reviewer for validation  
3. Implement code → Write the implementation
4. Pre-commit checks → Run MANDATORY local quality checks (ruff, tests, coverage)
5. Review code → Use code-reviewer for feedback (AFTER checks pass)
6. If UI involved → Use ux-ui-designer for validation
```

## Architecture Principles

### 1. Agent Autonomy
- **Agents are autonomous**: Each agent decides which MCP tools to use based on their assessment needs
- **Persona-driven behavior**: Agent instructions are loaded from persona markdown files
- **No hardcoded logic**: Avoid embedding business logic in orchestrator code
- **Jobs-to-be-Done focused**: Agents designed around customer jobs, not internal processes
- **Strategic multi-agent choice**: Architecture designed for future growth - agents will gain intelligence as MCP servers expand from current 3 to planned 20+
- **Progressive autonomy**: Agents start simple but evolve independently without refactoring

### 2. Clean Orchestration
- **Minimal orchestrator code**: Orchestrators should only handle agent coordination and context passing
- **Use personas for instructions**: All agent-specific logic lives in persona files
- **Context accumulation**: Pass previous agent assessments as context to subsequent agents
- **Configuration-driven**: Define orchestration patterns in YAML, not code

### 3. MCP Server Integration
- **Tool selection by agents**: Agents autonomously select appropriate MCP servers based on needs
- **Secure parameters**: Always use `applicant_id` (UUID) instead of SSN for privacy compliance
- **Multiple server access**: Agents can access multiple MCP servers for comprehensive functionality

### 4. Token Optimization (CRITICAL)
- **Keep personas concise**: Target 300-500 lines, not 2000+
- **Focus on WHAT not HOW**: Clear directives over verbose explanations
- **Reference external docs**: Link to documentation instead of inline explanations
- **Result**: 75% token reduction, 10x faster responses

## Repository Architecture (Current)

### Directory Structure
```
loan_processing/
├── models/                           # Business data models (Pydantic v2)
│   ├── application.py               # LoanApplication model
│   ├── assessment.py               # Assessment result models
│   └── decision.py                 # LoanDecision model
├── agents/
│   └── agent-persona/              # Agent instruction markdown files
│       ├── intake-agent-persona.md
│       ├── credit-agent-persona.md
│       ├── income-agent-persona.md
│       ├── risk-agent-persona.md
│       └── orchestrator-agent-persona.md
├── tools/
│   ├── mcp_servers/                # MCP server implementations
│   │   ├── application_verification/
│   │   ├── document_processing/
│   │   └── financial_calculations/
│   └── services/                   # Business service interfaces
├── config/
│   └── agents.yaml                # Agent and MCP server configuration
└── utils/                         # Shared utilities
```

### Microsoft Agent Framework Integration
The system is designed for Microsoft Agent Framework with direct agent persona loading:

**Agent Personas**: Located in `loan_processing/agents/agent-persona/`
- Load directly as ChatClientAgent instructions
- Each persona contains specialized domain knowledge
- Optimized for token efficiency (300-500 lines each)

**Configuration**: See `loan_processing/config/agents.yaml`
- Maps agents to their required MCP servers
- Defines agent capabilities and output formats
- Used for tool configuration in Microsoft Agent Framework

### Agent Integration Pattern
```python
from microsoft_agent_framework import ChatClientAgent
from loan_processing.agents import get_persona_path

# Load agent persona
persona = open(get_persona_path("credit")).read()

# Create Microsoft Agent Framework agent
agent = ChatClientAgent(
    name="Credit Assessment Agent",
    instructions=persona
)
```

## Development Guidelines

### Pre-Commit Quality Checks (MANDATORY)

**CRITICAL**: Always run these checks locally BEFORE making any commit to prevent GitHub Actions failures.

#### Quick Validation
Run complete validation: `uv run python scripts/validate_ci_fix.py`
- See implementation: `scripts/validate_ci_fix.py`
- Automated in: `.github/workflows/test.yml`

#### Manual Checks
1. **Linting**: `uv run ruff check . --fix`
2. **Formatting**: `uv run ruff format .`
3. **Tests**: See test commands in `scripts/validate_ci_fix.py:64-78`
4. **Coverage**: Must be ≥85% on core modules

**⚠️ NEVER COMMIT if any checks fail. Fix issues locally first.**

#### Integration with Support Agents
- **ALWAYS run pre-commit checks** before using the code-reviewer agent
- **Include check results** when asking for agent feedback
- **Fix any issues** identified by checks before requesting code review

### IDE Configuration Notes

#### Cursor IDE (Current Structure)
Cursor uses a rules-based system with automatic context attachment:
- Rules stored in `.cursor/rules/` directory
- Files use `.mdc` format (Markdown with metadata)
- Rules auto-attach based on file patterns (globs)
- Hierarchical: subdirectories can have specific rules
- Use `.cursor/rules/*.mdc` files with YAML frontmatter

Project rules structure:
- `.cursor/rules/project-rules.mdc` - Always applied
- `.cursor/rules/agent-development.mdc` - Auto-attaches for agent files
- `.cursor/rules/testing.mdc` - Auto-attaches for test files
- `.cursor/rules/security.mdc` - Auto-attaches for sensitive files

#### VS Code / GitHub Copilot
- Uses `.github/instructions/copilot-instructions.md`
- Chatmodes in `.github/chatmodes/*.chatmode.md`

### Pre-Commit Synchronization (MANDATORY)

**CRITICAL**: Before committing ANY changes that modify instruction files:

1. **Check if sync is needed**: Did you modify any of:
   - CLAUDE.md
   - `docs/decisions/*.md` (ADRs - architectural changes)
   - `docs/developer-agents/*.md` (developer agent documentation)
   - `.claude/agents/*.md` (Claude agent implementations)
   - `.github/chatmodes/*.chatmode.md` (GitHub Copilot implementations)
   - `.cursor/rules/*.mdc` (Cursor implementations)
   - `.github/instructions/copilot-instructions.md`

2. **If yes, run agent-sync-coordinator**:
   - Use the Task tool with `subagent_type: agent-sync-coordinator`
   - Provide list of changed files and nature of changes
   - Apply any synchronization updates it recommends
   - Include sync changes in your commit
   - Agent location: `.claude/agents/agent-sync-coordinator.md`
   - Syncs between: `.claude/agents/`, `.github/chatmodes/`, `.cursor/rules/`

3. **Skip sync only if**:
   - No instruction files were modified
   - Changes are purely in code files
   - Commit message includes `[skip-sync]` flag

### Commit Best Practices

#### Branch Management (CRITICAL)
- **Always delete branches after PR merge**: Clean up both local and remote branches
- **Create new branch for new work**: Never reuse old feature branches
- **Branch naming**: Use descriptive names like `feat/feature-name` or `fix/bug-description`
- **Keep main clean**: Always work in feature branches, never commit directly to main

#### Commit Frequency (CRITICAL)
- **Commit often**: After each logical change (not after hours of work)
- **Atomic commits**: One logical change per commit
- **Small PRs**: Target 50-200 lines changed per PR
- **Test before commit**: Always run tests before committing

#### Good Commit Examples
```bash
# ✅ Good: Specific, focused commits
git commit -m "feat: add agent registry configuration loading"
git commit -m "test: add coverage for persona loading functionality" 
git commit -m "fix: update persona_loader path for shared directory"
git commit -m "docs: update cursor rules for new test patterns"

# ❌ Bad: Large, unfocused commits
git commit -m "update everything"
git commit -m "fix tests and update docs and refactor code"
```

#### Commit Message Format
```
<type>: <short description>

<optional longer description>
<optional breaking changes>
<optional issues closed>
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Support Agent Integration
- **ALWAYS consult appropriate support agents** before making significant changes
- **Use Task tool** to launch support agents with detailed prompts
- **Document agent recommendations** in commit messages or PR descriptions
- **Iterate based on feedback** from support agents before finalizing

### ADR Documentation for Support Agent Feedback
**MANDATORY**: When support agents provide feedback that leads to accepted changes, create an Architecture Decision Record:

- **Location**: `docs/decisions/adr-XXX-[descriptive-title].md`
- **Format**: Follow existing ADR template with Status, Context, Decision, Consequences, Implementation
- **Content Requirements**:
  - Document specific feedback received from support agents
  - Detail what changes were made and implementation approach
  - Explain rationale for decisions to help future developers
  - Include support agent assessment scores/grades when provided
  - List any outstanding issues identified but not yet addressed
  - Reference which support agents provided the feedback

**Purpose**: Create clear audit trail so future developers understand why architectural and implementation decisions were made

### 1. Adding New Agents
- Create persona markdown file in `loan_processing/agents/agent-persona/`
- Add agent configuration in `loan_processing/config/agents.yaml`
- Configure required MCP servers and capabilities
- Create Microsoft Agent Framework ChatClientAgent with persona as instructions
- Test with sample loan applications

### 2. Modifying Agent Behavior
- **Update persona files**, not code
- Personas are loaded directly into Microsoft Agent Framework
- Test with demo applications to verify behavior changes
- Keep personas focused and under 500 lines for optimal token usage

### 3. MCP Server Usage
- Agents select tools autonomously based on their persona instructions
- Configure MCP servers in `agents.yaml` for each agent type
- Ensure all MCP servers use secure parameters (applicant_id, not SSN)
- Connect MCP servers to Microsoft Agent Framework agents

### 4. Multi-Agent Workflow
- **Intake → Credit → Income → Risk → Orchestrator**: Sequential processing workflow
- Each agent processes LoanApplication and produces typed assessments
- Context and results passed between agents in the workflow
- Final orchestrator produces LoanDecision with complete audit trail

## Security & Privacy

### Critical Rules
1. **NEVER use SSN** in tool calls - always use `applicant_id`
2. **Secure all PII** - encrypt sensitive data in transit and at rest
3. **Audit logging** - maintain audit trails for all agent decisions
4. **Access control** - limit MCP server access to authorized agents only

## Testing Guidelines

### Package Manager: Use uv Only
**CRITICAL**: Always use `uv` for all package management and test execution:
- `uv add package` - Add dependencies
- `uv sync` - Install dependencies
- `uv run pytest` - Run tests
- `uv run python` - Run Python scripts
- Never use pip, poetry, or conda

### Current Test Status
Working tests should focus on:
- Data model validation (Pydantic models)
- Agent persona loading functionality
- MCP server configurations
- Microsoft Agent Framework integration patterns

### Test Commands
```bash
# Run tests with coverage (update paths as needed)
uv run pytest tests/ -v --cov=loan_processing --cov-report=term-missing

# Quick validation
uv run python scripts/validate_ci_fix.py

# Test specific components
uv run pytest tests/test_models.py -v
uv run pytest tests/test_agents.py -v
```

### 1. Data Model Tests
- Test LoanApplication validation and calculations
- Verify assessment model structures
- Test LoanDecision model with audit trails
- Validate Pydantic constraints and business rules

### 2. Agent Integration Tests
- Test persona loading from markdown files
- Verify Microsoft Agent Framework integration
- Test agent configuration loading from YAML
- Validate MCP server connection patterns

### 3. Workflow Integration Tests
- Test complete loan processing workflow
- Verify agent coordination and context passing
- Test error handling and edge cases
- Validate final decision generation with audit trails

## Performance Considerations

### 1. Agent Efficiency
- Keep agent personas under 500 lines for optimal token usage
- Use appropriate model sizes in Microsoft Agent Framework
- Cache MCP server responses when appropriate
- Design agents for specific domain expertise to minimize processing time

### 2. Workflow Optimization
- Sequential processing: Intake → Credit → Income → Risk → Orchestrator
- Minimize context size passed between agents in the workflow
- Implement timeout handling for long-running agent operations
- Use structured data models to reduce token usage between agents

## Maintenance & Evolution

### 1. Persona Updates
- Review and update personas based on business requirements
- Version control persona changes
- Test thoroughly after persona modifications

### 2. Adding MCP Servers
- Create new MCP server following existing patterns
- Update relevant agents to include new server access
- Document new tool capabilities in agent personas

### 3. Monitoring & Observability
- Log all agent decisions and tool usage
- Track processing times and success rates
- Monitor MCP server availability and performance

## Instruction File Synchronization

### Developer-Side Synchronization Process

This repository uses **developer-side synchronization** to maintain consistency across all instruction files. When you update CLAUDE.md, ADRs, or developer agents, you must run the sync coordinator agent to update related files before committing.

### How It Works

1. **Developer-side Trigger**: Before committing changes to instruction files:
   - `docs/decisions/*.md` (ADRs)
   - `CLAUDE.md` (this file)
   - `docs/developer-agents/*.md`
   - `.github/instructions/copilot-instructions.md`
   - `.claude/agents/*.md` or `.github/chatmodes/*.md`

2. **Manual Sync Process**: Developer runs sync agent and:
   - Uses Task tool with `subagent_type: agent-sync-coordinator`
   - Agent analyzes git changes and recommends updates
   - Developer applies suggested changes
   - Commits all changes together in single commit

3. **No CI/CD dependency**: Entirely developer-side, provider-agnostic

### Synchronization Hierarchy

When conflicts arise, this hierarchy determines source of truth:

1. **ADRs** - Architecture decisions override everything
2. **CLAUDE.md** - Primary source for development practices (this file)
3. **Developer agents** - Domain-specific expertise
4. **Copilot instructions** - Derived from above sources
5. **Chatmodes** - Tool-specific implementations

### Manual Override

- Add `[skip-sync]` to commit message to skip synchronization
- Run workflow manually via Actions tab if needed
- Sync agent preserves natural language and tool-specific features

### What Gets Synchronized

**Automatically synchronized**:
- Development standards and practices
- Agent invocation patterns  
- Quality gates and pre-commit checks
- Workflow definitions
- Architecture principles from ADRs

**NOT synchronized** (tool-specific):
- IDE-specific configurations
- Tool-specific command patterns (e.g., `/commands`)
- Platform installation instructions
- Tool UI references

See [ADR-003](docs/decisions/adr-003-instruction-synchronization.md) for detailed synchronization strategy.

## Development Workflows with Support Agents

### Feature Development Workflow
```
1. User Request → Use product-manager-advisor:
   - Analyze requirements and business value
   - Create proper GitHub issues
   - Define acceptance criteria

2. Design Phase → Use system-architecture-reviewer:
   - Review proposed architecture changes
   - Analyze system impacts
   - Validate design decisions

3. Implementation → Write code following patterns

4. Pre-Commit Validation (MANDATORY) → Run local quality checks:
   - uv run ruff check . --fix (auto-fix issues)
   - uv run ruff format . (auto-format)
   - uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
   - Verify ≥85% coverage on core components

5. Code Review → Use code-reviewer (ONLY after checks pass):
   - Review for best practices
   - Check architecture alignment
   - Validate code quality

6. UI Components → Use ux-ui-designer (if applicable):
   - Review user experience
   - Validate interface design
   - Ensure usability standards

7. Document Decisions → Create ADR (MANDATORY):
   - Document context and changes made based on support agent feedback
   - Explain rationale for future developers
   - Include support agent assessments and scores
   - Track outstanding issues for future implementation
```

### Bug Fix Workflow
```
1. Issue Analysis → Use system-architecture-reviewer:
   - Understand system impact
   - Identify root cause areas

2. Solution Design → Use product-manager-advisor:
   - Validate business impact
   - Prioritize fix approach

3. Implementation → Write fix

4. Pre-Commit Validation (MANDATORY) → Run local quality checks:
   - uv run ruff check . --fix (auto-fix issues)
   - uv run ruff format . (auto-format)
   - uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
   - Verify fix doesn't break existing functionality

5. Review → Use code-reviewer (ONLY after checks pass):
   - Ensure fix doesn't introduce regressions
   - Validate approach

6. Document Fix → Create ADR (if significant):
   - Document root cause analysis from support agents
   - Explain solution approach and alternatives considered
   - Record lessons learned for future similar issues
```

## GitHub Issue Management (MANDATORY)

### Core Principle
**NO CODE WITHOUT AN ISSUE. NO PR WITHOUT A LINKED ISSUE.**

Every code change must be tracked through a GitHub issue for transparency, traceability, and team coordination.

### When to Create Issues

#### ALWAYS Create an Issue For:
1. **New Features** - Any new functionality or capability
2. **Bug Fixes** - Even small bugs need tracking
3. **Refactoring** - Code improvements or technical debt
4. **Documentation** - New docs or significant updates
5. **Infrastructure** - CI/CD, deployment, configuration changes
6. **Dependencies** - Upgrading or adding packages

#### Exception (Create Issue Retroactively):
- Urgent hotfixes (create issue immediately after deploying)
- Typo fixes in comments (optional)

### Issue Structure Best Practices

#### 1. Use Product-Manager-Advisor BEFORE Creating Issues
**MANDATORY for all feature/enhancement issues:**
```
Before creating GitHub issues, use Task tool with:
  subagent_type: product-manager-advisor
  prompt: "Help me create GitHub issues for [feature description].
          Context: [user need, business value, technical constraints]"
```

The advisor will:
- Help clarify requirements
- Suggest proper issue breakdown
- Define acceptance criteria
- Add business context
- Recommend size estimates

#### 2. Issue Size Guidelines
Break down issues to keep them manageable:
- **Small** (1-3 days): Single component, clear scope, minimal dependencies
- **Medium** (4-7 days): Multiple related changes, some complexity
- **Large** (8+ days): Break into Epic with sub-issues

**Rule**: If an issue takes >1 week, create an Epic and sub-issues.

#### 3. Required Issue Components

**Every Issue Must Have:**
```markdown
## Overview
[1-2 sentence description]

## Context
- Why is this needed?
- What problem does it solve?
- Reference to product docs/ADRs if applicable

## Acceptance Criteria
- [ ] Specific testable criterion 1
- [ ] Specific testable criterion 2
- [ ] Specific testable criterion 3

## Technical Requirements
- Technology/framework constraints
- Performance requirements
- Security considerations

## Definition of Done
- [ ] Code implemented and tested
- [ ] Tests pass with ≥85% coverage
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] PR merged to main

## Dependencies
- Blocked by: #XX (if applicable)
- Blocks: #YY (if applicable)

## Related Documentation
- Link to product docs
- Link to ADRs
- Link to design docs
```

#### 4. Labels (Required)

**Every issue MUST have at least 3 labels:**
1. **Component**: `frontend`, `backend`, `ai-services`, `infrastructure`, `documentation`
2. **Size**: `size: small`, `size: medium`, `size: large`, `epic`
3. **Phase**: `phase-1-mvp`, `phase-2-enhanced`, etc.

**Optional but Recommended:**
- **Priority**: `priority: high`, `priority: medium`, `priority: low`
- **Type**: `bug`, `enhancement`, `good first issue`
- **Team**: `team: frontend`, `team: backend`

#### 5. Milestones (Required for Sprint Planning)
- Assign every issue to a milestone
- Milestones represent sprints or phases
- Update milestone progress weekly

### Epic Management

**When to Create an Epic:**
- Feature requires 2+ weeks of work
- Feature has 3+ sub-tasks
- Multiple team members will work on different parts

**Epic Structure:**
```
Issue Title: [EPIC] Feature Name
Labels: epic, size: large, [component], [phase]

Body:
## Overview
High-level feature description

## Sub-Issues
- [ ] #XX - Sub-task 1 (owner: @username)
- [ ] #YY - Sub-task 2 (owner: @username)
- [ ] #ZZ - Sub-task 3 (owner: @username)

## Progress
- Total: 3 sub-issues
- Completed: 1 (33%)
- Remaining: 2

## Definition of Done
- All sub-issues completed
- Integration testing passed
- Documentation complete
```

### Pull Request Rules (ENFORCED)

#### 1. Every PR Must Link to an Issue
**Format in PR description:**
```markdown
Closes #123
Fixes #456
Relates to #789
```

**GitHub will:**
- Auto-close issue when PR merges (if using "Closes" or "Fixes")
- Link PR to issue for traceability
- **Block PR merge if no issue linked** (via branch protection rule)

#### 2. PR Title Format
```
[#123] Brief description of change

Examples:
[#24] Implement conversation state machine
[#31] Add progress card component with 4 states
[#bug-456] Fix authentication token expiration
```

#### 3. PR Description Must Include
```markdown
## Related Issue
Closes #XXX

## Changes Made
- Bullet list of changes
- What was added/modified/removed

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Screenshots (if UI)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows project conventions
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No merge conflicts
```

### GitHub Branch Protection Rules

**Main branch protection (ENFORCED):**
1. ✅ Require pull request before merging
2. ✅ Require status checks to pass:
   - CI tests must pass
   - Code coverage ≥85%
   - Ruff linting passes
3. ✅ **Require linked issue** (via GitHub Actions check)
4. ✅ Require code review approval (1+ reviewer)
5. ✅ Dismiss stale reviews when new commits pushed
6. ✅ Require conversation resolution before merge
7. ❌ Allow force pushes (disabled)
8. ❌ Allow deletions (disabled)

**See**: `.github/workflows/require-linked-issue.yml` for enforcement

### Issue Workflow States

**Use GitHub Projects to track:**
1. **Backlog** - Not yet prioritized
2. **Ready** - Prioritized, no blockers, ready to start
3. **In Progress** - Actively being worked on
4. **In Review** - PR submitted, awaiting review
5. **Done** - PR merged, issue closed

**Update issue status when:**
- Starting work: Comment "Starting work on this" and move to In Progress
- Creating PR: Link PR and move to In Review
- PR merged: Issue auto-closes and moves to Done

### Common Mistakes to Avoid

❌ **DON'T**:
- Start coding without creating an issue first
- Create vague issues ("Improve performance")
- Skip acceptance criteria
- Forget to link PRs to issues
- Create issues that are too large (>2 weeks)
- Work on issues without assigning yourself

✅ **DO**:
- Use product-manager-advisor to help create well-structured issues
- Break large features into Epic + sub-issues
- Link all related issues (blocks/blocked-by)
- Assign issues to yourself when starting work
- Update issue with progress comments
- Close issues only when Definition of Done is met

## Common Patterns

### Multi-Agent Workflow Processing
```python
# Sequential agent workflow pattern
application = LoanApplication(...)

# 1. Intake Agent - validates and routes
intake_result = await intake_agent.run(application.model_dump())

# 2. Credit Agent - analyzes creditworthiness
credit_result = await credit_agent.run(application.model_dump())

# 3. Income Agent - verifies income and employment
income_result = await income_agent.run(application.model_dump())

# 4. Risk Agent - synthesizes assessments
risk_result = await risk_agent.run({
    "application": application.model_dump(),
    "credit_assessment": credit_result,
    "income_assessment": income_result
})

# 5. Orchestrator - final decision
decision = await orchestrator_agent.run({
    "application": application.model_dump(),
    "assessments": [credit_result, income_result, risk_result]
})
```

### Error Handling
- Handle Microsoft Agent Framework exceptions and timeouts
- Implement fallback strategies for MCP server failures
- Retry logic for temporary agent or tool failures
- Graceful degradation when external services are unavailable

### Context Management (Loss Prevention)
**Best Practices**:
- Use `/compact` command after large refactoring sessions
- Create git checkpoints: `git commit -m "checkpoint: refactoring complete"`
- Provide explicit context anchoring for new sessions
- Document key changes when switching tasks

### Debugging Circular Loops
- Track attempted fixes to detect repetition
- Request human intervention when loops detected
- Apply "be pragmatic" guidance from humans
- Focus on incremental improvements rather than complete rewrites

## Best Practices

1. **Use support agents proactively** - Consult architecture, PM, design, and code review agents
2. **Keep orchestrators thin** - Business logic in personas, not code
3. **Optimize token usage** - Keep personas under 500 lines for 10x speed improvement
4. **Manage context actively** - Use /compact and checkpoints to prevent context loss
5. **Validate with experts** - Use system-architecture-reviewer before implementing
6. **Review all code** - Use code-reviewer agent after writing significant code
7. **Define requirements properly** - Use product-manager-advisor for feature planning
8. **Design user experiences** - Use ux-ui-designer for any user-facing components
9. **Document tool usage** - Clear descriptions in agent personas
10. **Test comprehensively** - Unit, integration, and end-to-end tests
11. **Monitor for loops** - Detect circular debugging and request human intervention
12. **Focus sessions** - Keep to 2-3 hour focused sessions over 8+ hour marathons
13. **Iterate on personas** - Continuously improve based on outcomes

## Quick Reference

### Key Files
- Agent Personas: `loan_processing/agents/agent-persona/*.md`
- Data Models: `loan_processing/models/*.py`
- Agent Configuration: `loan_processing/config/agents.yaml`
- MCP Servers: `loan_processing/tools/mcp_servers/*/server.py`
- Business Utils: `loan_processing/utils/*.py`

### Common Commands
```bash
# Package Management (Use uv for all package operations)
uv sync                     # Install dependencies
uv add package_name        # Add new dependency
uv add --dev package_name  # Add development dependency

# Run MCP servers
uv run python -m loan_processing.tools.mcp_servers.application_verification.server
uv run python -m loan_processing.tools.mcp_servers.document_processing.server
uv run python -m loan_processing.tools.mcp_servers.financial_calculations.server

# Run tests
uv run pytest tests/ -v                                    # All tests
uv run pytest tests/test_models.py -v                     # Data model tests
uv run pytest tests/ --cov=loan_processing                # With coverage

# Test validation
uv run python scripts/validate_ci_fix.py                  # Quick validation
```

### Environment Variables
- Microsoft Agent Framework API credentials (as required by the framework)
- `MCP_SERVER_HOST`: Host for MCP servers (default: localhost)
- `MCP_SERVER_PORTS`: Port configuration for MCP servers (8010, 8011, 8012)

### Success Criteria
- All tests pass with >85% coverage on core modules
- Agent personas load correctly into Microsoft Agent Framework
- MCP servers start and respond to tool calls
- Complete loan workflow produces valid LoanDecision outputs