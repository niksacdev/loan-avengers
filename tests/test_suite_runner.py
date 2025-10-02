"""
Test suite runner with different test categories.

This script provides convenient ways to run different types of tests
for the intake agent and validation system.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        return True
    else:
        print(f"❌ {description} - FAILED")
        return False


def run_unit_tests():
    """Run unit tests only."""
    return run_command(["uv", "run", "pytest", "tests/unit/", "-v", "--tb=short"], "Unit Tests")


def run_integration_tests():
    """Run integration tests only."""
    return run_command(
        ["uv", "run", "pytest", "tests/integration/", "-v", "--tb=short", "-m", "integration"], "Integration Tests"
    )


def run_intake_agent_tests():
    """Run intake agent specific tests."""
    return run_command(
        ["uv", "run", "pytest", "tests/unit/agents/test_intake_agent.py", "-v"], "Intake Agent Unit Tests"
    )


def run_mcp_service_tests():
    """Run MCP service tests."""
    return run_command(
        ["uv", "run", "pytest", "tests/unit/tools/test_application_verification_service.py", "-v"], "MCP Service Tests"
    )


def run_model_tests():
    """Run data model tests."""
    return run_command(["uv", "run", "pytest", "tests/unit/models/", "-v"], "Data Model Tests")


def run_all_tests():
    """Run all tests."""
    return run_command(["uv", "run", "pytest", "tests/", "-v", "--tb=short"], "All Tests")


def run_tests_with_coverage():
    """Run tests with coverage report."""
    return run_command(
        [
            "uv",
            "run",
            "pytest",
            "tests/unit/",  # Only unit tests for reliable coverage
            "-v",
            "--cov=loan_defenders",
            "--cov-branch",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=json:coverage.json",
            "--cov-report=xml:coverage.xml",
            "--tb=short",
            "-m",
            "not integration",  # Skip integration tests for coverage
        ],
        "Unit Tests with Coverage",
    )


def run_coverage_analysis():
    """Run detailed coverage analysis."""
    return run_command(["uv", "run", "python", "tests/coverage_report.py", "report"], "Detailed Coverage Analysis")


def run_coverage_check():
    """Check if coverage meets requirements."""
    return run_command(["uv", "run", "python", "tests/coverage_report.py", "check"], "Coverage Requirements Check")


def run_fast_tests():
    """Run fast tests only (excluding slow integration tests)."""
    return run_command(
        ["uv", "run", "pytest", "tests/", "-v", "-m", "not integration", "--tb=short"], "Fast Tests (Unit Tests Only)"
    )


def run_performance_tests():
    """Run performance tests."""
    return run_command(["uv", "run", "pytest", "tests/", "-v", "-m", "performance", "--tb=short"], "Performance Tests")


def main():
    """Main test runner with menu."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        print("🧪 Intake Agent Test Suite")
        print("=" * 40)
        print("1. Unit tests only")
        print("2. Integration tests only")
        print("3. Intake agent tests")
        print("4. MCP service tests")
        print("5. Model tests")
        print("6. All tests")
        print("7. Tests with coverage")
        print("8. Fast tests (no integration)")
        print("9. Performance tests")
        print("10. Coverage analysis")
        print("11. Coverage check")
        print("0. Exit")

        choice = input("\nSelect test type (1-11, 0 to exit): ").strip()

        test_type_map = {
            "1": "unit",
            "2": "integration",
            "3": "intake",
            "4": "mcp",
            "5": "models",
            "6": "all",
            "7": "coverage",
            "8": "fast",
            "9": "performance",
            "10": "coverage_analysis",
            "11": "coverage_check",
            "0": "exit",
        }

        test_type = test_type_map.get(choice, "all")

    if test_type == "exit":
        print("👋 Goodbye!")
        return

    # Map test types to functions
    test_functions = {
        "unit": run_unit_tests,
        "integration": run_integration_tests,
        "intake": run_intake_agent_tests,
        "mcp": run_mcp_service_tests,
        "models": run_model_tests,
        "all": run_all_tests,
        "coverage": run_tests_with_coverage,
        "fast": run_fast_tests,
        "performance": run_performance_tests,
        "coverage_analysis": run_coverage_analysis,
        "coverage_check": run_coverage_check,
    }

    test_function = test_functions.get(test_type, run_all_tests)

    print("\n🚀 Starting test run...")
    success = test_function()

    if success:
        print("\n🎉 Test run completed successfully!")

        # Auto-show coverage for coverage runs
        if test_type in ["coverage", "coverage_analysis"]:
            print("\n📊 Coverage report available at: htmlcov/index.html")

        sys.exit(0)
    else:
        print("\n💥 Test run failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
