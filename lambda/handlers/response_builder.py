"""
Response builder for constructing Alexa responses with SSML enhancements.
Enhanced per T052 to use SSML for natural speech flow, pauses, and emphasis.
"""
from typing import List, Optional
from models.meal_plan import Meal
from models.time_period import TimePeriod


class ResponseBuilder:
    """Builds formatted responses for Alexa with SSML support."""
    
    @staticmethod
    def build_meal_response(period: TimePeriod, meal: Meal, day: str = "today") -> str:
        """
        Build response for a single meal query with SSML.
        
        Args:
            period: TimePeriod for the meal
            meal: Meal object
            day: Day name (default "today")
        
        Returns:
            Formatted speech response with SSML
        """
        if meal.is_empty:
            period_phrase = period.name.replace('_', ' ')
            return (
                f"<speak>"
                f"There is <emphasis level='moderate'>no</emphasis> {period_phrase} "
                f"planned for {day}."
                f"</speak>"
            )
        
        day_phrase = day if day.lower() != "today" else "today"
        period_phrase = period.name.replace('_', ' ')
        
        return (
            f"<speak>"
            f"For {period_phrase} {day_phrase}, <break time='300ms'/> "
            f"you should make <emphasis level='strong'>{meal.name}</emphasis>."
            f"</speak>"
        )
    
    @staticmethod
    def build_multiple_meals_response(meals_with_periods: List[tuple], day: str = "today") -> str:
        """
        Build response for multiple meals with SSML pauses between items.
        
        Args:
            meals_with_periods: List of (TimePeriod, Meal) tuples
            day: Day name (default "today")
        
        Returns:
            Formatted speech response with SSML
        """
        if not meals_with_periods:
            return f"<speak>There are no meals planned for {day}.</speak>"
        
        # Filter out empty meals
        non_empty_meals = [(p, m) for p, m in meals_with_periods if not m.is_empty]
        
        if not non_empty_meals:
            return f"<speak>There are no meals planned for {day}.</speak>"
        
        if len(non_empty_meals) == 1:
            period, meal = non_empty_meals[0]
            return ResponseBuilder.build_meal_response(period, meal, day)
        
        # Build list of meals with SSML pauses
        day_phrase = day if day.lower() != "today" else "today"
        speech_parts = [f"<speak>For {day_phrase}, you should make: <break time='400ms'/>"]
        
        for i, (period, meal) in enumerate(non_empty_meals):
            period_phrase = period.name.replace('_', ' ')
            
            if i == len(non_empty_meals) - 1:
                # Last item
                speech_parts.append(f"<break time='300ms'/> and for {period_phrase}, "
                                   f"<emphasis level='moderate'>{meal.name}</emphasis>")
            elif i == 0:
                # First item
                speech_parts.append(f"for {period_phrase}, "
                                   f"<emphasis level='moderate'>{meal.name}</emphasis>")
            else:
                # Middle items
                speech_parts.append(f"<break time='300ms'/> for {period_phrase}, "
                                   f"<emphasis level='moderate'>{meal.name}</emphasis>")
        
        speech_parts.append(".</speak>")
        return "".join(speech_parts)
    
    @staticmethod
    def build_remaining_meals_response(meals_with_periods: List[tuple]) -> str:
        """
        Build response for remaining meals today with SSML.
        
        Args:
            meals_with_periods: List of (TimePeriod, Meal) tuples
        
        Returns:
            Formatted speech response with SSML
        """
        if not meals_with_periods:
            return (
                "<speak>"
                "<prosody rate='medium'>You're done cooking for today!</prosody> "
                "<break time='400ms'/> "
                "All meals have passed."
                "</speak>"
            )
        
        return ResponseBuilder.build_multiple_meals_response(meals_with_periods, "today")
    
    @staticmethod
    def build_next_meal_response(period: TimePeriod, meal: Meal) -> str:
        """
        Build response for next upcoming meal with SSML emphasis.
        
        Args:
            period: TimePeriod for the meal
            meal: Meal object
        
        Returns:
            Formatted speech response with SSML
        """
        period_phrase = period.name.replace('_', ' ')
        
        if meal.is_empty:
            return (
                f"<speak>"
                f"The next meal time is <emphasis level='moderate'>{period_phrase}</emphasis>, "
                f"<break time='300ms'/> but nothing is planned."
                f"</speak>"
            )
        
        return (
            f"<speak>"
            f"The next meal is <emphasis level='moderate'>{period_phrase}</emphasis>, "
            f"<break time='300ms'/> "
            f"and you should make <emphasis level='strong'>{meal.name}</emphasis>."
            f"</speak>"
        )
    
    @staticmethod
    def build_error_response(error_type: str = "generic") -> str:
        """
        Build error response messages with SSML.
        
        Args:
            error_type: Type of error (generic, sheet_access, empty_plan)
        
        Returns:
            Formatted error message with SSML
        """
        if error_type == "sheet_access":
            return (
                "<speak>"
                "<say-as interpret-as='interjection'>Oh no</say-as>. "
                "<break time='300ms'/> "
                "I'm having trouble accessing the meal plan right now. "
                "Please try again later."
                "</speak>"
            )
        elif error_type == "empty_plan":
            return (
                "<speak>"
                "The meal plan appears to be empty. "
                "<break time='300ms'/> "
                "Please check your Google Sheet."
                "</speak>"
            )
        elif error_type == "invalid_meal_type":
            return (
                "<speak>"
                "I didn't understand which meal you're asking about. "
                "<break time='300ms'/> "
                "Please try again."
                "</speak>"
            )
        else:
            return (
                "<speak>"
                "<say-as interpret-as='interjection'>Uh oh</say-as>. "
                "Something went wrong. Please try again."
                "</speak>"
            )
    
    @staticmethod
    def build_help_response() -> str:
        """
        Build help response explaining skill capabilities with SSML.
        
        Returns:
            Help message with SSML
        """
        return (
            "<speak>"
            "You can ask me about your weekly meal plan. "
            "<break time='400ms'/> "
            "Try saying: <break time='200ms'/> "
            "<emphasis level='moderate'>what's for dinner today</emphasis>, "
            "<break time='200ms'/> "
            "<emphasis level='moderate'>what's for lunch on Friday</emphasis>, "
            "<break time='200ms'/> "
            "<emphasis level='moderate'>what should I cook today</emphasis>, "
            "<break time='200ms'/> "
            "or <emphasis level='moderate'>what's the next meal</emphasis>?"
            "</speak>"
        )
    
    @staticmethod
    def build_welcome_response() -> str:
        """
        Build welcome response for skill launch with SSML.
        
        Returns:
            Welcome message with SSML
        """
        return (
            "<speak>"
            "<prosody rate='medium'>Welcome to Weekly Meal Planner!</prosody> "
            "<break time='400ms'/> "
            "You can ask me about any meal for the week. "
            "<break time='300ms'/> "
            "What would you like to know?"
            "</speak>"
        )
    
    @staticmethod
    def build_goodbye_response() -> str:
        """
        Build goodbye response with SSML.
        
        Returns:
            Goodbye message with SSML
        """
        return (
            "<speak>"
            "<prosody rate='medium'>Happy cooking!</prosody> "
            "<break time='300ms'/> "
            "Goodbye."
            "</speak>"
        )
