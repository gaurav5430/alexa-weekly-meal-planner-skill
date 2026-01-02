#!/usr/bin/env python3
"""
Simple debugging script for testing Alexa skill locally.
Set breakpoints in your skill code, then run this script with the debugger.
"""

import json
import sys
import os
from pathlib import Path

# Add lambda to path (go up 2 levels from scripts/debug to workspace root)
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root / 'lambda'))

from lambda_function import lambda_handler


def create_intent_request(intent_name, slots=None):
    """Create a mock Alexa request for testing."""
    return {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'debug-session-' + intent_name,
            'application': {
                'applicationId': 'amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746'
            },
            'user': {
                'userId': 'debug-user-123'
            }
        },
        'request': {
            'type': 'IntentRequest',
            'requestId': 'debug-request-' + intent_name,
            'intent': {
                'name': intent_name,
                'slots': slots or {}
            },
            'locale': 'en-US'
        }
    }


def test_get_meal_intent():
    """Test GetMealIntent with different meal types."""
    print("\n" + "="*60)
    print("🧪 Testing GetMealIntent")
    print("="*60)
    
    meal_types = ['breakfast', 'lunch', 'dinner', 'morning snack', 'evening snack']
    
    for meal_type in meal_types:
        print(f"\n📍 Testing: {meal_type}")
        request = create_intent_request('GetMealIntent', {
            'MealType': {
                'name': 'MealType',
                'value': meal_type
            }
        })
        
        # SET BREAKPOINT HERE to debug the handler
        response = lambda_handler(request, None)
        
        output = response.get('response', {}).get('outputSpeech', {})
        text = output.get('text') or output.get('ssml', 'No response')
        print(f"   🗣️  Alexa: {text[:100]}...")


def test_get_today_meals():
    """Test GetTodayMealsIntent."""
    print("\n" + "="*60)
    print("🧪 Testing GetTodayMealsIntent")
    print("="*60)
    
    request = create_intent_request('GetTodayMealsIntent')
    
    # SET BREAKPOINT HERE to debug the handler
    response = lambda_handler(request, None)
    
    output = response.get('response', {}).get('outputSpeech', {})
    text = output.get('text') or output.get('ssml', 'No response')
    print(f"   🗣️  Alexa: {text[:200]}...")


def test_get_specific_day_meal():
    """Test GetSpecificDayMealIntent."""
    print("\n" + "="*60)
    print("🧪 Testing GetSpecificDayMealIntent")
    print("="*60)
    
    days = ['monday', 'tuesday', 'friday']
    
    for day in days:
        print(f"\n📍 Testing: dinner on {day}")
        request = create_intent_request('GetSpecificDayMealIntent', {
            'Day': {
                'name': 'Day',
                'value': day
            },
            'MealType': {
                'name': 'MealType',
                'value': 'dinner'
            }
        })
        
        # SET BREAKPOINT HERE to debug the handler
        response = lambda_handler(request, None)
        
        output = response.get('response', {}).get('outputSpeech', {})
        text = output.get('text') or output.get('ssml', 'No response')
        print(f"   🗣️  Alexa: {text[:100]}...")


def test_get_next_meal():
    """Test GetNextMealIntent."""
    print("\n" + "="*60)
    print("🧪 Testing GetNextMealIntent")
    print("="*60)
    
    request = create_intent_request('GetNextMealIntent')
    
    # SET BREAKPOINT HERE to debug the handler
    response = lambda_handler(request, None)
    
    output = response.get('response', {}).get('outputSpeech', {})
    text = output.get('text') or output.get('ssml', 'No response')
    print(f"   🗣️  Alexa: {text[:200]}...")


def test_launch_request():
    """Test LaunchRequest."""
    print("\n" + "="*60)
    print("🧪 Testing LaunchRequest (Alexa, open weekly meal planner)")
    print("="*60)
    
    request = {
        'version': '1.0',
        'session': {
            'new': True,
            'sessionId': 'debug-session-launch',
            'application': {
                'applicationId': 'amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746'
            },
            'user': {
                'userId': 'debug-user-123'
            }
        },
        'request': {
            'type': 'LaunchRequest',
            'requestId': 'debug-request-launch',
            'locale': 'en-US'
        }
    }
    
    # SET BREAKPOINT HERE to debug the handler
    response = lambda_handler(request, None)
    
    output = response.get('response', {}).get('outputSpeech', {})
    text = output.get('text') or output.get('ssml', 'No response')
    print(f"   🗣️  Alexa: {text}")


def main():
    """Run all tests."""
    print("\n" + "🚀 "*30)
    print("ALEXA SKILL LOCAL DEBUG SCRIPT")
    print("🚀 "*30)
    print("\nSet breakpoints in your code and run this with VS Code debugger!")
    print("Or just run it directly to see responses.\n")
    
    try:
        # Run all tests
        test_launch_request()
        test_get_meal_intent()
        test_get_today_meals()
        test_get_specific_day_meal()
        test_get_next_meal()
        
        print("\n" + "✅ "*30)
        print("ALL TESTS COMPLETED!")
        print("✅ "*30 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
