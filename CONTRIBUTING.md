# Contributing to Loan Avengers

First off, thank you for considering contributing to Loan Avengers! It's people like you that make this project a great demonstration of multi-agent AI systems.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Code Contributions](#code-contributions)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. By participating, you are expected to uphold this standard. Please report unacceptable behavior to niksac@microsoft.com.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/niksacdev/loan-avengers/issues) to avoid duplicates.

**How to Submit a Bug Report**:

1. **Use the bug report template** when creating an issue
2. **Provide a clear title** describing the problem
3. **Include detailed steps to reproduce** the issue
4. **Describe expected vs actual behavior**
5. **Include your environment details**:
   - Python version
   - Operating system
   - Dependencies versions (from `uv.lock`)
6. **Add screenshots** if applicable
7. **Label the issue** with `bug`

### Suggesting Features

Feature suggestions are welcome! To suggest a feature:

1. **Check existing feature requests** to avoid duplicates
2. **Use the feature request template** when creating an issue
3. **Explain the problem** your feature would solve
4. **Describe your proposed solution**
5. **Consider alternatives** you've thought about
6. **Label the issue** with `enhancement`

### Code Contributions

We love code contributions! Here's how to get started:

1. **Find or create an issue** describing what you'll work on
2. **Comment on the issue** to claim it (avoid duplicate work)
3. **Fork the repository**
4. **Create a feature branch** from `main`
5. **Make your changes** following our style guidelines
6. **Add tests** for your changes
7. **Ensure all tests pass** locally
8. **Submit a pull request**

## Development Setup

### Prerequisites

- **Python 3.10+** (3.11 recommended)
- **Node.js 18+** (for UI development)
- **uv** package manager (for Python)
- **Azure OpenAI API** access (for testing with real agents)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/niksacdev/loan-avengers.git
   cd loan-avengers
   ```

2. **Install Python dependencies**:
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies
   cd apps/api
   uv sync --prerelease=allow
   ```

3. **Install UI dependencies** (if working on frontend):
   ```bash
   cd apps/ui
   npm install
   ```

4. **Configure environment**:
   ```bash
   # From repository root
   cp .env.example .env
   # Edit .env and add your Azure OpenAI credentials
   ```

5. **Run tests** to verify setup:
   ```bash
   cd apps/api
   uv run pytest ../../tests/ -v
   ```

### Development Workflow

#### Running the API Server

```bash
cd apps/api
uv run uvicorn loan_avengers.api.app:app --reload --host 0.0.0.0 --port 8000
```

#### Running the UI Development Server

```bash
cd apps/ui
npm run dev
```

#### Running MCP Servers

```bash
# Application Verification Server
uv run python -m loan_avengers.tools.mcp_servers.application_verification.server

# Document Processing Server
uv run python -m loan_avengers.tools.mcp_servers.document_processing.server

# Financial Calculations Server
uv run python -m loan_avengers.tools.mcp_servers.financial_calculations.server
```

### Running Tests

#### Python Tests

```bash
cd apps/api

# Run all tests
uv run pytest ../../tests/ -v

# Run specific test file
uv run pytest ../../tests/unit/test_models.py -v

# Run with coverage
uv run pytest ../../tests/ -v --cov=loan_avengers --cov-report=term-missing

# Run only fast tests (skip slow integration tests)
uv run pytest ../../tests/ -v -m "not slow"
```

#### UI Tests

```bash
cd apps/ui

# Run linting
npm run lint

# Run type checking
npm run type-check

# Build (verifies no errors)
npm run build

# Run tests (if available)
npm test
```

### Code Quality Checks (MANDATORY Before PR)

**Run these commands before submitting a PR**:

```bash
cd apps/api

# 1. Auto-fix linting issues
uv run ruff check . --fix

# 2. Auto-format code
uv run ruff format .

# 3. Run tests with coverage (must be ≥85%)
uv run pytest ../../tests/ -v --cov=loan_avengers --cov-report=term-missing

# 4. Type checking (optional but recommended)
uv run mypy loan_avengers/
```

If any of these fail, **fix the issues before creating your PR**.

## Pull Request Process

### Before Submitting

1. ✅ **Create or link to an issue** describing the change
2. ✅ **Run all pre-commit checks** (linting, formatting, tests)
3. ✅ **Ensure test coverage ≥85%** on modified code
4. ✅ **Update documentation** if needed
5. ✅ **Write clear commit messages** following our conventions

### PR Requirements

Every PR must:

1. **Link to a GitHub issue** (add "Closes #123" in description)
2. **Pass all CI checks** (tests, linting, type checking)
3. **Have ≥1 approval** from a maintainer
4. **Resolve all review conversations**
5. **Include tests** for new functionality
6. **Update docs** if changing public APIs

### PR Title Format

Use conventional commit format:

```
[#123] type: Brief description

Examples:
[#45] feat: Add income verification agent
[#67] fix: Correct credit score calculation
[#89] docs: Update deployment guide
[#12] test: Add integration tests for workflow
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### PR Description Template

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
- [ ] Coverage ≥85%

## Screenshots (if UI changes)
[Add screenshots here]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally (uv run pytest tests/ -v)
- [ ] Linting passes (uv run ruff check .)
- [ ] Formatting applied (uv run ruff format .)
- [ ] Documentation updated
- [ ] No merge conflicts
```

### Review Process

1. **Automated checks run** (GitHub Actions)
2. **Maintainer reviews** your code
3. **Address feedback** by pushing new commits
4. **Resolve conversations** when addressed
5. **Maintainer approves** when ready
6. **Auto-merge** or maintainer merges

### After Your PR is Merged

1. ✅ **Delete your feature branch** (GitHub does this automatically)
2. ✅ **Pull latest main** to your local repository
3. ✅ **Close linked issue** (if not auto-closed)
4. ✅ **Celebrate!** 🎉 Your contribution is live!

## Style Guidelines

### Python Code Style

We use **Ruff** for linting and formatting (configured in `pyproject.toml`):

- **Line length**: 120 characters max
- **Python version**: 3.10+ features allowed
- **Type hints**: Encouraged (using Pydantic for data models)
- **Docstrings**: Use for public functions (Google style)

**Key Conventions**:
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants
- Prefer Pydantic models over plain dictionaries
- Always validate user input with Pydantic

**Example**:
```python
from pydantic import BaseModel, Field

class LoanApplication(BaseModel):
    """Represents a loan application with validated fields."""

    applicant_id: str = Field(..., description="Unique applicant identifier")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")

    def calculate_dti(self) -> float:
        """Calculate debt-to-income ratio."""
        return self.monthly_debt / self.monthly_income
```

### JavaScript/TypeScript Style

We use **ESLint** and **Prettier** for UI code:

- **Functional components**: Prefer React hooks over class components
- **TypeScript**: Strongly typed, avoid `any`
- **File structure**: Components in `src/components/`, pages in `src/pages/`

### Git Commit Messages

Follow conventional commits format:

```
type(scope): Brief description

Longer description explaining the change in more detail.
Can span multiple lines.

Closes #123
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring (no behavior change)
- `chore`: Maintenance tasks

**Examples**:
```
feat(agents): Add risk assessment agent with MCP tool integration
fix(api): Correct session timeout calculation
docs(readme): Update setup instructions for Windows
test(workflow): Add integration tests for loan processing pipeline
```

### Documentation Style

- **README**: Clear setup and usage instructions
- **Inline comments**: Explain "why", not "what"
- **Docstrings**: Use Google-style for Python functions
- **Architecture decisions**: Document in `docs/decisions/adr-XXX.md`

## Project Structure

Understanding the codebase:

```
loan-avengers/
├── apps/
│   ├── api/                      # FastAPI backend
│   │   └── loan_avengers/
│   │       ├── agents/          # Agent personas and orchestration
│   │       ├── api/             # FastAPI endpoints
│   │       ├── models/          # Pydantic data models
│   │       └── tools/           # MCP servers
│   └── ui/                      # React/TypeScript frontend
│       └── src/
│           ├── components/      # React components
│           ├── pages/           # Page components
│           └── types/           # TypeScript types
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── docs/                        # Documentation
│   ├── decisions/              # ADRs (Architecture Decision Records)
│   ├── diagrams/               # Mermaid diagrams
│   └── guides/                 # User guides
└── .github/                    # GitHub configuration
    ├── workflows/              # CI/CD pipelines
    └── ISSUE_TEMPLATE/         # Issue templates
```

## Testing Guidelines

### Unit Tests

- **Test one thing** per test function
- **Use descriptive names**: `test_credit_agent_rejects_low_score`
- **Follow AAA pattern**: Arrange, Act, Assert
- **Mock external dependencies**: Use `pytest-mock`

**Example**:
```python
import pytest
from loan_avengers.models.application import LoanApplication

def test_loan_application_validates_positive_amount():
    """Loan amount must be positive."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError):
        LoanApplication(loan_amount=-1000, ...)
```

### Integration Tests

- **Test full workflows**: End-to-end agent coordination
- **Use realistic data**: Sample loan applications
- **Mark as slow**: Use `@pytest.mark.slow` decorator
- **May use real API calls**: But prefer mocks for speed

### Coverage Requirements

- **Minimum coverage**: 85% overall
- **Critical paths**: 100% coverage for security-sensitive code
- **New code**: Must maintain or improve coverage

## Community

### Getting Help

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Report bugs, request features
- **Security Issues**: Email niksac@microsoft.com (see SECURITY.md)

### Recognition

Contributors are recognized in:
- README.md acknowledgments section
- Release notes
- GitHub contributors page

## Questions?

If you have questions about contributing:

1. Check existing [issues](https://github.com/niksacdev/loan-avengers/issues)
2. Check [documentation](https://niksacdev.github.io/loan-avengers/)
3. Ask in [Discussions](https://github.com/niksacdev/loan-avengers/discussions)
4. Email: niksac@microsoft.com

---

**Thank you for contributing to Loan Avengers!** 🦸‍♂️

Your contributions help demonstrate the power of AI agent systems and inspire others to build with these technologies.
