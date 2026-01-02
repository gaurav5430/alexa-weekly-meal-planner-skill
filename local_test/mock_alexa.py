"""
Mock Alexa request builder for local testing.
"""
from datetime import datetime
from typing import Optional, Dict, Any


def create_launch_request(session_id: str = "test-session-123") -> Dict[str, Any]:
    """
    Create a LaunchRequest event.
    
    Args:
        session_id: Optional session ID
    
    Returns:
        Alexa LaunchRequest event
    """
    return {
        "version": "1.0",
        "session": {
            "new": True,
            "sessionId": session_id,
            "application": {
                "applicationId": "amzn1.ask.skill.test"
            },
            "user": {
                "userId": "amzn1.ask.account.test"
            }
        },
        "request": {
            "type": "LaunchRequest",
            "requestId": f"amzn1.echo-api.request.{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "locale": "en-US"
        }
    }


def create_intent_request(
    intent_name: str,
    slots: Optional[Dict[str, str]] = None,
    session_id: str = "test-session-123"
) -> Dict[str, Any]:
    """
    Create an IntentRequest event.
    
    Args:
        intent_name: Name of the intent (e.g., "GetMealIntent")
        slots: Dictionary of slot names to values
        session_id: Optional session ID
    
    Returns:
        Alexa IntentRequest event
    """
    # Build slots structure
    intent_slots = {}
    if slots:
        for slot_name, slot_value in slots.items():
            intent_slots[slot_name] = {
                "name": slot_name,
                "value": slot_value,
                "confirmationStatus": "NONE"
            }
    
    return {
        "version": "1.0",
        "session": {
            "new": False,
            "sessionId": session_id,
            "application": {
                "applicationId": "amzn1.ask.skill.test"
            },
            "user": {
                "userId": "amzn1.ask.account.test"
            }
        },
        "request": {
            "type": "IntentRequest",
            "requestId": f"amzn1.echo-api.request.{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "locale": "en-US",
            "intent": {
                "name": intent_name,
                "confirmationStatus": "NONE",
                "slots": intent_slots
            }
        }
    }


def create_session_ended_request(
    reason: str = "USER_INITIATED",
    session_id: str = "test-session-123"
) -> Dict[str, Any]:
    """
    Create a SessionEndedRequest event.
    
    Args:
        reason: Reason for session end (USER_INITIATED, ERROR, EXCEEDED_MAX_REPROMPTS)
        session_id: Optional session ID
    
    Returns:
        Alexa SessionEndedRequest event
    """
    return {
        "version": "1.0",
        "session": {
            "new": False,
            "sessionId": session_id,
            "application": {
                "applicationId": "amzn1.ask.skill.test"
            },
            "user": {
                "userId": "amzn1.ask.account.test"
            }
        },
        "request": {
            "type": "SessionEndedRequest",
            "requestId": f"amzn1.echo-api.request.{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "locale": "en-US",
            "reason": reason
        }
    }


# Convenience functions for common intents

def create_get_meal_request(meal_type: str) -> Dict[str, Any]:
    """Create GetMealIntent request."""
    return create_intent_request("GetMealIntent", {"MealType": meal_type})


def create_get_today_meals_request() -> Dict[str, Any]:
    """Create GetTodayMealsIntent request."""
    return create_intent_request("GetTodayMealsIntent")


def create_get_specific_day_meal_request(day: str, meal_type: str) -> Dict[str, Any]:
    """Create GetSpecificDayMealIntent request."""
    return create_intent_request(
        "GetSpecificDayMealIntent",
        {"Day": day, "MealType": meal_type}
    )


def create_get_next_meal_request() -> Dict[str, Any]:
    """Create GetNextMealIntent request."""
    return create_intent_request("GetNextMealIntent")


def create_help_request() -> Dict[str, Any]:
    """Create AMAZON.HelpIntent request."""
    return create_intent_request("AMAZON.HelpIntent")


def create_cancel_request() -> Dict[str, Any]:
    """Create AMAZON.CancelIntent request."""
    return create_intent_request("AMAZON.CancelIntent")


def create_stop_request() -> Dict[str, Any]:
    """Create AMAZON.StopIntent request."""
    return create_intent_request("AMAZON.StopIntent")
