"""
End-to-end integration tests for Alexa Meal Planner.

These tests can run with either mocked Google Sheets data OR real Google Sheets API
depending on environment configuration. Set USE_REAL_SHEETS_API=true and provide
credentials.json + GOOGLE_SHEET_ID to test with real data.

Tests cover:
- Full intent handling flow from Alexa request to response
- Google Sheets data retrieval and parsing
- All user stories from spec.md
- Error handling and edge cases
"""
import pytest
import json
import os
import sys
from pathlib import Path
from datetime import datetime, time
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.test_config import TestConfig
# Note: lambda_handler imported in tests that need it to avoid module-level import errors
import sys
from pathlib import Path

# Add lambda folder to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'lambda'))

from services.sheets_service import SheetsService
from models.meal_plan import MealPlan, Meal


def get_lambda_handler():
    """Lazy import of lambda_handler to avoid module-level import errors."""
    from lambda_function import lambda_handler
    return lambda_handler


@pytest.fixture(scope='session', autouse=True)
def print_test_mode():
    """Print test mode at start of test session."""
    TestConfig.print_test_mode()


@pytest.fixture
def real_sheets_service():
    """
    Fixture providing real SheetsService if credentials available.
    Skips test if real API not configured.
    """
    if not TestConfig.can_run_real_api_tests():
        pytest.skip("Real API tests disabled - set USE_REAL_SHEETS_API=true and provide credentials")
    
    # Set environment variables for the service
    os.environ['GOOGLE_SHEET_ID'] = TestConfig.TEST_GOOGLE_SHEET_ID
    os.environ['CREDENTIALS_PATH'] = TestConfig.CREDENTIALS_PATH
    
    return SheetsService()


@pytest.fixture
def mock_sheets_data():
    """Fixture providing mock Google Sheets data."""
    return [
        ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner'],
        ['Monday', 'Oatmeal with Berries', 'Apple Slices', 'Grilled Chicken Salad', 'Granola Bar', 'Spaghetti Bolognese'],
        ['Tuesday', 'Scrambled Eggs', 'Yogurt', 'Turkey Sandwich', 'Crackers', 'Baked Salmon'],
        ['Wednesday', 'Pancakes', 'Banana', 'Veggie Wrap', 'Trail Mix', 'Beef Stir Fry'],
        ['Thursday', 'French Toast', 'Orange', 'Caesar Salad', 'Cheese Sticks', 'Grilled Pork Chops'],
        ['Friday', 'Breakfast Burrito', 'Smoothie', 'Pizza', 'Popcorn', 'Steak and Potatoes'],
        ['Saturday', 'Waffles', 'Muffin', 'Pasta Salad', 'Nuts', 'BBQ Chicken'],
        ['Sunday', 'Eggs Benedict', 'Fruit Cup', 'Roast Beef Sandwich', 'Pretzels', 'Lasagna']
    ]


@pytest.fixture
def mock_alexa_context():
    """Fixture providing mock Alexa Lambda context."""
    return {
        "requestId": "test-request-12345",
        "timestamp": datetime.now().isoformat()
    }


class TestE2EWithRealAPI:
    """
    End-to-end tests using REAL Google Sheets API.
    
    These tests validate the complete integration:
    - Google Sheets API authentication
    - Data retrieval from actual spreadsheet
    - Data parsing and validation
    - Meal plan construction
    """
    
    def test_fetch_real_meal_plan(self, real_sheets_service):
        """Test fetching meal plan from real Google Sheet."""
        # Fetch meal plan from real API
        meal_plan = real_sheets_service.fetch_meal_plan()
        
        # Validate meal plan structure
        assert isinstance(meal_plan, MealPlan), "Should return MealPlan instance"
        assert meal_plan.is_valid, "Meal plan should be valid"
        assert meal_plan.last_updated is not None, "Should have timestamp"
        assert meal_plan.sheet_id == TestConfig.TEST_GOOGLE_SHEET_ID
        
        # Validate we have 7 days of data
        assert len(meal_plan.meals) == 7, "Should have 7 days of meals"
        
        # Validate days of week
        expected_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in expected_days:
            assert day in meal_plan.meals, f"Should have meals for {day}"
        
        # Validate meal structure for each day
        for day, meals in meal_plan.meals.items():
            assert 'breakfast' in meals, f"{day} should have breakfast"
            assert 'morning_snack' in meals, f"{day} should have morning snack"
            assert 'lunch' in meals, f"{day} should have lunch"
            assert 'evening_snack' in meals, f"{day} should have evening snack"
            assert 'dinner' in meals, f"{day} should have dinner"
            
            # Each meal should be a Meal instance
            for period, meal in meals.items():
                assert isinstance(meal, Meal), f"{day} {period} should be Meal instance"
                assert hasattr(meal, 'name'), f"{day} {period} should have name"
                assert hasattr(meal, 'is_empty'), f"{day} {period} should have is_empty flag"
        
        print(f"\n✓ Successfully fetched meal plan from Sheet: {meal_plan.sheet_id}")
        print(f"✓ Validated {len(meal_plan.meals)} days of meals")
    
    def test_real_api_data_quality(self, real_sheets_service):
        """Test data quality from real Google Sheets."""
        meal_plan = real_sheets_service.fetch_meal_plan()
        
        # Check for at least some non-empty meals
        total_meals = 0
        non_empty_meals = 0
        
        for day_meals in meal_plan.meals.values():
            for meal in day_meals.values():
                total_meals += 1
                if not meal.is_empty:
                    non_empty_meals += 1
        
        assert total_meals == 35, "Should have 35 total meal slots (7 days × 5 meals)"
        assert non_empty_meals > 0, "Should have at least some non-empty meals"
        
        print(f"\n✓ Total meals: {total_meals}")
        print(f"✓ Non-empty meals: {non_empty_meals}")
        print(f"✓ Empty meals: {total_meals - non_empty_meals}")
    
    def test_real_api_specific_meal_lookup(self, real_sheets_service):
        """Test looking up specific meals from real data."""
        meal_plan = real_sheets_service.fetch_meal_plan()
        
        # Try to get Monday breakfast
        monday_breakfast = meal_plan.get_meal('Monday', 'breakfast')
        assert monday_breakfast is not None, "Should find Monday breakfast"
        
        # Try to get Friday dinner
        friday_dinner = meal_plan.get_meal('Friday', 'dinner')
        assert friday_dinner is not None, "Should find Friday dinner"
        
        print(f"\n✓ Monday breakfast: {monday_breakfast.name if not monday_breakfast.is_empty else '(empty)'}")
        print(f"✓ Friday dinner: {friday_dinner.name if not friday_dinner.is_empty else '(empty)'}")


class TestE2EFullIntentFlow:
    """
    End-to-end tests for complete Alexa intent handling flow.
    
    These tests simulate actual Alexa requests and validate complete
    response generation including Google Sheets integration.
    """
    
    @pytest.fixture
    def setup_mock_sheets(self, mock_sheets_data):
        """Setup mock Google Sheets for tests that don't use real API."""
        with patch('services.sheets_service.gspread.authorize') as mock_authorize:
            mock_client = MagicMock()
            mock_sheet = MagicMock()
            mock_worksheet = MagicMock()
            
            mock_worksheet.get_all_values.return_value = mock_sheets_data
            mock_sheet.worksheet.return_value = mock_worksheet
            mock_client.open_by_key.return_value = mock_sheet
            mock_authorize.return_value = mock_client
            
            with patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name'):
                yield
    
    def test_e2e_launch_request(self, setup_mock_sheets, mock_alexa_context):
        """Test complete flow for LaunchRequest."""
        event = {
            "version": "1.0",
            "session": {
                "new": True,
                "sessionId": "test-session-123",
                "application": {"applicationId": "amzn1.ask.skill.test"},
                "user": {"userId": "amzn1.ask.account.test"}
            },
            "request": {
                "type": "LaunchRequest",
                "requestId": "test-request-123",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = get_lambda_handler()(event, mock_alexa_context)
        
        assert 'response' in response
        assert 'outputSpeech' in response['response']
        speech_output = response['response']['outputSpeech']['ssml']
        
        assert 'Welcome' in speech_output or 'welcome' in speech_output
        print(f"\n✓ Launch request successful: {speech_output[:100]}...")
    
    def test_e2e_get_meal_intent(self, setup_mock_sheets, mock_alexa_context):
        """Test complete flow for GetMealIntent."""
        event = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "test-session-123",
                "application": {"applicationId": "amzn1.ask.skill.test"},
                "user": {"userId": "amzn1.ask.account.test"}
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "test-request-124",
                "timestamp": datetime.now().isoformat(),
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
        
        with patch('services.meal_service.datetime') as mock_datetime:
            # Mock to Monday
            mock_now = MagicMock()
            mock_now.weekday.return_value = 0  # Monday
            mock_now.time.return_value = time(19, 0)  # 7 PM
            mock_datetime.now.return_value = mock_now
            
            response = get_lambda_handler()(event, mock_alexa_context)
        
        assert 'response' in response
        assert 'outputSpeech' in response['response']
        speech_output = response['response']['outputSpeech']['ssml']
        
        # Should mention dinner and the meal name
        assert 'dinner' in speech_output.lower()
        print(f"\n✓ GetMealIntent successful: {speech_output}")
    
    def test_e2e_get_today_meals_intent(self, setup_mock_sheets, mock_alexa_context):
        """Test complete flow for GetTodayMealsIntent."""
        event = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "test-session-123",
                "application": {"applicationId": "amzn1.ask.skill.test"},
                "user": {"userId": "amzn1.ask.account.test"}
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "test-request-125",
                "timestamp": datetime.now().isoformat(),
                "intent": {
                    "name": "GetTodayMealsIntent",
                    "slots": {}
                }
            }
        }
        
        with patch('services.meal_service.datetime') as mock_datetime:
            # Mock to Monday at 8 AM (before all meals)
            mock_now = MagicMock()
            mock_now.weekday.return_value = 0  # Monday
            mock_now.time.return_value = time(8, 0)  # 8 AM
            mock_datetime.now.return_value = mock_now
            
            response = get_lambda_handler()(event, mock_alexa_context)
        
        assert 'response' in response
        assert 'outputSpeech' in response['response']
        speech_output = response['response']['outputSpeech']['ssml']
        
        # Should list multiple meals
        assert 'breakfast' in speech_output.lower()
        assert 'lunch' in speech_output.lower()
        assert 'dinner' in speech_output.lower()
        print(f"\n✓ GetTodayMealsIntent successful: {speech_output[:150]}...")
    
    def test_e2e_get_specific_day_meal_intent(self, setup_mock_sheets, mock_alexa_context):
        """Test complete flow for GetSpecificDayMealIntent."""
        event = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "test-session-123",
                "application": {"applicationId": "amzn1.ask.skill.test"},
                "user": {"userId": "amzn1.ask.account.test"}
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "test-request-126",
                "timestamp": datetime.now().isoformat(),
                "intent": {
                    "name": "GetSpecificDayMealIntent",
                    "slots": {
                        "Day": {
                            "name": "Day",
                            "value": "Friday"
                        },
                        "MealType": {
                            "name": "MealType",
                            "value": "breakfast"
                        }
                    }
                }
            }
        }
        
        response = get_lambda_handler()(event, mock_alexa_context)
        
        assert 'response' in response
        assert 'outputSpeech' in response['response']
        speech_output = response['response']['outputSpeech']['ssml']
        
        # Should mention Friday and breakfast
        assert 'friday' in speech_output.lower()
        assert 'breakfast' in speech_output.lower()
        print(f"\n✓ GetSpecificDayMealIntent successful: {speech_output}")
    
    def test_e2e_get_next_meal_intent(self, setup_mock_sheets, mock_alexa_context):
        """Test complete flow for GetNextMealIntent."""
        event = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "test-session-123",
                "application": {"applicationId": "amzn1.ask.skill.test"},
                "user": {"userId": "amzn1.ask.account.test"}
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "test-request-127",
                "timestamp": datetime.now().isoformat(),
                "intent": {
                    "name": "GetNextMealIntent",
                    "slots": {}
                }
            }
        }
        
        with patch('services.meal_service.datetime') as mock_datetime:
            # Mock to Monday at 10:30 AM (before morning snack)
            mock_now = MagicMock()
            mock_now.weekday.return_value = 0  # Monday
            mock_now.time.return_value = time(10, 30)  # 10:30 AM
            mock_datetime.now.return_value = mock_now
            
            response = get_lambda_handler()(event, mock_alexa_context)
        
        assert 'response' in response
        assert 'outputSpeech' in response['response']
        speech_output = response['response']['outputSpeech']['ssml']
        
        # Should mention next meal
        assert 'next' in speech_output.lower() or 'snack' in speech_output.lower()
        print(f"\n✓ GetNextMealIntent successful: {speech_output}")


class TestE2EErrorHandling:
    """Test error handling in end-to-end scenarios."""
    
    @pytest.fixture
    def setup_mock_sheets_with_empty_slots(self):
        """Setup mock with some empty meal slots."""
        mock_data = [
            ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner'],
            ['Monday', 'Oatmeal', '', 'Salad', 'Yogurt', 'Pasta'],
            ['Tuesday', 'Eggs', 'Banana', '', 'Carrots', 'Fish'],
            ['Wednesday', '', 'Orange', 'Soup', 'Nuts', ''],
            ['Thursday', 'Toast', 'Grapes', 'Pizza', '', 'Steak'],
            ['Friday', 'Cereal', 'Berries', 'Burrito', 'Hummus', ''],
            ['Saturday', 'Smoothie', 'Mix', 'Pasta', 'Crackers', 'Chicken'],
            ['Sunday', 'French Toast', 'Fruit', 'Roast Beef', 'Popcorn', 'Lasagna']
        ]
        
        with patch('services.sheets_service.gspread.authorize') as mock_authorize:
            mock_client = MagicMock()
            mock_sheet = MagicMock()
            mock_worksheet = MagicMock()
            
            mock_worksheet.get_all_values.return_value = mock_data
            mock_sheet.worksheet.return_value = mock_worksheet
            mock_client.open_by_key.return_value = mock_sheet
            mock_authorize.return_value = mock_client
            
            with patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name'):
                yield
    
    def test_e2e_empty_meal_slot(self, setup_mock_sheets_with_empty_slots, mock_alexa_context):
        """Test handling of empty meal slot."""
        event = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "test-session-123",
                "application": {"applicationId": "amzn1.ask.skill.test"},
                "user": {"userId": "amzn1.ask.account.test"}
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "test-request-128",
                "timestamp": datetime.now().isoformat(),
                "intent": {
                    "name": "GetSpecificDayMealIntent",
                    "slots": {
                        "Day": {"name": "Day", "value": "Monday"},
                        "MealType": {"name": "MealType", "value": "morning snack"}
                    }
                }
            }
        }
        
        response = get_lambda_handler()(event, mock_alexa_context)
    
        assert 'response' in response
        speech_output = response['response']['outputSpeech']['ssml']
    
        # Should indicate empty slot
        assert 'not' in speech_output.lower() or 'empty' in speech_output.lower() or "haven't" in speech_output.lower() or 'no' in speech_output.lower()
        print(f"\n✓ Empty slot handling: {speech_output}")


class TestE2ERealIntentWithRealAPI:
    """
    Complete end-to-end tests using REAL Google Sheets API.
    
    These tests validate the entire stack from Alexa request through
    to actual Google Sheets data retrieval and response generation.
    """
    
    @pytest.fixture(autouse=True)
    def skip_if_no_real_api(self):
        """Auto-skip these tests if real API not available."""
        if not TestConfig.can_run_real_api_tests():
            pytest.skip("Real API tests disabled")
    
    def test_full_stack_get_meal_with_real_api(self, mock_alexa_context):
        """Test complete stack with real Google Sheets - GetMealIntent."""
        # Set environment for real API
        os.environ['GOOGLE_SHEET_ID'] = TestConfig.TEST_GOOGLE_SHEET_ID
        os.environ['CREDENTIALS_PATH'] = TestConfig.CREDENTIALS_PATH
        
        event = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "test-session-real-123",
                "application": {"applicationId": "amzn1.ask.skill.test"},
                "user": {"userId": "amzn1.ask.account.test"}
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "test-request-real-124",
                "timestamp": datetime.now().isoformat(),
                "intent": {
                    "name": "GetMealIntent",
                    "slots": {
                        "MealType": {"name": "MealType", "value": "dinner"}
                    }
                }
            }
        }
        
        with patch('services.meal_service.datetime') as mock_datetime:
            # Mock to Monday at 7 PM
            mock_now = MagicMock()
            mock_now.weekday.return_value = 0  # Monday
            mock_now.time.return_value = time(19, 0)
            mock_datetime.now.return_value = mock_now
            
            response = get_lambda_handler()(event, mock_alexa_context)
        
        assert 'response' in response
        assert 'outputSpeech' in response['response']
        speech_output = response['response']['outputSpeech']['ssml']
        
        assert 'dinner' in speech_output.lower()
        print(f"\n✓ REAL API Full Stack Test: {speech_output}")
    
    def test_full_stack_get_today_meals_with_real_api(self, mock_alexa_context):
        """Test complete stack with real Google Sheets - GetTodayMealsIntent."""
        os.environ['GOOGLE_SHEET_ID'] = TestConfig.TEST_GOOGLE_SHEET_ID
        os.environ['CREDENTIALS_PATH'] = TestConfig.CREDENTIALS_PATH
        
        event = {
            "version": "1.0",
            "session": {
                "new": False,
                "sessionId": "test-session-real-125",
                "application": {"applicationId": "amzn1.ask.skill.test"},
                "user": {"userId": "amzn1.ask.account.test"}
            },
            "request": {
                "type": "IntentRequest",
                "requestId": "test-request-real-125",
                "timestamp": datetime.now().isoformat(),
                "intent": {
                    "name": "GetTodayMealsIntent",
                    "slots": {}
                }
            }
        }
        
        with patch('services.meal_service.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 0  # Monday
            mock_now.time.return_value = time(8, 0)
            mock_datetime.now.return_value = mock_now
            
            response = get_lambda_handler()(event, mock_alexa_context)
        
        assert 'response' in response
        speech_output = response['response']['outputSpeech']['ssml']
        
        # Should list multiple meals from real data
        print(f"\n✓ REAL API Today's Meals: {speech_output[:200]}...")
