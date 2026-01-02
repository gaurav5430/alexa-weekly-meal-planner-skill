"""
Slot validation utilities for Alexa intent handlers.
Provides type checking and validation for all slot inputs per T046.
"""
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

# Valid meal periods (should match config/meal_periods.py)
VALID_MEAL_PERIODS = [
    "breakfast",
    "morning snack", 
    "lunch",
    "evening snack",
    "dinner"
]

# Valid day names
VALID_DAYS = [
    "monday", "tuesday", "wednesday", "thursday", 
    "friday", "saturday", "sunday",
    "today", "tomorrow"
]


class SlotValidator:
    """Validates and normalizes Alexa slot values."""
    
    @staticmethod
    def validate_meal_type(slot_value: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate meal type slot value.
        
        Args:
            slot_value: Raw slot value from Alexa
            
        Returns:
            Tuple of (is_valid, normalized_value, error_message)
        """
        if not slot_value:
            return (False, None, "I didn't catch which meal you're asking about.")
        
        # Normalize to lowercase for comparison
        normalized = slot_value.lower().strip()
        
        # Check if it's a valid meal period
        if normalized not in VALID_MEAL_PERIODS:
            # Try to find a close match
            for valid_period in VALID_MEAL_PERIODS:
                if valid_period.startswith(normalized) or normalized in valid_period:
                    logger.info(f"Matched '{slot_value}' to '{valid_period}'")
                    return (True, valid_period, None)
            
            # No match found
            valid_list = ", ".join(VALID_MEAL_PERIODS[:-1]) + f", or {VALID_MEAL_PERIODS[-1]}"
            error_msg = (
                f"I don't recognize '{slot_value}' as a meal type. "
                f"You can ask about {valid_list}."
            )
            logger.warning(f"Invalid meal type: {slot_value}")
            return (False, None, error_msg)
        
        return (True, normalized, None)
    
    @staticmethod
    def validate_day(slot_value: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate day slot value.
        
        Args:
            slot_value: Raw slot value from Alexa
            
        Returns:
            Tuple of (is_valid, normalized_value, error_message)
        """
        if not slot_value:
            return (False, None, "I didn't catch which day you're asking about.")
        
        # Normalize to lowercase for comparison
        normalized = slot_value.lower().strip()
        
        # Check if it's a valid day
        if normalized not in VALID_DAYS:
            # Try to find a close match
            for valid_day in VALID_DAYS:
                if valid_day.startswith(normalized[:3]):  # Match first 3 letters
                    logger.info(f"Matched '{slot_value}' to '{valid_day}'")
                    return (True, valid_day, None)
            
            # No match found
            error_msg = (
                f"I don't recognize '{slot_value}' as a day. "
                "You can ask about today, tomorrow, or any day of the week."
            )
            logger.warning(f"Invalid day: {slot_value}")
            return (False, None, error_msg)
        
        return (True, normalized, None)
    
    @staticmethod
    def validate_slot_exists(slots: dict, slot_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if a required slot exists and has a value.
        
        Args:
            slots: Dictionary of slots from handler_input
            slot_name: Name of the slot to check
            
        Returns:
            Tuple of (is_valid, slot_value, error_message)
        """
        slot = slots.get(slot_name)
        
        if not slot:
            error_msg = f"The {slot_name} slot is missing from the request."
            logger.error(f"Missing slot: {slot_name}")
            return (False, None, error_msg)
        
        if not slot.value:
            error_msg = f"I didn't catch the {slot_name}. Please try again."
            logger.warning(f"Empty slot value: {slot_name}")
            return (False, None, error_msg)
        
        # Type check - ensure it's a string
        if not isinstance(slot.value, str):
            error_msg = f"Invalid {slot_name} format. Please try again."
            logger.error(f"Non-string slot value: {slot_name} = {type(slot.value)}")
            return (False, None, error_msg)
        
        return (True, slot.value, None)
    
    @staticmethod
    def validate_and_get_meal_type(slots: dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Combined validation: check slot exists and is valid meal type.
        
        Args:
            slots: Dictionary of slots from handler_input
            
        Returns:
            Tuple of (is_valid, normalized_meal_type, error_message)
        """
        # First check if slot exists
        exists, raw_value, error = SlotValidator.validate_slot_exists(slots, "MealType")
        if not exists:
            return (False, None, error)
        
        # Then validate the meal type
        return SlotValidator.validate_meal_type(raw_value)
    
    @staticmethod
    def validate_and_get_day(slots: dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Combined validation: check slot exists and is valid day.
        
        Args:
            slots: Dictionary of slots from handler_input
            
        Returns:
            Tuple of (is_valid, normalized_day, error_message)
        """
        # First check if slot exists
        exists, raw_value, error = SlotValidator.validate_slot_exists(slots, "Day")
        if not exists:
            return (False, None, error)
        
        # Then validate the day
        return SlotValidator.validate_day(raw_value)
