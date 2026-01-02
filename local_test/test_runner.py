"""
Test runner for all local tests.
Executes unit tests, integration tests, and manual tests.
"""
import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✓ {description} - PASSED")
            return True
        else:
            print(f"✗ {description} - FAILED (exit code {result.returncode})")
            return False
    except Exception as e:
        print(f"✗ {description} - ERROR: {e}")
        return False


def main():
    """Run all test suites."""
    print("="*60)
    print("Weekly Meal Planner - Test Runner")
    print("="*60)
    
    results = []
    
    # Check if pytest is available
    pytest_available = subprocess.run(
        "python3 -m pytest --version",
        shell=True,
        capture_output=True
    ).returncode == 0
    
    if pytest_available:
        # Run unit tests
        results.append(run_command(
            "python3 -m pytest tests/unit/ -v",
            "Unit Tests"
        ))
        
        # Run integration tests (if they exist)
        integration_tests = list(Path("tests/integration").glob("test_*.py"))
        if integration_tests:
            results.append(run_command(
                "python3 -m pytest tests/integration/ -v",
                "Integration Tests"
            ))
    else:
        print("\n⚠ pytest not installed - skipping unit tests")
        print("Install with: pip install -r requirements.txt")
    
    # Run Google Sheets integration test
    results.append(run_command(
        "python3 local_test/test_sheets.py",
        "Google Sheets Integration Test"
    ))
    
    # Run manual Alexa tests
    results.append(run_command(
        "python3 local_test/manual_test.py --all",
        "Manual Alexa Tests"
    ))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
