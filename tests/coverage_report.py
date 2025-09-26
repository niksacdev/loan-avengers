#!/usr/bin/env python3
"""
Coverage reporting and analysis script.

This script provides detailed coverage analysis with module-specific targets
and actionable insights for improving test coverage.
"""

import json
import subprocess
import sys
from pathlib import Path


class CoverageAnalyzer:
    """Analyze and report on test coverage with detailed insights."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.coverage_file = project_root / ".coverage"
        self.html_dir = project_root / "htmlcov"
        self.json_file = project_root / "coverage.json"

        # Module-specific coverage targets
        self.coverage_targets = {
            # Core business logic - high coverage required
            "loan_avengers/agents/": 90.0,
            "loan_avengers/models/": 95.0,
            "loan_avengers/tools/services/": 85.0,
            # MCP servers - medium coverage (has external dependencies)
            "loan_avengers/tools/mcp_servers/": 75.0,
            # Utilities - medium coverage
            "loan_avengers/utils/": 80.0,
            # Configuration - lower coverage acceptable
            "loan_avengers/config/": 70.0,
        }

    def run_coverage_tests(self, test_path: str = "tests/unit/") -> bool:
        """Run tests with coverage collection."""
        print("🧪 Running tests with coverage collection...")

        cmd = [
            "uv",
            "run",
            "pytest",
            test_path,
            "--cov=loan_avengers",
            "--cov-branch",
            f"--cov-report=html:{self.html_dir}",
            f"--cov-report=json:{self.json_file}",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml",
            "-v",
        ]

        try:
            subprocess.run(cmd, cwd=self.project_root, check=True, capture_output=True, text=True)
            print("✅ Tests completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Tests failed: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False

    def load_coverage_data(self) -> dict:
        """Load coverage data from JSON report."""
        if not self.json_file.exists():
            raise FileNotFoundError(f"Coverage JSON file not found: {self.json_file}")

        with open(self.json_file) as f:
            return json.load(f)

    def analyze_module_coverage(self, coverage_data: dict) -> dict[str, dict]:
        """Analyze coverage by module with detailed metrics."""
        files = coverage_data.get("files", {})
        module_analysis = {}

        for file_path, file_data in files.items():
            # Group by module directory
            if "loan_avengers/" in file_path:
                # Extract module path (e.g., "loan_avengers/agents/")
                parts = Path(file_path).parts
                if len(parts) >= 2:
                    module_path = "/".join(parts[:2]) + "/"

                    if module_path not in module_analysis:
                        module_analysis[module_path] = {
                            "files": [],
                            "total_statements": 0,
                            "covered_statements": 0,
                            "total_branches": 0,
                            "covered_branches": 0,
                            "missing_lines": [],
                            "target_coverage": self.coverage_targets.get(module_path, 85.0),
                        }

                    module_data = module_analysis[module_path]
                    module_data["files"].append(file_path)

                    # Aggregate coverage data
                    summary = file_data.get("summary", {})
                    module_data["total_statements"] += summary.get("num_statements", 0)
                    module_data["covered_statements"] += summary.get("covered_lines", 0)
                    module_data["total_branches"] += summary.get("num_branches", 0)
                    module_data["covered_branches"] += summary.get("covered_branches", 0)

                    # Collect missing lines
                    missing_lines = file_data.get("missing_lines", [])
                    if missing_lines:
                        module_data["missing_lines"].extend([f"{file_path}:{line}" for line in missing_lines])

        # Calculate coverage percentages
        for _module_path, data in module_analysis.items():
            if data["total_statements"] > 0:
                data["line_coverage"] = (data["covered_statements"] / data["total_statements"]) * 100
            else:
                data["line_coverage"] = 100.0

            if data["total_branches"] > 0:
                data["branch_coverage"] = (data["covered_branches"] / data["total_branches"]) * 100
            else:
                data["branch_coverage"] = 100.0

            # Combined coverage (weighted average)
            total_elements = data["total_statements"] + data["total_branches"]
            if total_elements > 0:
                covered_elements = data["covered_statements"] + data["covered_branches"]
                data["combined_coverage"] = (covered_elements / total_elements) * 100
            else:
                data["combined_coverage"] = 100.0

        return module_analysis

    def generate_detailed_report(self) -> None:
        """Generate a detailed coverage report with actionable insights."""
        print("\n" + "=" * 80)
        print("📊 DETAILED COVERAGE ANALYSIS")
        print("=" * 80)

        try:
            coverage_data = self.load_coverage_data()
        except FileNotFoundError:
            print("❌ No coverage data found. Run tests with coverage first.")
            return

        # Overall summary
        totals = coverage_data.get("totals", {})
        overall_coverage = totals.get("percent_covered", 0)

        print(f"\n🎯 OVERALL COVERAGE: {overall_coverage:.2f}%")
        print("   Target: 85.00%")
        if overall_coverage >= 85.0:
            print("   Status: ✅ MEETS TARGET")
        else:
            print(f"   Status: ❌ BELOW TARGET (need {85.0 - overall_coverage:.2f}% more)")

        # Module-by-module analysis
        module_analysis = self.analyze_module_coverage(coverage_data)

        print("\n📂 MODULE COVERAGE ANALYSIS")
        print("-" * 80)
        print(f"{'Module':<30} {'Coverage':<12} {'Target':<10} {'Status':<10} {'Gap':<10}")
        print("-" * 80)

        for module_path, data in sorted(module_analysis.items()):
            coverage_pct = data["combined_coverage"]
            target_pct = data["target_coverage"]

            if coverage_pct >= target_pct:
                status = "✅ PASS"
                gap = ""
            else:
                status = "❌ FAIL"
                gap = f"-{target_pct - coverage_pct:.1f}%"

            print(f"{module_path:<30} {coverage_pct:>8.2f}% {target_pct:>8.1f}% {status:<10} {gap:<10}")

        # Detailed file analysis for modules below target
        print("\n🔍 DETAILED ANALYSIS FOR MODULES BELOW TARGET")
        print("-" * 80)

        for module_path, data in sorted(module_analysis.items()):
            if data["combined_coverage"] < data["target_coverage"]:
                print(f"\n📁 {module_path}")
                print(
                    f"   Line Coverage: {data['line_coverage']:.2f}% "
                    f"({data['covered_statements']}/{data['total_statements']})"
                )
                print(
                    f"   Branch Coverage: {data['branch_coverage']:.2f}% "
                    f"({data['covered_branches']}/{data['total_branches']})"
                )
                print(f"   Files: {len(data['files'])}")

                # Show top missing lines
                missing_lines = data["missing_lines"][:10]  # Top 10
                if missing_lines:
                    print("   Top Missing Lines:")
                    for line in missing_lines:
                        print(f"     - {line}")
                    if len(data["missing_lines"]) > 10:
                        print(f"     ... and {len(data['missing_lines']) - 10} more")

        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 80)

        recommendations = []
        for module_path, data in module_analysis.items():
            if data["combined_coverage"] < data["target_coverage"]:
                gap = data["target_coverage"] - data["combined_coverage"]
                recommendations.append((module_path, gap, data))

        if recommendations:
            # Sort by gap (largest first)
            recommendations.sort(key=lambda x: x[1], reverse=True)

            print("Priority order for improving coverage:")
            for i, (module_path, gap, data) in enumerate(recommendations, 1):
                print(f"{i}. {module_path} (need +{gap:.1f}% coverage)")

                # Specific recommendations
                if data["line_coverage"] < data["branch_coverage"]:
                    print("   → Focus on adding tests for uncovered lines")
                else:
                    print("   → Focus on adding tests for edge cases and branches")

                print(f"   → Add ~{int(gap * data['total_statements'] / 100)} more covered lines")
        else:
            print("🎉 All modules meet their coverage targets!")

        # Links to reports
        print("\n📈 DETAILED REPORTS AVAILABLE:")
        print(f"   HTML Report: file://{self.html_dir.absolute()}/index.html")
        print(f"   JSON Report: {self.json_file}")
        print("   XML Report: coverage.xml")

    def check_coverage_requirements(self) -> bool:
        """Check if coverage meets requirements and return pass/fail."""
        try:
            coverage_data = self.load_coverage_data()
        except FileNotFoundError:
            print("❌ No coverage data found")
            return False

        # Check overall coverage
        totals = coverage_data.get("totals", {})
        overall_coverage = totals.get("percent_covered", 0)

        if overall_coverage < 85.0:
            print(f"❌ Overall coverage {overall_coverage:.2f}% below minimum 85.0%")
            return False

        # Check module-specific targets
        module_analysis = self.analyze_module_coverage(coverage_data)
        failed_modules = []

        for module_path, data in module_analysis.items():
            if data["combined_coverage"] < data["target_coverage"]:
                failed_modules.append(module_path)

        if failed_modules:
            print(f"❌ {len(failed_modules)} modules below target coverage:")
            for module in failed_modules:
                print(f"   - {module}")
            return False

        print("✅ All coverage requirements met!")
        return True


def main():
    """Main coverage analysis runner."""
    project_root = Path(__file__).parent.parent
    analyzer = CoverageAnalyzer(project_root)

    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        print("🔍 Coverage Analysis Options:")
        print("1. Run tests and generate coverage")
        print("2. Analyze existing coverage")
        print("3. Check coverage requirements")
        print("4. Generate detailed report")

        choice = input("\nSelect option (1-4): ").strip()

        command_map = {"1": "run", "2": "analyze", "3": "check", "4": "report"}

        command = command_map.get(choice, "run")

    if command == "run":
        print("🚀 Running tests with coverage collection...")
        success = analyzer.run_coverage_tests()
        if success:
            analyzer.generate_detailed_report()
        else:
            sys.exit(1)

    elif command == "analyze":
        analyzer.generate_detailed_report()

    elif command == "check":
        success = analyzer.check_coverage_requirements()
        sys.exit(0 if success else 1)

    elif command == "report":
        analyzer.generate_detailed_report()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
