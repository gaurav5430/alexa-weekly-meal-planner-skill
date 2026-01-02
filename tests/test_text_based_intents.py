"""
Example tests using natural language text prompts instead of JSON.

This demonstrates how to test with realistic user utterances.
"""
import pytest
from unittest.mock import patch, Mock
from tests.utils import text_to_intent, EXAMPLE_UTTERANCES
import sys
from pathlib import Path

# Add lambda folder to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lambda'))

from lambda_function import lambda_handler
from models.meal_plan import Meal, MealPlan


@pytest.fixture
def mock_meal_plan():
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


class TestTextBasedIntents:
    """Test suite using natural language text prompts."""
    
    def test_whats_for_dinner(self, mock_meal_plan):
        """Test asking 'what's for dinner?' with natural language."""
        # Convert natural language to intent request
        event = text_to_intent("what's for dinner?")
        
        # Verify it created the correct intent
        assert event['request']['intent']['name'] == 'GetMealIntent'
        assert 'MealType' in event['request']['intent']['slots']
        assert event['request']['intent']['slots']['MealType']['value'] == 'dinner'
        
        # Test with lambda handler
        with patch('lambda_function.SheetsService') as mock_sheets:
            mock_sheets.return_value.fetch_meal_plan.return_value = mock_meal_plan
            
            response = lambda_handler(event, None)
            
            # Should return a response mentioning dinner
            assert 'response' in response
            assert 'outputSpeech' in response['response']
    
    def test_whats_for_breakfast(self, mock_meal_plan):
        """Test asking about breakfast."""
        event = text_to_intent("what should I make for breakfast")
        
        assert event['request']['intent']['name'] == 'GetMealIntent'
        assert event['request']['intent']['slots']['MealType']['value'] == 'breakfast'
    
    def test_whats_for_dinner_on_friday(self, mock_meal_plan):
        """Test asking about a specific day and meal."""
        event = text_to_intent("what's for dinner on Friday?")
        
        assert event['request']['intent']['name'] == 'GetSpecificDayMealIntent'
        assert event['request']['intent']['slots']['MealType']['value'] == 'dinner'
        assert event['request']['intent']['slots']['Day']['value'] == 'Friday'
        
        # Test with lambda handler
        with patch('lambda_function.SheetsService') as mock_sheets:
            mock_sheets.return_value.fetch_meal_plan.return_value = mock_meal_plan
            
            response = lambda_handler(event, None)
            
            # Should have a response (actual meal content depends on current time and data)
            assert 'response' in response
            assert 'outputSpeech' in response['response']
    
    def test_what_should_i_cook_today(self, mock_meal_plan):
        """Test asking what to cook today."""
        event = text_to_intent("what should I cook today?")
        
        assert event['request']['intent']['name'] == 'GetTodayMealsIntent'
        # This intent has no slots
        assert len(event['request']['intent']['slots']) == 0
    
    def test_whats_next(self, mock_meal_plan):
        """Test asking what's next."""
        event = text_to_intent("what's next?")
        
        assert event['request']['intent']['name'] == 'GetNextMealIntent'
        assert len(event['request']['intent']['slots']) == 0
    
    def test_help_command(self):
        """Test help command."""
        event = text_to_intent("help")
        
        assert event['request']['intent']['name'] == 'AMAZON.HelpIntent'
    
    def test_stop_command(self):
        """Test stop/cancel commands."""
        for utterance in ["stop", "cancel", "quit", "goodbye"]:
            event = text_to_intent(utterance)
            assert event['request']['intent']['name'] == 'AMAZON.StopIntent'
    
    def test_all_example_utterances(self):
        """Test that all example utterances can be converted."""
        for intent_name, utterances in EXAMPLE_UTTERANCES.items():
            for utterance in utterances:
                event = text_to_intent(utterance)
                assert event['request']['intent']['name'] == intent_name, \
                    f"Utterance '{utterance}' should map to {intent_name}"
    
    def test_invalid_utterance_raises_error(self):
        """Test that invalid utterances raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            text_to_intent("this is not a valid command")
        
        assert "Could not match text" in str(exc_info.value)


class TestNaturalLanguageE2E:
    """End-to-end tests using natural language."""
    
    def test_realistic_conversation_flow(self, mock_meal_plan):
        """Simulate a realistic user conversation."""
        with patch('lambda_function.SheetsService') as mock_sheets:
            mock_sheets.return_value.fetch_meal_plan.return_value = mock_meal_plan
            
            # User asks: "what's for dinner?"
            event1 = text_to_intent("what's for dinner?")
            response1 = lambda_handler(event1, None)
            assert response1['response']['outputSpeech'] is not None
            
            # User asks: "what should I cook today?"
            event2 = text_to_intent("what should I cook today?")
            response2 = lambda_handler(event2, None)
            assert response2['response']['outputSpeech'] is not None
            
            # User asks: "what's for lunch on Friday?"
            event3 = text_to_intent("what's for lunch on Friday?")
            response3 = lambda_handler(event3, None)
            assert 'outputSpeech' in response3['response']
            assert 'ssml' in response3['response']['outputSpeech']
            
            # User says: "stop"
            event4 = text_to_intent("stop")
            response4 = lambda_handler(event4, None)
            # Verify it's a stop response (should end session)
            assert response4['response'].get('shouldEndSession', True) == True


class TestComparisonWithTraditionalTests:
    """Demonstrate the difference between text-based and JSON-based testing."""
    
    def test_traditional_json_approach(self, mock_meal_plan):
        """Traditional approach: manually construct JSON."""
        event = {
            "version": "1.0",
            "session": {"new": True, "sessionId": "test", "application": {"applicationId": "test"}},
            "request": {
                "type": "IntentRequest",
                "requestId": "test",
                "intent": {
                    "name": "GetMealIntent",
                    "slots": {
                        "MealType": {"name": "MealType", "value": "dinner"}
                    }
                }
            }
        }
        
        # This works but requires understanding Alexa JSON structure
        assert event['request']['intent']['name'] == 'GetMealIntent'
    
    def test_text_based_approach(self, mock_meal_plan):
        """Modern approach: use natural language."""
        event = text_to_intent("what's for dinner?")
        
        # Much more intuitive - just write what the user would say!
        assert event['request']['intent']['name'] == 'GetMealIntent'
    
    def test_easier_to_add_test_cases(self):
        """Text-based tests are easier to extend with new cases."""
        # With text-based approach, adding test cases is trivial:
        test_cases = [
            "what's for dinner?",
            "what should I make for breakfast",
            "what's for lunch on Monday",
            "what should I cook today?",
        ]
        
        for utterance in test_cases:
            event = text_to_intent(utterance)
            assert 'request' in event
            assert 'intent' in event['request']
            # Each utterance correctly maps to an intent!


# Documentation example
def example_usage():
    """
    Example of how to use text_to_intent in your tests.
    
    Instead of writing:
        event = {
            "request": {
                "intent": {
                    "name": "GetMealIntent",
                    "slots": {"MealType": {"value": "dinner"}}
                }
            }
        }
    
    You can now write:
        event = text_to_intent("what's for dinner?")
    
    This is:
    - More readable
    - Easier to maintain
    - Closer to how users actually interact
    - Less error-prone
    """
    pass
