"""
Meal period configuration defining when each meal is served.
"""
from datetime import time
from models.time_period import TimePeriod


# Define all 5 meal periods with their time ranges
MEAL_PERIODS = [
    TimePeriod(
        name="breakfast",
        start_time=time(8, 0),
        end_time=time(11, 0),
        display_name="Breakfast"
    ),
    TimePeriod(
        name="morning_snack",
        start_time=time(11, 0),
        end_time=time(12, 0),
        display_name="Morning Snack"
    ),
    TimePeriod(
        name="lunch",
        start_time=time(12, 0),
        end_time=time(15, 0),
        display_name="Lunch"
    ),
    TimePeriod(
        name="evening_snack",
        start_time=time(16, 0),
        end_time=time(18, 0),
        display_name="Evening Snack"
    ),
    TimePeriod(
        name="dinner",
        start_time=time(19, 0),
        end_time=time(22, 0),
        display_name="Dinner"
    ),
]


# Mapping from various user inputs to canonical meal period names
MEAL_PERIOD_SYNONYMS = {
    "breakfast": "breakfast",
    "morning meal": "breakfast",
    "first meal": "breakfast",
    
    "morning snack": "morning_snack",
    "morning time snack": "morning_snack",
    "mid morning snack": "morning_snack",
    "snack before lunch": "morning_snack",
    "first snack": "morning_snack",
    
    "lunch": "lunch",
    "noon meal": "lunch",
    "midday meal": "lunch",
    "afternoon meal": "lunch",
    
    "evening snack": "evening_snack",
    "afternoon snack": "evening_snack",
    "snack before dinner": "evening_snack",
    "evening time snack": "evening_snack",
    "second snack": "evening_snack",
    
    "dinner": "dinner",
    "supper": "dinner",
    "evening meal": "dinner",
    "night meal": "dinner",
    "last meal": "dinner",
}


def get_period_by_name(period_name: str) -> TimePeriod:
    """
    Get TimePeriod by name, handling synonyms.
    
    Args:
        period_name: Name or synonym of meal period
    
    Returns:
        TimePeriod object
    
    Raises:
        ValueError: If period name is not recognized
    """
    # Normalize input
    normalized = period_name.lower().strip()
    
    # Check synonyms first
    canonical_name = MEAL_PERIOD_SYNONYMS.get(normalized)
    if canonical_name:
        # Find the period with this canonical name
        for period in MEAL_PERIODS:
            if period.name == canonical_name:
                return period
    
    # Try direct name match
    for period in MEAL_PERIODS:
        if period.name == normalized:
            return period
    
    raise ValueError(f"Unknown meal period: {period_name}")
