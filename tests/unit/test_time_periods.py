"""
Unit tests for time period utilities.
"""
import pytest
from datetime import time
import sys
from pathlib import Path

# Add lambda folder to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'lambda'))

from models.time_period import TimePeriod, get_current_meal_period, get_remaining_meals, get_next_meal_period


class TestTimePeriod:
    """Test TimePeriod class."""
    
    def test_contains_time_within_period(self):
        """Test that contains() returns True for time within period."""
        period = TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast")
        assert period.contains(time(9, 30)) is True
        assert period.contains(time(8, 0)) is True
        assert period.contains(time(10, 59)) is True
    
    def test_contains_time_outside_period(self):
        """Test that contains() returns False for time outside period."""
        period = TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast")
        assert period.contains(time(7, 59)) is False
        assert period.contains(time(11, 0)) is False
        assert period.contains(time(12, 0)) is False
    
    def test_contains_boundary_conditions(self):
        """Test boundary conditions for contains()."""
        period = TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch")
        assert period.contains(time(12, 0)) is True  # Start inclusive
        assert period.contains(time(15, 0)) is False  # End exclusive


class TestGetCurrentMealPeriod:
    """Test get_current_meal_period function."""
    
    def test_finds_correct_period(self):
        """Test that correct period is returned for a given time."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast"),
            TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch"),
            TimePeriod("dinner", time(19, 0), time(22, 0), "Dinner")
        ]
        
        # Morning time should return breakfast
        result = get_current_meal_period(time(9, 30), periods)
        assert result is not None
        assert result.name == "breakfast"
        
        # Afternoon time should return lunch
        result = get_current_meal_period(time(13, 0), periods)
        assert result is not None
        assert result.name == "lunch"
        
        # Evening time should return dinner
        result = get_current_meal_period(time(20, 0), periods)
        assert result is not None
        assert result.name == "dinner"
    
    def test_returns_none_between_periods(self):
        """Test that None is returned when time is between periods."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast"),
            TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch")
        ]
        
        # Time between breakfast and lunch
        result = get_current_meal_period(time(11, 30), periods)
        assert result is None
    
    def test_returns_none_before_all_periods(self):
        """Test that None is returned when time is before all periods."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast")
        ]
        
        result = get_current_meal_period(time(7, 0), periods)
        assert result is None
    
    def test_returns_none_after_all_periods(self):
        """Test that None is returned when time is after all periods."""
        periods = [
            TimePeriod("dinner", time(19, 0), time(22, 0), "Dinner")
        ]
        
        result = get_current_meal_period(time(23, 0), periods)
        assert result is None


class TestGetRemainingMeals:
    """Test get_remaining_meals function."""
    
    def test_returns_all_future_periods(self):
        """Test that all periods after current time are returned."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast"),
            TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch"),
            TimePeriod("dinner", time(19, 0), time(22, 0), "Dinner")
        ]
        
        # At 10am, should return lunch and dinner
        result = get_remaining_meals(time(10, 0), periods)
        assert len(result) == 2
        assert result[0].name == "lunch"
        assert result[1].name == "dinner"
    
    def test_returns_empty_after_all_periods(self):
        """Test that empty list is returned when all periods have passed."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast"),
            TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch")
        ]
        
        result = get_remaining_meals(time(16, 0), periods)
        assert len(result) == 0
    
    def test_includes_current_period(self):
        """Test that current period is NOT included - only future periods."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast"),
            TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch")
        ]
        
        # At 9am (during breakfast), remaining should only include future meals (lunch)
        result = get_remaining_meals(time(9, 0), periods)
        assert len(result) == 1
        assert result[0].name == "lunch"


class TestGetNextMealPeriod:
    """Test get_next_meal_period function."""
    
    def test_returns_next_upcoming_period(self):
        """Test that next period is returned correctly."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast"),
            TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch"),
            TimePeriod("dinner", time(19, 0), time(22, 0), "Dinner")
        ]
        
        # At 10am (during breakfast), next should be lunch
        result = get_next_meal_period(time(10, 0), periods)
        assert result is not None
        assert result.name == "lunch"
        
        # At 11:30am (between meals), next should be lunch
        result = get_next_meal_period(time(11, 30), periods)
        assert result is not None
        assert result.name == "lunch"
    
    def test_returns_none_after_all_periods(self):
        """Test that None is returned when all periods have passed."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast"),
            TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch")
        ]
        
        result = get_next_meal_period(time(16, 0), periods)
        assert result is None
    
    def test_returns_first_period_before_start(self):
        """Test that first period is returned when time is before all periods."""
        periods = [
            TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast"),
            TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch")
        ]
        
        result = get_next_meal_period(time(7, 0), periods)
        assert result is not None
        assert result.name == "breakfast"
