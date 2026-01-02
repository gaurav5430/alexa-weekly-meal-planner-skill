"""
Unit tests for data models.
"""
import pytest
from datetime import time
import sys
from pathlib import Path

# Add lambda folder to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'lambda'))

from models.time_period import TimePeriod
from models.meal_plan import Meal, MealPlan, MealQuery, QueryType


class TestTimePeriodModel:
    """Test TimePeriod data class."""
    
    def test_initialization(self):
        """Test that TimePeriod initializes correctly."""
        period = TimePeriod("breakfast", time(8, 0), time(11, 0), "Breakfast")
        assert period.name == "breakfast"
        assert period.start_time == time(8, 0)
        assert period.end_time == time(11, 0)
    
    def test_string_representation(self):
        """Test string representation."""
        period = TimePeriod("lunch", time(12, 0), time(15, 0), "Lunch")
        assert "lunch" in str(period)


class TestMealModel:
    """Test Meal data class."""
    
    def test_initialization_with_name(self):
        """Test that Meal initializes correctly with a name."""
        meal = Meal("Monday", "breakfast", "Oatmeal")
        assert meal.day_of_week == "Monday"
        assert meal.meal_period == "breakfast"
        assert meal.name == "Oatmeal"
        assert meal.is_empty is False
    
    def test_initialization_with_empty_name(self):
        """Test that empty meal is detected."""
        meal = Meal("Monday", "lunch", "")
        assert meal.day_of_week == "Monday"
        assert meal.meal_period == "lunch"
        assert meal.name == ""
        assert meal.is_empty is True
    
    def test_initialization_with_whitespace_name(self):
        """Test that whitespace-only name is considered empty."""
        meal = Meal("Monday", "dinner", "   ")
        assert meal.is_empty is True
    
    def test_initialization_with_none_name(self):
        """Test that empty string is handled correctly."""
        meal = Meal("Monday", "snack", "")
        assert meal.name == ""
        assert meal.is_empty is True


class TestMealPlanModel:
    """Test MealPlan data class."""
    
    def test_initialization(self):
        """Test that MealPlan initializes correctly."""
        meals = {
            "Monday": {
                "breakfast": Meal("Monday", "breakfast", "Oatmeal"),
                "lunch": Meal("Monday", "lunch", "Salad")
            }
        }
        plan = MealPlan(meals, is_valid=True)
        assert plan.meals == meals
        assert plan.is_valid is True
    
    def test_get_meal_existing(self):
        """Test that get_meal returns correct meal."""
        meals = {
            "Monday": {
                "breakfast": Meal("Monday", "breakfast", "Pancakes")
            }
        }
        plan = MealPlan(meals, is_valid=True)
        
        meal = plan.get_meal("Monday", "breakfast")
        assert meal is not None
        assert meal.name == "Pancakes"
    
    def test_get_meal_missing_day(self):
        """Test that get_meal returns None for missing day."""
        meals = {
            "Monday": {
                "breakfast": Meal("Monday", "breakfast", "Pancakes")
            }
        }
        plan = MealPlan(meals, is_valid=True)
        
        meal = plan.get_meal("Tuesday", "breakfast")
        assert meal is None
    
    def test_get_meal_missing_period(self):
        """Test that get_meal returns None for missing period."""
        meals = {
            "Monday": {
                "breakfast": Meal("Monday", "breakfast", "Pancakes")
            }
        }
        plan = MealPlan(meals, is_valid=True)
        
        meal = plan.get_meal("Monday", "dinner")
        assert meal is None
    
    def test_get_day_meals(self):
        """Test that get_day_meals returns all meals for a day."""
        meals = {
            "Monday": {
                "breakfast": Meal("Monday", "breakfast", "Pancakes"),
                "lunch": Meal("Monday", "lunch", "Salad"),
                "dinner": Meal("Monday", "dinner", "Pasta")
            }
        }
        plan = MealPlan(meals, is_valid=True)
        
        day_meals = plan.get_day_meals("Monday")
        assert len(day_meals) == 3
        assert "breakfast" in day_meals
        assert "lunch" in day_meals
        assert "dinner" in day_meals
    
    def test_get_day_meals_missing_day(self):
        """Test that get_day_meals returns empty dict for missing day."""
        meals = {"Monday": {}}
        plan = MealPlan(meals, is_valid=True)
        
        day_meals = plan.get_day_meals("Tuesday")
        assert day_meals == {}


class TestQueryTypeEnum:
    """Test QueryType enum."""
    
    def test_enum_values(self):
        """Test that all expected enum values exist."""
        assert QueryType.SPECIFIC_MEAL is not None
        assert QueryType.TODAY_MEALS is not None
        assert QueryType.NEXT_MEAL is not None
        assert QueryType.SPECIFIC_DAY_MEAL is not None
    
    def test_enum_comparison(self):
        """Test that enum values can be compared."""
        assert QueryType.SPECIFIC_MEAL == QueryType.SPECIFIC_MEAL
        assert QueryType.SPECIFIC_MEAL != QueryType.TODAY_MEALS


class TestMealQueryModel:
    """Test MealQuery data class."""
    
    def test_initialization_specific_meal(self):
        """Test initialization for specific meal query."""
        from datetime import datetime
        query = MealQuery(
            query_type=QueryType.SPECIFIC_MEAL,
            query_time=datetime.now(),
            target_period="breakfast"
        )
        assert query.query_type == QueryType.SPECIFIC_MEAL
        assert query.target_period == "breakfast"
        assert query.target_day is None
    
    def test_initialization_specific_day_meal(self):
        """Test initialization for specific day and meal query."""
        from datetime import datetime
        query = MealQuery(
            query_type=QueryType.SPECIFIC_DAY_MEAL,
            query_time=datetime.now(),
            target_period="lunch",
            target_day="Friday"
        )
        assert query.query_type == QueryType.SPECIFIC_DAY_MEAL
        assert query.target_period == "lunch"
        assert query.target_day == "Friday"
    
    def test_initialization_today_remaining(self):
        """Test initialization for today's remaining meals query."""
        from datetime import datetime
        query = MealQuery(
            query_type=QueryType.TODAY_MEALS,
            query_time=datetime.now()
        )
        assert query.query_type == QueryType.TODAY_MEALS
        assert query.target_period is None
        assert query.target_day is None
    
    def test_initialization_next_meal(self):
        """Test initialization for next meal query."""
        from datetime import datetime
        query = MealQuery(
            query_type=QueryType.NEXT_MEAL,
            query_time=datetime.now()
        )
        assert query.query_type == QueryType.NEXT_MEAL
        assert query.target_period is None
        assert query.target_day is None


class TestMealValidation:
    """Test meal validation logic."""
    
    def test_meal_with_valid_name(self):
        """Test that meal with valid name is not empty."""
        meal = Meal("Monday", "breakfast", "Eggs and Toast")
        assert not meal.is_empty
    
    def test_meal_with_special_characters(self):
        """Test that meal names with special characters work."""
        meal = Meal("Monday", "lunch", "Mom's Famous Lasagna")
        assert not meal.is_empty
        assert meal.name == "Mom's Famous Lasagna"
    
    def test_meal_with_numbers(self):
        """Test that meal names with numbers work."""
        meal = Meal("Monday", "dinner", "3-Bean Chili")
        assert not meal.is_empty
        assert meal.name == "3-Bean Chili"


class TestMealPlanValidation:
    """Test MealPlan validation."""
    
    def test_invalid_meal_plan(self):
        """Test that invalid meal plan is marked correctly."""
        plan = MealPlan({}, is_valid=False)
        assert plan.is_valid is False
        assert plan.meals == {}
    
    def test_valid_meal_plan_with_empty_meals(self):
        """Test that valid plan can contain empty meals."""
        meals = {
            "Monday": {
                "breakfast": Meal("Monday", "breakfast", ""),
                "lunch": Meal("Monday", "lunch", "Sandwich")
            }
        }
        plan = MealPlan(meals, is_valid=True)
        assert plan.is_valid is True
        
        # Verify empty meal is properly marked
        breakfast = plan.get_meal("Monday", "breakfast")
        assert breakfast.is_empty is True
        
        # Verify non-empty meal works
        lunch = plan.get_meal("Monday", "lunch")
        assert lunch.is_empty is False
