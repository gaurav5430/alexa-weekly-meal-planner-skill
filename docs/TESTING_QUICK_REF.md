# Testing Quick Reference

## Run Tests

```bash
# All tests (mock data)
python local_test/run_e2e_tests.py

# With real Google Sheets
USE_REAL_SHEETS_API=true python local_test/run_e2e_tests.py

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v

# Specific test file
pytest tests/e2e/test_full_integration.py -v

# Interactive local testing
python local_test/manual_test.py
```

## Test Files

| File | Purpose |
|------|---------|
| `tests/unit/*` | Unit tests for individual components |
| `tests/integration/*` | Integration tests with mocked services |
| `tests/e2e/test_full_integration.py` | Full E2E tests (mock + real API) |
| `tests/test_config.py` | Test configuration for mock/real API switching |
| `local_test/test_sheets.py` | Google Sheets integration test (mock + real) |
| `local_test/run_e2e_tests.py` | E2E test orchestration script |
| `local_test/manual_test.py` | Interactive testing tool |

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `USE_REAL_SHEETS_API` | Enable real API testing | `true` or `false` |
| `GOOGLE_SHEET_ID` | Your Google Sheet ID | `1abc...xyz` |
| `CREDENTIALS_PATH` | Path to credentials | `credentials.json` |

## E2E Test Categories

### ✅ Mock Data (Always Available)
- Intent flow testing
- Error handling
- Response validation
- No credentials needed

### ✅ Real API (Requires Setup)
- Actual Google Sheets integration
- Real data retrieval
- Full stack validation
- Production-like testing

## Quick Setup for Real API Testing

```bash
# 1. Get credentials from Google Cloud Console
# 2. Save as credentials.json in project root
# 3. Set environment variables

export USE_REAL_SHEETS_API=true
export GOOGLE_SHEET_ID=your-sheet-id-here

# 4. Run tests
python local_test/run_e2e_tests.py --only-real-api -v
```

## Test Coverage

- **53+ automated tests**
- **43 unit tests** - Core logic
- **10 integration tests** - Component interaction
- **Full E2E suite** - End-to-end validation
- **Real API capability** - Production testing

## Common Commands

```bash
# Development workflow
pytest tests/unit/ -v                          # Fast unit tests
pytest tests/e2e/ -k "not RealAPI" -v         # E2E with mocks

# Pre-commit validation
python local_test/run_e2e_tests.py            # Full test suite

# Pre-deployment validation
USE_REAL_SHEETS_API=true \
  python local_test/run_e2e_tests.py          # With real API

# Coverage report
pytest --cov=src --cov-report=html            # Generate HTML report
```

## See Also

- [E2E Testing Guide](E2E_TESTING.md) - Comprehensive documentation
- [README.md](../README.md) - Project overview
- [Quick Start](../specs/001-alexa-meal-planner/quickstart.md) - Setup guide
