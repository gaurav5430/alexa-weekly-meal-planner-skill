# Quickstart Guide: Alexa Weekly Meal Planner

**Purpose**: Get the skill running locally for development and testing  
**Audience**: Developers setting up the project for the first time  
**Time**: ~15 minutes

---

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Google account with access to Google Sheets
- Code editor (VS Code, PyCharm, etc.)

---

## Step 1: Clone and Setup Project

```bash
# Clone repository (adjust URL as needed)
git clone <repository-url>
cd alexa-skill-weekly-menu

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Expected `requirements.txt`**:
```
ask-sdk-core==1.19.0
gspread==5.12.0
oauth2client==4.1.3
pytest==7.4.3
pytest-mock==3.12.0
```

---

## Step 2: Google Sheets Setup

### 2.1 Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "Weekly Meal Plan" (or your preference)
4. Structure it as follows:

| Day       | Breakfast | Morning Snack | Lunch | Evening Snack | Dinner |
|-----------|-----------|---------------|-------|---------------|--------|
| Monday    | Oatmeal   | Apple         | Salad | Nuts          | Pasta  |
| Tuesday   | Eggs      | Yogurt        | Soup  | Carrots       | Chicken|
| Wednesday | Pancakes  | Banana        | Rice  | Chips         | Fish   |
| Thursday  | Toast     | Smoothie      | Wrap  | Crackers      | Beef   |
| Friday    | Cereal    | Orange        | Pizza | Cookies       | Tacos  |
| Saturday  | Waffles   | Berries       | Burger| Popcorn       | Steak  |
| Sunday    | Bagel     | Nuts          | Pasta | Veggies       | Curry  |

5. Copy the Sheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
   - Save the `{SHEET_ID}` for later

### 2.2 Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable Google Sheets API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create service account:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name it "alexa-meal-planner-service"
   - Click "Create and Continue"
   - Skip optional steps, click "Done"
5. Create service account key:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Select "JSON" format
   - Click "Create" (file will download)
6. Rename downloaded file to `credentials.json`
7. Move `credentials.json` to project root

### 2.3 Share Sheet with Service Account

1. Open the `credentials.json` file
2. Find the `client_email` field (looks like `name@project-id.iam.gserviceaccount.com`)
3. Copy this email
4. Go back to your Google Sheet
5. Click "Share" button
6. Paste the service account email
7. Grant "Viewer" access (read-only)
8. Uncheck "Notify people"
9. Click "Share"

---

## Step 3: Configure Environment

Create a `.env` file in project root:

```bash
# .env
GOOGLE_SHEET_ID=your_sheet_id_from_step_2.1
CREDENTIALS_PATH=credentials.json
```

Add to `.gitignore`:
```
credentials.json
.env
venv/
__pycache__/
*.pyc
```

---

## Step 4: Run Local Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_meal_service.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

**Expected Output**:
```
============================= test session starts ==============================
collected 25 items

tests/unit/test_models.py ..........                                    [ 40%]
tests/unit/test_meal_service.py ..........                              [ 80%]
tests/unit/test_time_periods.py .....                                   [100%]

============================== 25 passed in 2.34s ===============================
```

---

## Step 5: Local Testing with Mock Alexa Requests

### 5.1 Create Test Script

Create `local_test/manual_test.py`:

```python
#!/usr/bin/env python3
import json
from src.lambda_function import lambda_handler

def test_get_meal():
    """Test GetMealIntent"""
    event = {
        "version": "1.0",
        "session": {
            "new": True,
            "sessionId": "test-session",
            "application": {"applicationId": "test-app-id"},
            "user": {"userId": "test-user"}
        },
        "request": {
            "type": "IntentRequest",
            "requestId": "test-request",
            "intent": {
                "name": "GetMealIntent",
                "slots": {
                    "MealType": {
                        "name": "MealType",
                        "value": "dinner"
                    }
                }
            }
        }
    }
    
    response = lambda_handler(event, None)
    print(json.dumps(response, indent=2))

def test_today_meals():
    """Test GetTodayMealsIntent"""
    event = {
        "version": "1.0",
        "session": {
            "new": True,
            "sessionId": "test-session",
            "application": {"applicationId": "test-app-id"},
            "user": {"userId": "test-user"}
        },
        "request": {
            "type": "IntentRequest",
            "requestId": "test-request",
            "intent": {
                "name": "GetTodayMealsIntent",
                "slots": {}
            }
        }
    }
    
    response = lambda_handler(event, None)
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    print("Testing GetMealIntent:")
    test_get_meal()
    print("\n" + "="*50 + "\n")
    print("Testing GetTodayMealsIntent:")
    test_today_meals()
```

### 5.2 Run Manual Tests

```bash
# Make script executable
chmod +x local_test/manual_test.py

# Run tests
python local_test/manual_test.py
```

**Expected Output**:
```json
Testing GetMealIntent:
{
  "version": "1.0",
  "response": {
    "outputSpeech": {
      "type": "SSML",
      "ssml": "<speak>For dinner today, you should prepare Pasta.</speak>"
    },
    "shouldEndSession": true
  }
}

==================================================

Testing GetTodayMealsIntent:
{
  "version": "1.0",
  "response": {
    "outputSpeech": {
      "type": "SSML",
      "ssml": "<speak>Here's what you should cook today: 1. For breakfast, Oatmeal. 2. For morning snack, Apple. 3. For lunch, Salad. 4. For evening snack, Nuts. 5. For dinner, Pasta.</speak>"
    },
    "shouldEndSession": true
  }
}
```

---

## Step 6: Verify Google Sheets Integration

Create `local_test/test_sheets.py`:

```python
#!/usr/bin/env python3
from src.services.sheets_service import SheetsService

def test_sheets_connection():
    service = SheetsService()
    meal_plan = service.fetch_meal_plan()
    
    print(f"Successfully loaded {len(meal_plan.meals)} days")
    print(f"Valid: {meal_plan.is_valid}")
    print(f"\nSample data - Monday breakfast:")
    print(meal_plan.meals['Monday']['breakfast'].name)

if __name__ == "__main__":
    test_sheets_connection()
```

Run:
```bash
python local_test/test_sheets.py
```

**Expected Output**:
```
Successfully loaded 7 days
Valid: True

Sample data - Monday breakfast:
Oatmeal
```

---

## Troubleshooting

### Issue: `gspread.exceptions.APIError: PERMISSION_DENIED`

**Solution**: Verify service account email has been granted access to the Google Sheet (Step 2.3)

---

### Issue: `FileNotFoundError: credentials.json`

**Solution**: Ensure `credentials.json` is in the project root directory

---

### Issue: `Import Error: No module named 'ask_sdk_core'`

**Solution**: 
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

### Issue: Empty/incorrect meal data

**Solution**: 
1. Verify Google Sheet structure matches template (Step 2.1)
2. Check that headers are in Row 1
3. Ensure day names are spelled correctly (Monday-Sunday)
4. Verify sheet name if using worksheet selection

---

## Step 6: Validate Installation

### 6.1 Run Complete Test Suite

```bash
# Run all tests at once
python3 local_test/test_runner.py
```

Expected output:
```
===========================
Test Summary
===========================
Tests Passed: 3/3
✓ All tests passed!
```

### 6.2 Run Individual Tests

**Unit Tests** (requires pytest):
```bash
# All unit tests
python3 -m pytest tests/unit/ -v

# Specific test files
python3 -m pytest tests/unit/test_time_periods.py -v
python3 -m pytest tests/unit/test_meal_service.py -v
python3 -m pytest tests/unit/test_models.py -v
```

**Google Sheets Integration**:
```bash
python3 local_test/test_sheets.py
```

**Manual Alexa Testing**:
```bash
# Interactive mode
python3 local_test/manual_test.py

# All scenarios
python3 local_test/manual_test.py --all

# Specific intent
python3 local_test/manual_test.py GetMealIntent_Dinner
```

### 6.3 Validation Checklist

- [ ] All unit tests pass (33 test cases)
- [ ] Google Sheets mock tests pass
- [ ] Manual Alexa tests return responses
- [ ] LaunchRequest returns welcome message
- [ ] GetMealIntent returns meals from sheet
- [ ] GetTodayMealsIntent filters by time
- [ ] Error handling works properly

---

## Next Steps

1. ✅ Local testing working
2. Configure Alexa Developer Console (see deployment docs)
3. Deploy to AWS Lambda (see deployment docs)
4. Test with actual Alexa device or simulator
5. Iterate on responses and add new features

---

## Development Workflow

**Typical development cycle**:

1. Update Google Sheet with new meals
2. Run tests: `python3 local_test/test_runner.py`
3. Test specific intents: `python3 local_test/manual_test.py`
4. Run unit tests: `python3 -m pytest tests/unit/ -v`
5. Deploy to Lambda (when ready for device testing)

**No deployment needed** for most development work - local testing covers 90% of scenarios!

---

## Project Structure Quick Reference

```
alexa-skill-weekly-menu/
├── src/
│   ├── models/              # Data classes
│   ├── services/            # Business logic
│   ├── handlers/            # Intent handlers
│   └── lambda_function.py   # Entry point
├── tests/                   # Automated tests
├── local_test/              # Manual testing scripts
├── credentials.json         # Google service account (DO NOT COMMIT)
├── .env                     # Environment config (DO NOT COMMIT)
└── requirements.txt         # Python dependencies
```

---

## Summary

You should now have:
- ✅ Python environment configured
- ✅ Google Sheets integrated
- ✅ Service account authentication working
- ✅ Local testing capability
- ✅ Sample data loaded

**Ready to start implementing!** Refer to `data-model.md` and `plan.md` for implementation details.
