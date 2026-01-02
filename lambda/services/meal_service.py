"""
Meal service for looking up and filtering meals from the meal plan.
"""
from datetime import datetime
from typing import Optional, List, Dict
from models.meal_plan import Meal, MealPlan
from models.time_period import TimePeriod, get_current_meal_period, get_remaining_meals, get_next_meal_period
from config.meal_periods import MEAL_PERIODS, get_period_by_name


class MealService:
    """Service for meal lookup and query handling."""
    
    def __init__(self, meal_plan: MealPlan):
        """
        Initialize meal service with a meal plan.
        
        Args:
            meal_plan: MealPlan object containing all meals
        """
        self.meal_plan = meal_plan
    
    def get_meal_for_period(self, day: str, period_name: str) -> Optional[Meal]:
        """
        Look up a meal by day and period.
        
        Args:
            day: Day of week (e.g., "Monday")
            period_name: Meal period name (e.g., "breakfast", "dinner")
        
        Returns:
            Meal object or None if not found
        """
        # Normalize day name
        day_normalized = day.strip().capitalize()
        
        # Handle period synonyms
        try:
            period = get_period_by_name(period_name)
            period_key = period.name
        except ValueError:
            # If period name is invalid, try direct lookup
            period_key = period_name.lower().strip()
        
        return self.meal_plan.get_meal(day_normalized, period_key)
    
    def get_current_day_name(self) -> str:
        """
        Get current day of week.
        
        Returns:
            Day name (e.g., "Monday")
        """
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[datetime.now().weekday()]
    
    def get_today_meals(self, current_time: datetime) -> List[tuple]:
        """
        Get all meals for today with their periods.
        
        Args:
            current_time: Current datetime
        
        Returns:
            List of (TimePeriod, Meal) tuples for all meals today
        """
        day = self.get_current_day_name()
        day_meals = self.meal_plan.get_day_meals(day)
        
        result = []
        for period in MEAL_PERIODS:
            if period.name in day_meals:
                meal = day_meals[period.name]
                result.append((period, meal))
        
        return result
    
    def get_remaining_today_meals(self, current_time: datetime) -> List[tuple]:
        """
        Get remaining meals for today based on current time.
        
        Args:
            current_time: Current datetime
        
        Returns:
            List of (TimePeriod, Meal) tuples for remaining meals
        """
        remaining_periods = get_remaining_meals(current_time.time(), MEAL_PERIODS)
        day = self.get_current_day_name()
        day_meals = self.meal_plan.get_day_meals(day)
        
        result = []
        for period in remaining_periods:
            if period.name in day_meals:
                meal = day_meals[period.name]
                result.append((period, meal))
        
        return result
    
    def get_next_meal(self, current_time: datetime) -> Optional[tuple]:
        """
        Get the next upcoming meal.
        
        Args:
            current_time: Current datetime
        
        Returns:
            Tuple of (TimePeriod, Meal) for next meal, or None if all meals passed
        """
        next_period = get_next_meal_period(current_time.time(), MEAL_PERIODS)
        if not next_period:
            return None
        
        day = self.get_current_day_name()
        meal = self.meal_plan.get_meal(day, next_period.name)
        
        if meal:
            return (next_period, meal)
        return None
    
    def parse_day_slot(self, day_value: str) -> str:
        """
        Parse day slot value handling relative days (today, tomorrow).
        
        Args:
            day_value: Day from Alexa slot (e.g., "Friday", "today", "tomorrow")
        
        Returns:
            Normalized day name (e.g., "Monday")
        """
        day_lower = day_value.lower().strip()
        
        if day_lower == "today":
            return self.get_current_day_name()
        elif day_lower == "tomorrow":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            today_index = datetime.now().weekday()
            tomorrow_index = (today_index + 1) % 7
            return days[tomorrow_index]
        else:
            # Regular day name
            return day_value.strip().capitalize()
    
    def get_meal_for_day_and_period(self, day_value: str, period_name: str) -> Optional[Meal]:
        """
        Get meal for a specific day and period, handling relative days.
        
        Args:
            day_value: Day from Alexa slot (can be relative like "tomorrow")
            period_name: Meal period name
        
        Returns:
            Meal object or None if not found
        """
        day = self.parse_day_slot(day_value)
        return self.get_meal_for_period(day, period_name)
