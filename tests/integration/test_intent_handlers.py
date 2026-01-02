"""
Integration tests for intent handlers with mock Alexa events.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import handlers
import sys
from pathlib import Path

# Add lambda folder to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'lambda'))

from handlers.intent_handlers import (
    LaunchRequestHandler,
    GetMealIntentHandler,
    GetTodayMealsIntentHandler,
    GetSpecificDayMealIntentHandler,
    GetNextMealIntentHandler,
    HelpIntentHandler,
    CancelOrStopIntentHandler,
)
from models.meal_plan import Meal, MealPlan


@pytest.fixture
def sample_meal_plan():
    """Create a sample meal plan for testing."""
    meals = {
        "Monday": {
            "breakfast": Meal("Monday", "breakfast", "Oatmeal"),
            "lunch": Meal("Monday", "lunch", "Salad"),
            "dinner": Meal("Monday", "dinner", "Pasta")
        },
        "Friday": {
            "breakfast": Meal("Friday", "breakfast", "Pancakes"),
            "lunch": Meal("Friday", "lunch", "Pizza"),
            "dinner": Meal("Friday", "dinner", "Steak")
        }
    }
    return MealPlan(meals, is_valid=True)


@pytest.fixture
def mock_handler_input():
    """Create mock handler input."""
    mock_input = Mock()
    mock_input.response_builder = Mock()
    mock_input.response_builder.speak = Mock(return_value=mock_input.response_builder)
    mock_input.response_builder.ask = Mock(return_value=mock_input.response_builder)
    mock_input.response_builder.response = {"version": "1.0", "response": {}}
    return mock_input


@pytest.fixture
def load_mock_requests():
    """Load mock Alexa requests from fixtures."""
    fixtures_path = Path(__file__).parent.parent / "fixtures" / "mock_alexa_requests.json"
    with open(fixtures_path, 'r') as f:
        return json.load(f)


class TestLaunchRequestHandler:
    """Test LaunchRequestHandler."""
    
    def test_can_handle_launch_request(self):
        """Test that handler recognizes LaunchRequest."""
        handler = LaunchRequestHandler()
        
        mock_input = Mock()
        mock_input.request_envelope.request.object_type = "LaunchRequest"
        
        # Test can_handle directly
        assert handler.can_handle(mock_input) is True
    
    def test_returns_welcome_message(self, mock_handler_input):
        """Test that handler returns welcome message."""
        handler = LaunchRequestHandler()
        
        response = handler.handle(mock_handler_input)
        
        # Verify response builder was called
        assert mock_handler_input.response_builder.speak.called
        speak_args = mock_handler_input.response_builder.speak.call_args[0][0]
        assert "Welcome" in speak_args or "welcome" in speak_args


class TestGetMealIntentHandler:
    """Test GetMealIntentHandler."""
    
    def test_handles_valid_meal_request(self, mock_handler_input, sample_meal_plan, monkeypatch):
        """Test handling valid meal request."""
        # Mock slots
        mock_slots = {
            "MealType": Mock(value="breakfast")
        }
        mock_handler_input.request_envelope.request.intent.slots = mock_slots
        
        # Mock MealService
        with patch('handlers.intent_handlers.SheetsService') as mock_sheets:
            mock_sheets.return_value.fetch_meal_plan.return_value = sample_meal_plan
            
            # Mock datetime to return Monday
            class MockDatetime:
                @staticmethod
                def now():
                    class MockNow:
                        def weekday(self):
                            return 0  # Monday
                    return MockNow()
            
            with patch('services.meal_service.datetime', MockDatetime):
                handler = GetMealIntentHandler()
                response = handler.handle(mock_handler_input)
                
                # Verify speak was called
                assert mock_handler_input.response_builder.speak.called
    
    def test_handles_missing_meal_type_slot(self, mock_handler_input):
        """Test handling request with missing meal type."""
        mock_handler_input.request_envelope.request.intent.slots = {}
        
        handler = GetMealIntentHandler()
        response = handler.handle(mock_handler_input)
        
        # Verify error response
        assert mock_handler_input.response_builder.speak.called
        speak_args = mock_handler_input.response_builder.speak.call_args[0][0]
        assert "missing" in speak_args.lower() or "sorry" in speak_args.lower()


class TestGetTodayMealsIntentHandler:
    """Test GetTodayMealsIntentHandler."""
    
    def test_returns_remaining_meals(self, mock_handler_input, sample_meal_plan):
        """Test that remaining meals are returned."""
        with patch('handlers.intent_handlers.SheetsService') as mock_sheets:
            mock_sheets.return_value.fetch_meal_plan.return_value = sample_meal_plan
            
            handler = GetTodayMealsIntentHandler()
            response = handler.handle(mock_handler_input)
            
            # Verify speak was called
            assert mock_handler_input.response_builder.speak.called


class TestGetSpecificDayMealIntentHandler:
    """Test GetSpecificDayMealIntentHandler."""
    
    def test_handles_specific_day_request(self, mock_handler_input, sample_meal_plan):
        """Test handling specific day and meal request."""
        mock_slots = {
            "Day": Mock(value="Friday"),
            "MealType": Mock(value="lunch")
        }
        mock_handler_input.request_envelope.request.intent.slots = mock_slots
        
        with patch('handlers.intent_handlers.SheetsService') as mock_sheets:
            mock_sheets.return_value.fetch_meal_plan.return_value = sample_meal_plan
            
            handler = GetSpecificDayMealIntentHandler()
            response = handler.handle(mock_handler_input)
            
            # Verify speak was called
            assert mock_handler_input.response_builder.speak.called
            speak_args = mock_handler_input.response_builder.speak.call_args[0][0]
            # Should mention Pizza (Friday lunch in sample data)
            assert "Pizza" in speak_args or "pizza" in speak_args
    
    def test_handles_missing_slots(self, mock_handler_input):
        """Test handling request with missing slots."""
        mock_handler_input.request_envelope.request.intent.slots = {}
        
        handler = GetSpecificDayMealIntentHandler()
        response = handler.handle(mock_handler_input)
        
        # Verify error response
        assert mock_handler_input.response_builder.speak.called


class TestGetNextMealIntentHandler:
    """Test GetNextMealIntentHandler."""
    
    def test_returns_next_meal(self, mock_handler_input, sample_meal_plan):
        """Test that next meal is returned."""
        with patch('handlers.intent_handlers.SheetsService') as mock_sheets:
            mock_sheets.return_value.fetch_meal_plan.return_value = sample_meal_plan
            
            handler = GetNextMealIntentHandler()
            response = handler.handle(mock_handler_input)
            
            # Verify speak was called
            assert mock_handler_input.response_builder.speak.called


class TestHelpIntentHandler:
    """Test HelpIntentHandler."""
    
    def test_returns_help_message(self, mock_handler_input):
        """Test that help message is returned."""
        handler = HelpIntentHandler()
        response = handler.handle(mock_handler_input)
        
        # Verify speak was called
        assert mock_handler_input.response_builder.speak.called
        speak_args = mock_handler_input.response_builder.speak.call_args[0][0]
        assert "ask" in speak_args.lower() or "try" in speak_args.lower()


class TestCancelOrStopIntentHandler:
    """Test CancelOrStopIntentHandler."""
    
    def test_returns_goodbye_message(self, mock_handler_input):
        """Test that goodbye message is returned."""
        handler = CancelOrStopIntentHandler()
        response = handler.handle(mock_handler_input)
        
        # Verify speak was called
        assert mock_handler_input.response_builder.speak.called
        speak_args = mock_handler_input.response_builder.speak.call_args[0][0]
        assert "goodbye" in speak_args.lower() or "bye" in speak_args.lower()
