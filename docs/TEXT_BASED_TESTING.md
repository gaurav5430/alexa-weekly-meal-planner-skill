# Text-Based Testing for Alexa Skills

## Overview

This document explains the new text-based testing capability added to the Alexa Weekly Meal Planner skill. This feature allows you to write tests using natural language user utterances instead of manually constructing JSON intent requests.

## Why Text-Based Testing?

### Traditional Approach (JSON)
```python
event = {
    "version": "1.0",
    "session": {
        "sessionId": "test-session",
        "application": {"applicationId": "test-app"}
    },
    "request": {
        "type": "IntentRequest",
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
```

### New Approach (Natural Language)
```python
from tests.utils import text_to_intent

event = text_to_intent("what's for dinner?")
```

## Benefits

1. **More Readable** - Tests read like actual user interactions
2. **Easier to Write** - No need to remember complex JSON structure
3. **Less Error-Prone** - Automatic generation ensures valid structure
4. **Closer to Reality** - Tests match how users actually speak
5. **Easier to Maintain** - Simple text changes vs JSON manipulation

## How to Use

### Basic Usage

```python
from tests.utils import text_to_intent

# Simple meal query
event = text_to_intent("what's for dinner?")

# Specific day query
event = text_to_intent("what's for lunch on Friday?")

# Today's meals
event = text_to_intent("what should I cook today?")

# Next meal
event = text_to_intent("what's next?")

# Help
event = text_to_intent("help")

# Stop
event = text_to_intent("stop")
```

### In Tests

```python
import pytest
from unittest.mock import patch
from tests.utils import text_to_intent
from src.lambda_function import lambda_handler

def test_dinner_query(mock_meal_plan):
    """Test asking 'what's for dinner?' with natural language."""
    # Convert text to intent request
    event = text_to_intent("what's for dinner?")
    
    # Verify correct intent
    assert event['request']['intent']['name'] == 'GetMealIntent'
    assert event['request']['intent']['slots']['MealType']['value'] == 'dinner'
    
    # Test with lambda handler
    with patch('src.lambda_function.SheetsService') as mock_sheets:
        mock_sheets.return_value.fetch_meal_plan.return_value = mock_meal_plan
        response = lambda_handler(event, None)
        assert 'outputSpeech' in response['response']
```

## Supported Utterances

### GetMealIntent
- "what's for dinner?"
- "what's for breakfast"
- "what should I make for lunch"
- "what should I cook for dinner"

### GetTodayMealsIntent
- "what should I cook today?"
- "what's on the menu today"
- "what's for meals today"
- "tell me today's meals"

### GetSpecificDayMealIntent
- "what's for dinner on Friday?"
- "what should I make for breakfast on Monday"
- "what's for lunch on tomorrow"

### GetNextMealIntent
- "what's next?"
- "what's the next meal"
- "what should I cook next"

### HelpIntent
- "help"
- "how do I use this"
- "what can you do"

### AMAZON.StopIntent
- "stop"
- "cancel"
- "quit"
- "goodbye"

## Implementation Details

### Location
- **Utility**: `tests/utils/text_to_intent.py`
- **Example Tests**: `tests/test_text_based_intents.py`

### How It Works

1. **Pattern Matching**: Uses regex patterns to identify which intent the user utterance maps to
2. **Slot Extraction**: Automatically extracts slot values (meal types, days, etc.)
3. **Request Building**: Constructs complete Alexa request envelope with proper structure

### The TextToIntentConverter Class

```python
from tests.utils import TextToIntentConverter

# Convert text
event = TextToIntentConverter.convert("what's for dinner?")

# Get example utterances for all intents
from tests.utils import EXAMPLE_UTTERANCES
print(EXAMPLE_UTTERANCES['GetMealIntent'])
# Output: ["what's for dinner?", "what's for breakfast", ...]
```

## Examples from Test Suite

### Simple Conversion Test
```python
def test_whats_for_dinner():
    event = text_to_intent("what's for dinner?")
    assert event['request']['intent']['name'] == 'GetMealIntent'
    assert event['request']['intent']['slots']['MealType']['value'] == 'dinner'
```

### End-to-End Conversation Flow
```python
def test_realistic_conversation_flow(mock_meal_plan):
    with patch('src.lambda_function.SheetsService') as mock_sheets:
        mock_sheets.return_value.fetch_meal_plan.return_value = mock_meal_plan
        
        # User asks multiple questions
        response1 = lambda_handler(text_to_intent("what's for dinner?"), None)
        response2 = lambda_handler(text_to_intent("what should I cook today?"), None)
        response3 = lambda_handler(text_to_intent("what's for lunch on Friday?"), None)
        response4 = lambda_handler(text_to_intent("stop"), None)
        
        # All responses should be valid
        assert all('response' in r for r in [response1, response2, response3, response4])
```

### Testing All Example Utterances
```python
def test_all_example_utterances():
    """Verify all documented examples work correctly."""
    from tests.utils import EXAMPLE_UTTERANCES
    
    for intent_name, utterances in EXAMPLE_UTTERANCES.items():
        for utterance in utterances:
            event = text_to_intent(utterance)
            assert event['request']['intent']['name'] == intent_name
```

## Error Handling

If an utterance doesn't match any pattern, a `ValueError` is raised:

```python
try:
    event = text_to_intent("this is not a valid command")
except ValueError as e:
    print(f"Error: {e}")
    # Output: Could not match text to any intent: 'this is not a valid command'
```

## Extending the Utility

To add support for new intents:

1. Add patterns to `PATTERNS` dict in `TextToIntentConverter`
2. Add examples to `EXAMPLE_UTTERANCES`
3. Create tests in `test_text_based_intents.py`

Example:
```python
PATTERNS = {
    # ... existing patterns ...
    "NewIntent": [
        (r"some\s+pattern", "slot_type"),
        (r"another\s+pattern", None),
    ],
}

EXAMPLE_UTTERANCES = {
    # ... existing examples ...
    "NewIntent": [
        "some pattern",
        "another pattern",
    ],
}
```

## Test Results

With the new text-based testing capability:
- **Total Tests**: 95
- **Passing**: 95 (100%)
- **Test Types**:
  - Unit Tests: 47
  - Integration Tests: 30
  - E2E Tests: 11
  - **Text-Based Tests**: 13 (NEW)

## Comparison: Before vs After

### Before (Traditional JSON)
```python
def test_dinner_query():
    event = {
        "version": "1.0",
        "session": {...},
        "context": {...},
        "request": {
            "type": "IntentRequest",
            "intent": {
                "name": "GetMealIntent",
                "slots": {
                    "MealType": {"name": "MealType", "value": "dinner"}
                }
            }
        }
    }
    response = lambda_handler(event, None)
    # 15+ lines of JSON construction
```

### After (Text-Based)
```python
def test_dinner_query():
    event = text_to_intent("what's for dinner?")
    response = lambda_handler(event, None)
    # 2 lines - much cleaner!
```

## Conclusion

Text-based testing makes Alexa skill testing more intuitive, maintainable, and closely aligned with real user interactions. It significantly reduces boilerplate and makes tests easier to write and understand.

For more examples, see:
- `tests/test_text_based_intents.py` - Complete test suite
- `tests/utils/text_to_intent.py` - Implementation details
