"""
Meal plan data models.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class QueryType(Enum):
    """Types of meal queries supported."""
    NEXT_MEAL = "next_meal"
    SPECIFIC_MEAL = "specific_meal"
    SPECIFIC_DAY_MEAL = "specific_day_meal"
    TODAY_MEALS = "today_meals"


@dataclass
class Meal:
    """Represents a single meal entry."""
    day_of_week: str
    meal_period: str
    name: str
    is_empty: bool = False
    
    def __post_init__(self):
        """Validate and normalize data."""
        if not self.name or self.name.strip() == "":
            self.is_empty = True
            self.name = ""
    
    def __repr__(self) -> str:
        return f"Meal({self.day_of_week} {self.meal_period}: {self.name or 'EMPTY'})"


@dataclass
class MealPlan:
    """Weekly meal plan containing all meals."""
    meals: Dict[str, Dict[str, Meal]] = field(default_factory=dict)
    last_updated: Optional[datetime] = None
    sheet_id: str = ""
    is_valid: bool = False
    
    def get_meal(self, day: str, period: str) -> Optional[Meal]:
        """
        Get a specific meal by day and period.
        
        Args:
            day: Day of week (e.g., "Monday")
            period: Meal period (e.g., "breakfast")
        
        Returns:
            Meal object or None if not found
        """
        if day in self.meals and period in self.meals[day]:
            return self.meals[day][period]
        return None
    
    def get_day_meals(self, day: str) -> Dict[str, Meal]:
        """
        Get all meals for a specific day.
        
        Args:
            day: Day of week
        
        Returns:
            Dictionary of {period: Meal} for the day
        """
        return self.meals.get(day, {})
    
    def __repr__(self) -> str:
        day_count = len(self.meals)
        return f"MealPlan({day_count} days, valid={self.is_valid})"


@dataclass
class MealQuery:
    """Represents a user's meal query."""
    query_type: QueryType
    query_time: datetime
    target_day: Optional[str] = None
    target_period: Optional[str] = None
    timezone: str = "UTC"
    
    def __repr__(self) -> str:
        return f"MealQuery({self.query_type.value}, {self.target_day or 'today'} {self.target_period or 'any'})"
