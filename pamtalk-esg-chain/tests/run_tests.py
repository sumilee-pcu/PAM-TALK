# -*- coding: utf-8 -*-
"""
Test Runner Script
Runs all tests and generates comprehensive reports
"""

import sys
import os
import subprocess
from datetime import datetime
import json


class TestRunner:
    """Manages test execution and reporting"""

    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {}
        }

    def run_unit_tests(self):
        """Run unit tests"""
        print("\n" + "="*60)
        print("🧪 Running Unit Tests")
        print("="*60 + "\n")

        cmd = [
            sys.executable, "-m", "pytest",
            "test_unit_contracts.py",
            "-v",
            "--tb=short",
            "-m", "unit or not integration and not e2e"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        self.results['test_suites']['unit'] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0

    def run_integration_tests(self):
        """Run integration tests"""
        print("\n" + "="*60)
        print("🔗 Running Integration Tests")
        print("="*60 + "\n")

        cmd = [
            sys.executable, "-m", "pytest",
            "test_integration_backend.py",
            "-v",
            "--tb=short",
            "-m", "integration or not unit and not e2e"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        self.results['test_suites']['integration'] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0

    def run_e2e_tests(self):
        """Run E2E scenario tests"""
        print("\n" + "="*60)
        print("🎯 Running E2E Scenario Tests")
        print("="*60 + "\n")

        cmd = [
            sys.executable, "-m", "pytest",
            "test_e2e_scenarios.py",
            "-v",
            "--tb=short",
            "-m", "e2e or not unit and not integration"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        self.results['test_suites']['e2e'] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0

    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*60)
        print("🚀 Running All Tests")
        print("="*60 + "\n")

        cmd = [
            sys.executable, "-m", "pytest",
            "-v",
            "--tb=short",
            "--html=test_report.html",
            "--self-contained-html"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        self.results['test_suites']['all'] = {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60 + "\n")

        total_passed = 0
        total_failed = 0
        total_skipped = 0

        for suite_name, suite_result in self.results['test_suites'].items():
            stdout = suite_result['stdout']

            # Parse pytest output
            if 'passed' in stdout:
                # Extract numbers from output
                import re
                match = re.search(r'(\d+) passed', stdout)
                if match:
                    passed = int(match.group(1))
                    total_passed += passed

                match = re.search(r'(\d+) failed', stdout)
                if match:
                    failed = int(match.group(1))
                    total_failed += failed

                match = re.search(r'(\d+) skipped', stdout)
                if match:
                    skipped = int(match.group(1))
                    total_skipped += skipped

        self.results['summary'] = {
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_skipped': total_skipped,
            'success_rate': (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        }

        print(f"✅ Passed:  {total_passed}")
        print(f"❌ Failed:  {total_failed}")
        print(f"⏭️  Skipped: {total_skipped}")
        print(f"📈 Success Rate: {self.results['summary']['success_rate']:.2f}%")

        return self.results['summary']

    def save_results(self, filename='test_results.json'):
        """Save test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {filename}")

    def print_recommendations(self):
        """Print recommendations based on test results"""
        print("\n" + "="*60)
        print("💡 Recommendations")
        print("="*60 + "\n")

        summary = self.results['summary']

        if summary['total_failed'] == 0:
            print("✅ All tests passed! Your system is ready for deployment.")
            print("\nNext steps:")
            print("  1. Deploy contracts to TestNet")
            print("  2. Run integration tests with real blockchain")
            print("  3. Perform security audit")
            print("  4. Set up monitoring and alerts")

        elif summary['success_rate'] >= 80:
            print("⚠️  Most tests passed, but some failures detected.")
            print("\nRecommended actions:")
            print("  1. Review failed test logs")
            print("  2. Fix identified issues")
            print("  3. Re-run tests")

        else:
            print("❌ Significant test failures detected.")
            print("\nCritical actions needed:")
            print("  1. Review all failed tests")
            print("  2. Check contract logic")
            print("  3. Verify backend integrations")
            print("  4. Do not proceed to deployment")


def main():
    """Main test runner"""
    print("\n" + "🌱" * 30)
    print("PAM-TALK ESG Chain - Integration Test Suite")
    print("🌱" * 30 + "\n")

    runner = TestRunner()

    # Check for pytest
    try:
        subprocess.run([sys.executable, "-m", "pytest", "--version"],
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ pytest not installed!")
        print("Install with: pip install pytest pytest-html")
        return

    # Parse arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1]

        if test_type == "unit":
            runner.run_unit_tests()
        elif test_type == "integration":
            runner.run_integration_tests()
        elif test_type == "e2e":
            runner.run_e2e_tests()
        elif test_type == "all":
            runner.run_all_tests()
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("Usage: python run_tests.py [unit|integration|e2e|all]")
            return
    else:
        # Run all tests by default
        print("Running all test suites...\n")
        runner.run_unit_tests()
        runner.run_integration_tests()
        runner.run_e2e_tests()

    # Generate summary and recommendations
    runner.generate_summary()
    runner.save_results()
    runner.print_recommendations()

    print("\n" + "="*60)
    print("✨ Test execution completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
