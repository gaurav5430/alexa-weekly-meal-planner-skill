#!/usr/bin/env python3
"""
End-to-End Test Runner for Alexa Meal Planner

This script orchestrates running comprehensive end-to-end tests with
options for mock or real Google Sheets API testing.

Usage:
    # Run with mock data (default)
    python local_test/run_e2e_tests.py
    
    # Run with real Google Sheets API
    USE_REAL_SHEETS_API=true python local_test/run_e2e_tests.py
    
    # Run specific test categories
    python local_test/run_e2e_tests.py --only-real-api
    python local_test/run_e2e_tests.py --only-mock
    
    # Verbose output
    python local_test/run_e2e_tests.py -v
"""
import sys
import os
import subprocess
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_config import TestConfig


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def check_prerequisites():
    """Check if required dependencies are installed."""
    print_header("Checking Prerequisites")
    
    try:
        import pytest
        print_success(f"pytest installed: {pytest.__version__}")
    except ImportError:
        print_error("pytest not installed")
        print_info("Install with: pip install pytest pytest-mock")
        return False
    
    try:
        import ask_sdk_core
        print_success("ask-sdk-core installed")
    except ImportError:
        print_error("ask-sdk-core not installed")
        print_info("Install with: pip install -r requirements.txt")
        return False
    
    # Check if source files exist
    src_path = Path(__file__).parent.parent / "src"
    if not src_path.exists():
        print_error("src/ directory not found")
        return False
    print_success("Source directory found")
    
    # Check test files
    tests_path = Path(__file__).parent.parent / "tests"
    if not tests_path.exists():
        print_error("tests/ directory not found")
        return False
    print_success("Tests directory found")
    
    return True


def run_unit_tests(verbose=False):
    """Run unit tests."""
    print_header("Running Unit Tests")
    
    cmd = ["pytest", "tests/unit/", "-v" if verbose else "-q"]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    
    if result.returncode == 0:
        print_success("Unit tests passed")
        return True
    else:
        print_error("Unit tests failed")
        return False


def run_integration_tests(verbose=False):
    """Run integration tests."""
    print_header("Running Integration Tests")
    
    cmd = ["pytest", "tests/integration/", "-v" if verbose else "-q"]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    
    if result.returncode == 0:
        print_success("Integration tests passed")
        return True
    else:
        print_error("Integration tests failed")
        return False


def run_e2e_mock_tests(verbose=False):
    """Run E2E tests with mock data."""
    print_header("Running E2E Tests (Mock Data)")
    
    # Ensure USE_REAL_SHEETS_API is false
    env = os.environ.copy()
    env['USE_REAL_SHEETS_API'] = 'false'
    
    cmd = ["pytest", "tests/e2e/", "-k", "not RealAPI", "-v" if verbose else "-q"]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, env=env)
    
    if result.returncode == 0:
        print_success("E2E mock tests passed")
        return True
    else:
        print_error("E2E mock tests failed")
        return False


def run_e2e_real_api_tests(verbose=False):
    """Run E2E tests with real Google Sheets API."""
    print_header("Running E2E Tests (Real Google Sheets API)")
    
    if not TestConfig.can_run_real_api_tests():
        print_warning("Real API tests skipped - not configured")
        print_info("To enable:")
        print_info("  1. Place credentials.json in project root")
        print_info("  2. Set GOOGLE_SHEET_ID environment variable")
        print_info("  3. Set USE_REAL_SHEETS_API=true")
        return None
    
    print_info(f"Testing with Sheet ID: {TestConfig.TEST_GOOGLE_SHEET_ID[:10]}...")
    
    env = os.environ.copy()
    env['USE_REAL_SHEETS_API'] = 'true'
    env['GOOGLE_SHEET_ID'] = TestConfig.TEST_GOOGLE_SHEET_ID
    env['CREDENTIALS_PATH'] = TestConfig.CREDENTIALS_PATH
    
    cmd = ["pytest", "tests/e2e/", "-k", "RealAPI", "-v" if verbose else "-q", "-s"]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, env=env)
    
    if result.returncode == 0:
        print_success("E2E real API tests passed")
        return True
    else:
        print_error("E2E real API tests failed")
        return False


def run_local_tests():
    """Run local test scripts."""
    print_header("Running Local Test Scripts")
    
    # Run test_sheets.py
    test_sheets = Path(__file__).parent / "test_sheets.py"
    if test_sheets.exists():
        print_info("Running test_sheets.py...")
        result = subprocess.run([sys.executable, str(test_sheets)])
        if result.returncode == 0:
            print_success("test_sheets.py passed")
        else:
            print_error("test_sheets.py failed")
            return False
    
    return True


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run E2E tests for Alexa Meal Planner")
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--only-real-api', action='store_true', help='Only run real API tests')
    parser.add_argument('--only-mock', action='store_true', help='Only run mock tests')
    parser.add_argument('--skip-unit', action='store_true', help='Skip unit tests')
    parser.add_argument('--skip-integration', action='store_true', help='Skip integration tests')
    parser.add_argument('--local-only', action='store_true', help='Only run local test scripts')
    
    args = parser.parse_args()
    
    print_header("Alexa Meal Planner - End-to-End Test Suite")
    
    # Print test mode
    TestConfig.print_test_mode()
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed")
        sys.exit(1)
    
    results = {}
    
    # Run local tests if requested
    if args.local_only:
        results['local'] = run_local_tests()
    else:
        # Run test suites based on arguments
        if not args.only_real_api:
            if not args.skip_unit:
                results['unit'] = run_unit_tests(args.verbose)
            
            if not args.skip_integration:
                results['integration'] = run_integration_tests(args.verbose)
            
            if not args.only_mock:
                results['e2e_mock'] = run_e2e_mock_tests(args.verbose)
        
        if not args.only_mock:
            real_api_result = run_e2e_real_api_tests(args.verbose)
            if real_api_result is not None:
                results['e2e_real'] = real_api_result
    
    # Print summary
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = sum(1 for r in results.values() if not r)
    
    for test_type, result in results.items():
        if result:
            print_success(f"{test_type.upper()}: PASSED")
        else:
            print_error(f"{test_type.upper()}: FAILED")
    
    print(f"\n{Colors.BOLD}Total: {total} | Passed: {passed} | Failed: {failed}{Colors.ENDC}")
    
    if failed > 0:
        print_error("\nSome tests failed!")
        sys.exit(1)
    else:
        print_success("\nAll tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
