# 🧪 Intake Agent Testing Suite

A comprehensive testing suite for the IntakeAgent and MCP validation system with unit and integration tests.

## 📁 Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── README.md                        # This file
├── test_suite_runner.py            # Convenient test runner script
├── unit/                           # Unit tests (isolated, mocked)
│   ├── agents/
│   │   └── test_intake_agent.py    # IntakeAgent unit tests
│   ├── tools/
│   │   └── test_application_verification_service.py  # MCP service tests
│   └── models/
│       └── test_application_models.py  # Data model tests
└── integration/                    # Integration tests (real dependencies)
    └── test_intake_agent_integration.py  # End-to-end integration tests
```

## 🚀 Quick Start

### Prerequisites
```bash
# Install test dependencies (already included in pyproject.toml)
uv sync --dev
```

### Run Tests

```bash
# Run all unit tests (fast, no external dependencies)
uv run pytest tests/unit/ -v

# Run specific test categories
uv run pytest tests/unit/agents/ -v          # Intake agent tests
uv run pytest tests/unit/tools/ -v           # MCP service tests  
uv run pytest tests/unit/models/ -v          # Data model tests

# Run with coverage
uv run pytest tests/ --cov=loan_defenders --cov-report=term-missing

# Run using the test suite runner
uv run python tests/test_suite_runner.py

# Generate detailed coverage analysis
uv run python tests/coverage_report.py
```

## 📊 Coverage Metrics & Analysis

### Coverage Targets by Module
```
Module                        Target   Purpose
loan_defenders/agents/         90.0%    Core business logic - high coverage required
loan_defenders/models/         95.0%    Data models - critical validation
loan_defenders/tools/services/ 85.0%    Service interfaces - important contracts
loan_defenders/tools/mcp_servers/ 75.0% MCP servers - has external dependencies  
loan_defenders/utils/          80.0%    Utilities - medium coverage
loan_defenders/config/         70.0%    Configuration - lower coverage acceptable
```

### Coverage Commands

#### Basic Coverage
```bash
# Run unit tests with coverage
uv run pytest tests/unit/ --cov=loan_defenders --cov-report=term-missing

# Generate HTML report
uv run pytest tests/unit/ --cov=loan_defenders --cov-report=html:htmlcov

# Generate JSON + XML reports  
uv run pytest tests/unit/ --cov=loan_defenders --cov-report=json --cov-report=xml
```

#### Advanced Coverage Analysis
```bash
# Interactive coverage analysis (menu driven)
uv run python tests/coverage_report.py

# Direct commands
uv run python tests/coverage_report.py run         # Run tests + generate reports
uv run python tests/coverage_report.py analyze     # Analyze existing coverage
uv run python tests/coverage_report.py check       # Check coverage requirements  
uv run python tests/coverage_report.py report      # Detailed analysis report

# Using test suite runner (enhanced menu)
uv run python tests/test_suite_runner.py
# Choose option 7: Tests with coverage
# Choose option 10: Coverage analysis  
# Choose option 11: Coverage check
```

#### Coverage Reports Available
- **Terminal**: Real-time coverage with missing lines
- **HTML**: Interactive web report at `htmlcov/index.html`
- **JSON**: Machine-readable at `coverage.json`
- **XML**: CI/CD compatible at `coverage.xml`

### Coverage Analysis Features

#### Module-by-Module Analysis
- ✅ **Coverage by module** with specific targets
- 📊 **Line vs Branch coverage** breakdown
- 🎯 **Gap analysis** showing what's needed to meet targets
- 📁 **File-level details** for modules below target

#### Actionable Recommendations  
- 🔍 **Priority order** for improving coverage
- 📋 **Specific missing lines** to focus on
- 💡 **Type of tests needed** (lines vs branches)
- 📈 **Quantified goals** (e.g., "need +15 more covered lines")

#### Quality Gates
- ❌ **Fail if overall coverage < 85%**
- ❌ **Fail if any module below its target**
- ✅ **Pass only when all requirements met**
- 🚀 **Perfect for CI/CD pipelines**

### Sample Coverage Analysis Output

```
📊 DETAILED COVERAGE ANALYSIS
================================================================================

🎯 OVERALL COVERAGE: 87.32%
   Target: 85.00%
   Status: ✅ MEETS TARGET

📂 MODULE COVERAGE ANALYSIS
--------------------------------------------------------------------------------
Module                         Coverage    Target     Status     Gap       
--------------------------------------------------------------------------------
loan_defenders/agents/          78.45%      90.0%      ❌ FAIL    -11.6%    
loan_defenders/models/          96.23%      95.0%      ✅ PASS              
loan_defenders/tools/services/  82.14%      85.0%      ❌ FAIL    -2.9%     
loan_defenders/utils/           85.67%      80.0%      ✅ PASS              

🔍 DETAILED ANALYSIS FOR MODULES BELOW TARGET
--------------------------------------------------------------------------------

📁 loan_defenders/agents/
   Line Coverage: 76.22% (45/59)
   Branch Coverage: 83.33% (5/6)
   Files: 2
   Top Missing Lines:
     - loan_defenders/agents/intake_agent.py:145
     - loan_defenders/agents/intake_agent.py:150
     - loan_defenders/agents/intake_agent.py:155

💡 RECOMMENDATIONS
--------------------------------------------------------------------------------
Priority order for improving coverage:
1. loan_defenders/agents/ (need +11.6% coverage)
   → Focus on adding tests for uncovered lines
   → Add ~7 more covered lines

2. loan_defenders/tools/services/ (need +2.9% coverage)  
   → Focus on adding tests for edge cases and branches
   → Add ~2 more covered lines

📈 DETAILED REPORTS AVAILABLE:
   HTML Report: file:///path/to/htmlcov/index.html
   JSON Report: coverage.json
   XML Report: coverage.xml
```

### Unit Tests (`tests/unit/`)
- **Fast execution** (< 1 second per test)
- **Isolated** - uses mocks for external dependencies
- **No Azure OpenAI** - mocked chat client
- **No MCP server** - mocked MCP tools
- **High coverage** - focuses on business logic

#### Intake Agent Unit Tests
- ✅ Initialization with/without custom chat client
- ✅ MCP tool configuration
- ✅ Application processing workflow
- ✅ Error handling and fallback assessments
- ✅ Message formatting and JSON serialization
- ✅ Conversation thread support

#### MCP Service Unit Tests  
- ✅ `validate_basic_parameters` method
- ✅ Completeness score calculation
- ✅ Routing recommendations (VIP/STANDARD/ENHANCED)
- ✅ Required field validation
- ✅ Format validation (email, amounts)
- ✅ Error handling for invalid JSON
- ✅ Legacy MCP tool methods

#### Data Model Unit Tests
- ✅ Pydantic validation rules
- ✅ Field constraints and patterns
- ✅ JSON serialization/deserialization
- ✅ Business logic methods (DTI ratio, etc.)
- ✅ Enum validation

### Integration Tests (`tests/integration/`)
- **Slower execution** (may require setup)
- **Real dependencies** - actual MCP server, Azure OpenAI
- **End-to-end workflows** - complete system integration
- **Performance testing** - <5 second requirement validation

#### Integration Test Categories
- 🔄 **MCP Integration**: Real MCP server connection
- 🤖 **Agent Integration**: Full IntakeAgent with Azure OpenAI
- ⚡ **Performance**: <5 second processing time validation
- 🔧 **Error Handling**: MCP server unavailability scenarios

> **Note**: Integration tests are marked with `@pytest.mark.integration` and most are currently skipped pending Azure OpenAI configuration.

## 📈 Test Status

### Current Status
- **35 tests** collected across unit and integration suites
- **Unit tests**: 25 tests, some failing due to fixtures (being fixed)
- **Integration tests**: 10 tests, mostly skipped (require Azure/MCP setup)
- **Coverage target**: ≥85% for core modules

### Known Issues Being Fixed
1. Some unit test fixtures need adjustment for AgentRunResponse format
2. JSON serialization handling for datetime objects in tests
3. Azure OpenAI mock client configuration
4. Integration tests need running MCP server

## 🎯 Test Fixtures

### Available in `conftest.py`
- `sample_loan_application` - Complete valid application
- `vip_loan_application` - High-income application (fast-track)
- `incomplete_loan_application` - Missing optional fields
- `sample_intake_assessment` - Valid assessment response
- `mock_azure_chat_client` - Mocked Azure OpenAI client
- `sample_agent_thread` - Conversation thread for context testing
- `mock_mcp_validation_result*` - Various MCP validation responses

## 🔧 Running Specific Test Scenarios

### Test the Validation Logic
```bash
# Test just the core validation service
uv run pytest tests/unit/tools/test_application_verification_service.py::TestApplicationVerificationServiceImpl::test_validate_basic_parameters_complete_application -v

# Test routing recommendations
uv run pytest tests/unit/tools/ -k "routing_recommendations" -v
```

### Test the Agent Integration
```bash
# Test agent initialization
uv run pytest tests/unit/agents/ -k "test_init" -v

# Test message formatting
uv run pytest tests/unit/agents/ -k "message" -v
```

### Test Data Models
```bash
# Test Pydantic validation
uv run pytest tests/unit/models/ -k "validation" -v

# Test business logic methods
uv run pytest tests/unit/models/ -k "ratio" -v
```

## ⚡ Performance Testing

Performance tests validate the **<5 second processing requirement**:

```bash
# Run performance tests (requires full setup)
uv run pytest tests/ -m "performance" -v

# These tests are currently skipped pending Azure OpenAI setup
```

## 🧪 Test Development Guidelines

### Adding New Tests

1. **Unit tests** for new business logic
2. **Mock external dependencies** (Azure OpenAI, MCP servers)
3. **Use fixtures** from `conftest.py`
4. **Follow naming convention**: `test_<functionality>_<scenario>`

### Test Categories
- Use `@pytest.mark.integration` for integration tests
- Use `@pytest.mark.performance` for performance tests
- Use `@pytest.mark.skip(reason="...")` for tests requiring setup

### Fixture Guidelines
- **Create reusable fixtures** in `conftest.py`
- **Keep test data realistic** but minimal
- **Mock external services** for unit tests
- **Use async fixtures** for async code

## 📝 Example Usage

```python
# Unit test example
async def test_intake_validation(service, sample_loan_application):
    """Test basic validation with complete application."""
    app_json = sample_loan_application.model_dump_json()
    result = await service.validate_basic_parameters(app_json)
    
    assert result["validation_status"] == "VALID"
    assert result["routing_recommendation"] == "STANDARD"

# Integration test example  
@pytest.mark.integration
@pytest.mark.skip(reason="Requires Azure OpenAI configuration")
async def test_full_intake_workflow(vip_loan_application):
    """Test complete intake workflow with VIP application."""
    agent = IntakeAgent()
    result = await agent.process_application(vip_loan_application)
    
    assert result["assessment"]["routing_decision"] == "FAST_TRACK"
```

## 🎉 Success Criteria

- ✅ **All unit tests pass** without external dependencies
- ✅ **Integration tests work** with proper configuration  
- ✅ **≥85% code coverage** on core modules
- ✅ **Performance tests validate** <5 second requirement
- ✅ **Error scenarios handled** gracefully

The testing suite ensures the IntakeAgent works correctly in isolation and integrates properly with the MCP validation system! 🦅