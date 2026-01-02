# Alexa Weekly Meal Planner

An Alexa skill that helps you plan your weekly meals by reading from a Google Sheet. Ask Alexa what to cook for any meal during the week!

**Status**: ✅ **Production Ready** | 48/55 tasks (87%) | 53 automated tests | Local testing enabled

## Features

- 🗣️ **Voice-activated meal planning**: Ask Alexa about any meal
- 📅 **Full weekly support**: Plan all 5 meals per day (breakfast, morning snack, lunch, evening snack, dinner)
- 📊 **Google Sheets integration**: Manage your meal plan in a simple spreadsheet
- 🧪 **Local testing**: Test without deploying to Alexa cloud services (FR-011)
- ⚡ **Fast responses**: <3 second response time with smart caching
- 🎯 **Smart filtering**: "What to cook today" only shows remaining meals
- 📝 **Comprehensive logging**: Production-ready error tracking

## Quick Start

See [quickstart.md](specs/001-alexa-meal-planner/quickstart.md) for detailed setup instructions.

### Prerequisites

- Python 3.9+
- Google account with Google Sheets access
- Alexa developer account (for deploying the skill to alexa)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd alexa-skill-weekly-menu

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Google Sheet ID and credentials path

# Test locally (no Alexa deployment needed!)
python3 local_test/manual_test.py
```

### Testing

```bash
# Quick test run (mock data)
python3 local_test/test_runner.py

# Interactive testing
python3 local_test/manual_test.py

# Unit tests only
python3 -m pytest tests/unit/ -v

# Google Sheets integration
python3 local_test/test_sheets.py

# End-to-end tests (comprehensive)
python3 local_test/run_e2e_tests.py
```

**Test Coverage**: 53+ automated tests
- 43 unit tests (time logic, meal service, data models)
- 10 integration tests (intent handlers)
- Full end-to-end test suite with real API capability

### End-to-End Testing with Real Google Sheets

The project includes comprehensive E2E tests that can run with either **mock data** or **real Google Sheets API**:

#### Running with Mock Data (Default)

```bash
# Run complete E2E test suite with mocked Google Sheets
python3 local_test/run_e2e_tests.py

# Or use pytest directly
pytest tests/e2e/ -v
```

#### Running with Real Google Sheets API

For true end-to-end validation, you can test against actual Google Sheets:

```bash
# 1. Ensure credentials are set up
#    - Place credentials.json in project root
#    - Set GOOGLE_SHEET_ID in .env

# 2. Run with real API enabled
USE_REAL_SHEETS_API=true python3 local_test/run_e2e_tests.py

# Or for just the real API tests
python3 local_test/run_e2e_tests.py --only-real-api -v

# Test local scripts with real API
USE_REAL_SHEETS_API=true python3 local_test/test_sheets.py
```

#### E2E Test Categories

The E2E test suite validates:

1. **Real API Integration** (when credentials provided)
   - Actual Google Sheets authentication
   - Data retrieval from live spreadsheet
   - Data parsing and validation
   - Meal plan construction from real data

2. **Full Intent Flow** (mock and real data)
   - Complete Alexa request → response cycle
   - LaunchRequest handling
   - GetMealIntent with Google Sheets lookup
   - GetTodayMealsIntent with time-based filtering
   - GetSpecificDayMealIntent with day/meal queries
   - GetNextMealIntent with time-aware logic

3. **Error Handling**
   - Empty meal slots
   - Invalid requests
   - API failures
   - Edge cases

#### Test Runner Options

```bash
# Verbose output
python3 local_test/run_e2e_tests.py -v

# Only mock tests
python3 local_test/run_e2e_tests.py --only-mock

# Skip unit/integration tests
python3 local_test/run_e2e_tests.py --skip-unit --skip-integration

# Local scripts only
python3 local_test/run_e2e_tests.py --local-only
```

---

## Documentation

- [Feature Specification](specs/001-alexa-meal-planner/spec.md) - User stories and requirements
- [Implementation Plan](specs/001-alexa-meal-planner/plan.md) - Technical architecture
- [Data Model](specs/001-alexa-meal-planner/data-model.md) - Entities and relationships
- [Quick Start Guide](specs/001-alexa-meal-planner/quickstart.md) - Setup and integration
- [Task Breakdown](specs/001-alexa-meal-planner/tasks.md) - Implementation tasks

---

**Ask about a specific meal:**
- "Alexa, ask meal planner what's for dinner?"
- "Alexa, ask meal planner what's for breakfast on Friday?"

**Get today's full meal plan:**
- "Alexa, ask meal planner what should I cook today?"

**Find out what's next:**
- "Alexa, ask meal planner what's next?"

## Project Structure

```
alexa-skill-weekly-menu/
├── lambda/
│   ├── models/          # Data classes (Meal, MealPlan, TimePeriod)
│   ├── services/        # Business logic (SheetsService, MealService)
│   ├── handlers/        # Alexa intent handlers
│   ├── config/          # Configuration (meal periods, settings)
│   └── lambda_function.py  # AWS Lambda entry point
├── tests/               # Unit and integration tests
├── local_test/          # Local testing scripts
├── specs/               # Feature specifications and documentation
└── requirements.txt     # Python dependencies
```

## Testing

The project includes comprehensive test coverage at multiple levels:

### Test Levels

1. **Unit Tests** (`tests/unit/`)
   - Time period logic and meal scheduling
   - Data models (Meal, MealPlan, TimePeriod)
   - Meal service business logic
   - 43 tests covering core functionality

2. **Integration Tests** (`tests/integration/`)
   - Intent handlers with mocked services
   - Google Sheets service integration
   - Response builder formatting
   - 10 tests validating component integration

3. **End-to-End Tests** (`tests/e2e/`)
   - Full request-to-response flow
   - Real Google Sheets API capability
   - All user stories validated
   - Error handling scenarios

### Quick Test Commands

```bash
# Run all tests with mock data
pytest

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Run with coverage report
pytest --cov=src --cov-report=html

# Interactive local testing
python local_test/manual_test.py
```

### Advanced E2E Testing

For comprehensive end-to-end validation:

```bash
# Complete E2E test suite (orchestrated)
python local_test/run_e2e_tests.py -v

# Test with REAL Google Sheets (requires credentials)
USE_REAL_SHEETS_API=true python local_test/run_e2e_tests.py

# Only run real API tests
python local_test/run_e2e_tests.py --only-real-api -v
```

See **End-to-End Testing with Real Google Sheets** section below for details.

---

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
