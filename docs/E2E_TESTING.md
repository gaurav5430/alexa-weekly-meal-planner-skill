# End-to-End Testing Guide

## Overview

This project includes comprehensive end-to-end (E2E) testing capabilities that can validate the entire system with either **mocked data** or **real Google Sheets API integration**.

## Test Architecture

### Test Levels

1. **Unit Tests** (`tests/unit/`)
   - Fast, isolated tests of individual components
   - No external dependencies
   - Tests time logic, data models, business logic

2. **Integration Tests** (`tests/integration/`)
   - Tests component interactions
   - Mocked external services (Google Sheets)
   - Validates intent handlers and service integration

3. **End-to-End Tests** (`tests/e2e/`)
   - Complete system validation
   - Can use real or mocked Google Sheets
   - Tests full Alexa request → response flow

## Running E2E Tests

### Quick Start - Mock Data

The easiest way to run E2E tests is with mocked Google Sheets data:

```bash
# Using pytest directly
pytest tests/e2e/ -v

# Using the E2E test runner
python local_test/run_e2e_tests.py
```

**No credentials or setup required!** Tests use realistic mock data.

### Advanced - Real Google Sheets API

For true end-to-end validation with actual Google Sheets:

#### Prerequisites

1. **Google Cloud Service Account**
   - Create a service account in Google Cloud Console
   - Download credentials JSON file
   - Place as `credentials.json` in project root

2. **Google Sheet**
   - Create a Google Sheet with your meal plan
   - Share the sheet with the service account email
   - Copy the Sheet ID from the URL

3. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Set `GOOGLE_SHEET_ID` to your sheet ID
   - Set `CREDENTIALS_PATH` (default: `credentials.json`)

#### Running Real API Tests

```bash
# Enable real API testing
export USE_REAL_SHEETS_API=true
export GOOGLE_SHEET_ID=your-sheet-id-here

# Run all E2E tests with real API
python local_test/run_e2e_tests.py -v

# Or just the real API tests
python local_test/run_e2e_tests.py --only-real-api -v

# Test local scripts with real API
USE_REAL_SHEETS_API=true python local_test/test_sheets.py
```

## E2E Test Coverage

### Test Categories

#### 1. Real API Integration (`TestE2EWithRealAPI`)
Tests actual Google Sheets integration when credentials are provided:
- ✅ Authentication with Google Sheets API
- ✅ Data retrieval from live spreadsheet
- ✅ Data parsing and validation
- ✅ Meal plan construction
- ✅ Data quality checks

**Automatically skipped if real API not configured.**

#### 2. Full Intent Flow (`TestE2EFullIntentFlow`)
Tests complete Alexa skill flow with mocked services:
- ✅ LaunchRequest handling
- ✅ GetMealIntent (e.g., "what's for dinner?")
- ✅ GetTodayMealsIntent (e.g., "what should I cook today?")
- ✅ GetSpecificDayMealIntent (e.g., "what's for breakfast on Friday?")
- ✅ GetNextMealIntent (e.g., "what's next?")

#### 3. Error Handling (`TestE2EErrorHandling`)
Validates edge cases and error scenarios:
- ✅ Empty meal slots
- ✅ Invalid requests
- ✅ Graceful error messages
- ✅ User-friendly responses

#### 4. Real Intent with Real API (`TestE2ERealIntentWithRealAPI`)
**Full stack validation** - Alexa request through to real Google Sheets:
- ✅ Complete integration test
- ✅ Actual API calls
- ✅ Real data retrieval and processing
- ✅ Production-like scenario

**Only runs when USE_REAL_SHEETS_API=true and credentials are valid.**

## Test Runner Features

The `local_test/run_e2e_tests.py` script provides:

### Basic Usage

```bash
# Run all tests
python local_test/run_e2e_tests.py

# Verbose output
python local_test/run_e2e_tests.py -v

# Only mock tests
python local_test/run_e2e_tests.py --only-mock

# Only real API tests
python local_test/run_e2e_tests.py --only-real-api
```

### Advanced Options

```bash
# Skip unit tests
python local_test/run_e2e_tests.py --skip-unit

# Skip integration tests
python local_test/run_e2e_tests.py --skip-integration

# Only run local test scripts
python local_test/run_e2e_tests.py --local-only
```

### Test Output

The runner provides:
- ✅ Color-coded test results
- ✅ Test mode detection (mock vs real API)
- ✅ Prerequisite checks
- ✅ Summary of passed/failed tests
- ✅ Configuration guidance

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `USE_REAL_SHEETS_API` | Enable real API testing | `false` | No |
| `GOOGLE_SHEET_ID` | Google Sheet ID | - | For real API |
| `CREDENTIALS_PATH` | Path to credentials JSON | `credentials.json` | For real API |

## Example Test Session

### Mock Data Testing (No Setup)

```bash
$ python local_test/run_e2e_tests.py

======================================================================
TEST MODE CONFIGURATION
======================================================================
Mode: MOCK MODE - Reason: USE_REAL_SHEETS_API not set to 'true'
======================================================================

============================================================
Running Unit Tests
============================================================
✓ Unit tests passed

============================================================
Running Integration Tests
============================================================
✓ Integration tests passed

============================================================
Running E2E Tests (Mock Data)
============================================================
✓ E2E mock tests passed

============================================================
Test Summary
============================================================
✓ UNIT: PASSED
✓ INTEGRATION: PASSED
✓ E2E_MOCK: PASSED

Total: 3 | Passed: 3 | Failed: 0

✓ All tests passed!
```

### Real API Testing (With Credentials)

```bash
$ export USE_REAL_SHEETS_API=true
$ export GOOGLE_SHEET_ID=1abc...xyz
$ python local_test/run_e2e_tests.py --only-real-api -v

======================================================================
TEST MODE CONFIGURATION
======================================================================
Mode: REAL API MODE - Using Sheet ID: 1abc...
======================================================================

============================================================
Running E2E Tests (Real Google Sheets API)
============================================================
ℹ Testing with Sheet ID: 1abc...

test_fetch_real_meal_plan PASSED
✓ Successfully fetched meal plan from Sheet: 1abc...xyz
✓ Validated 7 days of meals

test_real_api_data_quality PASSED
✓ Total meals: 35
✓ Non-empty meals: 32
✓ Empty meals: 3

test_full_stack_get_meal_with_real_api PASSED
✓ REAL API Full Stack Test: <speak>For dinner, you should prepare...</speak>

✓ E2E real API tests passed

============================================================
Test Summary
============================================================
✓ E2E_REAL: PASSED

✓ All tests passed!
```

## Best Practices

### For Development

1. **Use mock tests during development**
   - Faster execution
   - No API quotas
   - Reliable test data
   
2. **Run real API tests before deployment**
   - Validates actual integration
   - Catches API changes
   - Verifies credentials

### For CI/CD

1. **Mock tests in CI pipeline**
   - Fast feedback
   - No credential management
   - Consistent results

2. **Real API tests in staging**
   - Pre-production validation
   - Integration verification
   - Use test Google Sheet

### For Local Testing

```bash
# Quick validation during development
pytest tests/e2e/ -k "not RealAPI" -v

# Full validation before commit
python local_test/run_e2e_tests.py

# Production-like testing
USE_REAL_SHEETS_API=true python local_test/run_e2e_tests.py --only-real-api
```

## Troubleshooting

### Tests Skipped with "Real API tests disabled"

**Cause**: Real API not configured

**Solution**:
```bash
# Check configuration
export USE_REAL_SHEETS_API=true
export GOOGLE_SHEET_ID=your-sheet-id

# Verify credentials exist
ls credentials.json
```

### "Credentials not found" Error

**Cause**: Missing credentials.json file

**Solution**:
1. Download service account credentials from Google Cloud Console
2. Save as `credentials.json` in project root
3. Ensure service account has access to your Google Sheet

### "GOOGLE_SHEET_ID not set" Warning

**Cause**: Environment variable not configured

**Solution**:
```bash
# Set in environment
export GOOGLE_SHEET_ID=your-sheet-id-here

# Or in .env file
echo "GOOGLE_SHEET_ID=your-sheet-id-here" >> .env
```

### Import Errors

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

## Additional Resources

- [Quick Start Guide](../specs/001-alexa-meal-planner/quickstart.md) - Setup instructions
- [Feature Specification](../specs/001-alexa-meal-planner/spec.md) - User stories
- [Implementation Plan](../specs/001-alexa-meal-planner/plan.md) - Architecture
- [README.md](../README.md) - Project overview
