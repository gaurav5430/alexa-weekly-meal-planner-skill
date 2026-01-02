"""
Time period definitions and utilities for meal planning.
"""
from dataclasses import dataclass
from datetime import time
from typing import List, Optional


@dataclass
class TimePeriod:
    """Represents a time period for a meal type."""
    name: str
    start_time: time
    end_time: time
    display_name: str
    
    def contains(self, current_time: time) -> bool:
        """Check if a given time falls within this period."""
        return self.start_time <= current_time < self.end_time
    
    def __repr__(self) -> str:
        return f"TimePeriod({self.name}, {self.start_time}-{self.end_time})"


def get_current_meal_period(current_time: time, periods: List[TimePeriod]) -> Optional[TimePeriod]:
    """
    Determine which meal period the current time falls into.
    
    Args:
        current_time: Current time to check
        periods: List of TimePeriod instances to check against
    
    Returns:
        TimePeriod if time falls within a period, None if between periods
    """
    for period in periods:
        if period.contains(current_time):
            return period
    return None


def get_remaining_meals(current_time: time, periods: List[TimePeriod]) -> List[TimePeriod]:
    """
    Get list of meal periods that haven't started yet.
    
    Args:
        current_time: Current time to check
        periods: List of TimePeriod instances
    
    Returns:
        List of TimePeriod instances that start after current_time
    """
    current_minutes = current_time.hour * 60 + current_time.minute
    remaining = []
    
    for period in periods:
        period_start_minutes = period.start_time.hour * 60 + period.start_time.minute
        if period_start_minutes >= current_minutes:
            remaining.append(period)
    
    return remaining


def get_next_meal_period(current_time: time, periods: List[TimePeriod]) -> Optional[TimePeriod]:
    """
    Get the next upcoming meal period after current time.
    
    Args:
        current_time: Current time to check
        periods: List of TimePeriod instances
    
    Returns:
        Next TimePeriod or None if all meals have passed
    """
    remaining = get_remaining_meals(current_time, periods)
    return remaining[0] if remaining else None
