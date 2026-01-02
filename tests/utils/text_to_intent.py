"""
Utility to convert natural language text prompts into Alexa intent requests.

This allows testing with realistic user utterances instead of manually crafting JSON.
"""
import re
from typing import Dict, Optional, Any
from datetime import datetime


class TextToIntentConverter:
    """Converts natural language text to Alexa intent requests."""
    
    # Pattern matching for different intents
    PATTERNS = {
        "GetSpecificDayMealIntent": [
            (r"what'?s?\s+for\s+(breakfast|lunch|dinner|morning\s+snack|evening\s+snack)\s+on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today)", "meal_and_day"),
            (r"what\s+should\s+i\s+(?:make|cook|prepare)\s+for\s+(breakfast|lunch|dinner)\s+on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow)", "meal_and_day"),
        ],
        "GetMealIntent": [
            (r"what'?s?\s+for\s+(breakfast|lunch|dinner|morning\s+snack|evening\s+snack)(?:\s*\?)?$", "meal_type"),
            (r"what\s+should\s+i\s+(?:make|cook|prepare)\s+for\s+(breakfast|lunch|dinner)(?:\s*\?)?$", "meal_type"),
        ],
        "GetTodayMealsIntent": [
            (r"what\s+should\s+i\s+(?:cook|make)\s+today", None),
            (r"what'?s?\s+on\s+the\s+menu\s+today", None),
            (r"what'?s?\s+for\s+meals\s+today", None),
            (r"tell\s+me\s+today'?s?\s+meals", None),
        ],
        "GetNextMealIntent": [
            (r"what'?s?\s+next", None),
            (r"what'?s?\s+the\s+next\s+meal", None),
            (r"what\s+should\s+i\s+(?:cook|make)\s+next", None),
        ],
        "AMAZON.HelpIntent": [
            (r"help", None),
            (r"how\s+do\s+i\s+use\s+this", None),
            (r"what\s+can\s+you\s+do", None),
        ],
        "AMAZON.StopIntent": [
            (r"stop", None),
            (r"cancel", None),
            (r"quit", None),
            (r"exit", None),
            (r"goodbye", None),
        ],
    }
    
    @classmethod
    def convert(cls, text: str, request_id: Optional[str] = None, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert natural language text to an Alexa intent request.
        
        Args:
            text: Natural language user utterance
            request_id: Optional request ID (auto-generated if not provided)
            timestamp: Optional timestamp (current time if not provided)
        
        Returns:
            Complete Alexa request envelope as dict
        
        Raises:
            ValueError: If text doesn't match any known intent pattern
        """
        text_lower = text.lower().strip()
        
        # Try to match against patterns
        for intent_name, patterns in cls.PATTERNS.items():
            for pattern, slot_type in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    slots = cls._extract_slots(match, slot_type)
                    return cls._build_request(intent_name, slots, request_id, timestamp)
        
        raise ValueError(f"Could not match text to any intent: '{text}'")
    
    @classmethod
    def _extract_slots(cls, match: re.Match, slot_type: Optional[str]) -> Dict[str, Dict[str, str]]:
        """Extract slot values from regex match."""
        slots = {}
        
        if slot_type == "meal_type":
            # Extract meal type from first captured group
            meal_type = match.group(1).strip().lower()
            meal_type = meal_type.replace(" ", "_")  # "morning snack" -> "morning_snack"
            slots["MealType"] = {
                "name": "MealType",
                "value": meal_type
            }
        elif slot_type == "meal_and_day":
            # Extract both meal type and day from captured groups
            if match.lastindex and match.lastindex >= 2:
                meal_type = match.group(1).strip().lower().replace(" ", "_")
                day = match.group(2).strip().capitalize()
                
                slots["MealType"] = {
                    "name": "MealType",
                    "value": meal_type
                }
                slots["Day"] = {
                    "name": "Day",
                    "value": day
                }
        
        return slots
    
    @classmethod
    def _build_request(cls, intent_name: str, slots: Dict[str, Dict[str, str]], 
                      request_id: Optional[str] = None, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """Build complete Alexa request envelope."""
        if request_id is None:
            request_id = f"amzn1.echo-api.request.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if timestamp is None:
            timestamp = datetime.now().isoformat() + "Z"
        
        # Map intent names that might need special handling
        request_type = "IntentRequest"
        if "AMAZON." in intent_name:
            intent_name_to_use = intent_name
        else:
            intent_name_to_use = intent_name
        
        return {
            "version": "1.0",
            "session": {
                "new": True,
                "sessionId": f"amzn1.echo-api.session.{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "application": {
                    "applicationId": "amzn1.ask.skill.test"
                },
                "user": {
                    "userId": "amzn1.ask.account.TEST"
                },
                "attributes": {}
            },
            "context": {
                "System": {
                    "application": {
                        "applicationId": "amzn1.ask.skill.test"
                    },
                    "user": {
                        "userId": "amzn1.ask.account.TEST"
                    },
                    "device": {
                        "deviceId": "amzn1.ask.device.TEST",
                        "supportedInterfaces": {}
                    },
                    "apiEndpoint": "https://api.amazonalexa.com",
                    "apiAccessToken": "test_token"
                }
            },
            "request": {
                "type": request_type,
                "requestId": request_id,
                "timestamp": timestamp,
                "locale": "en-US",
                "intent": {
                    "name": intent_name_to_use,
                    "confirmationStatus": "NONE",
                    "slots": slots
                }
            }
        }


def text_to_intent(text: str) -> Dict[str, Any]:
    """
    Convenience function to convert text to intent request.
    
    Args:
        text: Natural language user utterance
    
    Returns:
        Complete Alexa request envelope as dict
    
    Example:
        >>> request = text_to_intent("what's for dinner?")
        >>> request['request']['intent']['name']
        'GetMealIntent'
    """
    return TextToIntentConverter.convert(text)


# Example usage patterns for documentation
EXAMPLE_UTTERANCES = {
    "GetMealIntent": [
        "what's for dinner?",
        "what's for breakfast",
        "what should I make for lunch",
        "what should I cook for dinner",
    ],
    "GetTodayMealsIntent": [
        "what should I cook today?",
        "what's on the menu today",
        "what's for meals today",
        "tell me today's meals",
    ],
    "GetSpecificDayMealIntent": [
        "what's for dinner on Friday?",
        "what should I make for breakfast on Monday",
        "what's for lunch on tomorrow",
    ],
    "GetNextMealIntent": [
        "what's next?",
        "what's the next meal",
        "what should I cook next",
    ],
    "AMAZON.HelpIntent": [
        "help",
        "how do I use this",
        "what can you do",
    ],
    "AMAZON.StopIntent": [
        "stop",
        "cancel",
        "quit",
        "goodbye",
    ],
}
