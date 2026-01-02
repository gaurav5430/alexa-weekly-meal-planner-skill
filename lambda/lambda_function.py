"""
AWS Lambda handler for Alexa skill.
"""
from datetime import datetime, timedelta
from ask_sdk_core.skill_builder import SkillBuilder
from handlers.intent_handlers import (
    LaunchRequestHandler,
    GetMealIntentHandler,
    GetTodayMealsIntentHandler,
    GetSpecificDayMealIntentHandler,
    GetNextMealIntentHandler,
    HelpIntentHandler,
    RefreshMealPlanIntentHandler,
    CancelOrStopIntentHandler,
    SessionEndedRequestHandler,
    FallbackIntentHandler,
    CatchAllExceptionHandler
)
from services.sheets_service import SheetsService

# Global cache for meal plan (persists across Lambda invocations)
_cached_meal_plan = None
_cache_timestamp = None
CACHE_DURATION_HOURS = 24  # 24-hour cache per FR-016


def get_cached_meal_plan():
    """
    Get meal plan from cache or fetch fresh data.
    
    Returns:
        Tuple of (MealPlan, is_stale)
    """
    global _cached_meal_plan, _cache_timestamp
    
    now = datetime.now()
    is_stale = False
    
    # Check if cache exists and is fresh
    if _cached_meal_plan and _cache_timestamp:
        age_hours = (now - _cache_timestamp).total_seconds() / 3600
        if age_hours < CACHE_DURATION_HOURS:
            # Cache is fresh
            return (_cached_meal_plan, False)
        else:
            # Cache exists but is stale
            is_stale = True
    
    # Fetch fresh data
    try:
        sheets_service = SheetsService()
        _cached_meal_plan = sheets_service.fetch_meal_plan()
        _cache_timestamp = now
        return (_cached_meal_plan, is_stale)
    except Exception as e:
        print(f"Error fetching meal plan: {e}")
        # If fetch fails but we have stale cache, use it
        if _cached_meal_plan:
            print("Using stale cache due to fetch error")
            return (_cached_meal_plan, True)
        raise


def invalidate_cache():
    """
    Manually invalidate the cache to force fresh data fetch on next request.
    Used by RefreshMealPlanIntent handler per FR-017.
    """
    global _cached_meal_plan, _cache_timestamp
    _cached_meal_plan = None
    _cache_timestamp = None
    print("Cache invalidated - next request will fetch fresh data")


# Initialize skill builder
sb = SkillBuilder()

# Register request handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetMealIntentHandler())
sb.add_request_handler(GetTodayMealsIntentHandler())
sb.add_request_handler(GetSpecificDayMealIntentHandler())
sb.add_request_handler(GetNextMealIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(RefreshMealPlanIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())

# Register exception handler
sb.add_exception_handler(CatchAllExceptionHandler())

# Lambda handler
lambda_handler = sb.lambda_handler()
