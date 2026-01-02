"""
Intent handlers for Alexa skill.
"""
import logging
from datetime import datetime
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_core.utils import is_intent_name, is_request_type

from services.sheets_service import SheetsService
from services.meal_service import MealService
from handlers.response_builder import ResponseBuilder
from handlers.slot_validator import SlotValidator
from utils.timezone_utils import TimezoneAwareMealService

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""
    
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("LaunchRequest received")
        speak_output = ResponseBuilder.build_welcome_response()
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetMealIntentHandler(AbstractRequestHandler):
    """Handler for GetMealIntent - asks for a specific meal type."""
    
    def can_handle(self, handler_input):
        return is_intent_name("GetMealIntent")(handler_input)
    
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        
        # Validate meal type slot with type checking
        is_valid, meal_type, error_msg = SlotValidator.validate_and_get_meal_type(slots)
        if not is_valid:
            logger.warning(f"GetMealIntent validation failed: {error_msg}")
            speak_output = error_msg if error_msg else ResponseBuilder.build_error_response("invalid_meal_type")
            return handler_input.response_builder.speak(speak_output).response
        
        logger.info(f"GetMealIntent: meal_type={meal_type}")
        
        try:
            # Fetch meal plan from Google Sheets
            sheets_service = SheetsService()
            meal_plan = sheets_service.fetch_meal_plan()
            
            if not meal_plan.is_valid:
                logger.error("Meal plan is invalid or empty")
                speak_output = ResponseBuilder.build_error_response("empty_plan")
                return handler_input.response_builder.speak(speak_output).response
            
            # Get current day's meal
            meal_service = MealService(meal_plan)
            current_day = meal_service.get_current_day_name()
            meal = meal_service.get_meal_for_period(current_day, meal_type)
            
            if meal:
                # Get period for response formatting
                from config.meal_periods import get_period_by_name
                try:
                    period = get_period_by_name(meal_type)
                    speak_output = ResponseBuilder.build_meal_response(period, meal, "today")
                    logger.info(f"Returning meal: {meal.name} for {meal_type}")
                except ValueError:
                    speak_output = f"For {meal_type} today, you should make {meal.name}."
                    logger.warning(f"Unknown meal period: {meal_type}")
            else:
                speak_output = f"There is no {meal_type} planned for today."
                logger.info(f"No meal found for {meal_type} on {current_day}")
            
        except Exception as e:
            logger.error(f"Error in GetMealIntentHandler: {e}", exc_info=True)
            speak_output = ResponseBuilder.build_error_response("sheet_access")
        
        return handler_input.response_builder.speak(speak_output).response


class GetTodayMealsIntentHandler(AbstractRequestHandler):
    """Handler for GetTodayMealsIntent - asks what to cook today."""
    
    def can_handle(self, handler_input):
        return is_intent_name("GetTodayMealsIntent")(handler_input)
    
    def handle(self, handler_input):
        try:
            # Fetch meal plan
            sheets_service = SheetsService()
            meal_plan = sheets_service.fetch_meal_plan()
            
            if not meal_plan.is_valid:
                speak_output = ResponseBuilder.build_error_response("empty_plan")
                return handler_input.response_builder.speak(speak_output).response
            
            # Get remaining meals for today using device timezone (per NFR-006)
            meal_service = MealService(meal_plan)
            current_time = TimezoneAwareMealService.get_current_time_for_handler(handler_input)
            logger.info(f"Using device timezone for current time: {current_time}")
            remaining_meals = meal_service.get_remaining_today_meals(current_time)
            
            speak_output = ResponseBuilder.build_remaining_meals_response(remaining_meals)
            
        except Exception as e:
            logger.error(f"Error in GetTodayMealsIntentHandler: {e}", exc_info=True)
            speak_output = ResponseBuilder.build_error_response("sheet_access")
        
        return handler_input.response_builder.speak(speak_output).response


class GetSpecificDayMealIntentHandler(AbstractRequestHandler):
    """Handler for GetSpecificDayMealIntent - asks for meal on a specific day."""
    
    def can_handle(self, handler_input):
        return is_intent_name("GetSpecificDayMealIntent")(handler_input)
    
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        
        # Validate day and meal type slots with type checking
        day_valid, day, day_error = SlotValidator.validate_and_get_day(slots)
        if not day_valid:
            logger.warning(f"GetSpecificDayMealIntent day validation failed: {day_error}")
            speak_output = day_error if day_error else "I didn't catch which day you're asking about."
            return handler_input.response_builder.speak(speak_output).response
        
        meal_valid, meal_type, meal_error = SlotValidator.validate_and_get_meal_type(slots)
        if not meal_valid:
            logger.warning(f"GetSpecificDayMealIntent meal type validation failed: {meal_error}")
            speak_output = meal_error if meal_error else ResponseBuilder.build_error_response("invalid_meal_type")
            return handler_input.response_builder.speak(speak_output).response
        
        logger.info(f"GetSpecificDayMealIntent: day={day}, meal_type={meal_type}")
        
        try:
            # Fetch meal plan
            sheets_service = SheetsService()
            meal_plan = sheets_service.fetch_meal_plan()
            
            if not meal_plan.is_valid:
                speak_output = ResponseBuilder.build_error_response("empty_plan")
                return handler_input.response_builder.speak(speak_output).response
            
            # Get meal for specific day and period
            meal_service = MealService(meal_plan)
            meal = meal_service.get_meal_for_day_and_period(day, meal_type)
            
            # Parse day for response
            parsed_day = meal_service.parse_day_slot(day)
            
            if meal:
                from config.meal_periods import get_period_by_name
                try:
                    period = get_period_by_name(meal_type)
                    speak_output = ResponseBuilder.build_meal_response(period, meal, parsed_day)
                except ValueError:
                    speak_output = f"For {meal_type} on {parsed_day}, you should make {meal.name}."
            else:
                speak_output = f"There is no {meal_type} planned for {parsed_day}."
            
        except Exception as e:
            print(f"Error in GetSpecificDayMealIntentHandler: {e}")
            speak_output = ResponseBuilder.build_error_response("sheet_access")
        
        return handler_input.response_builder.speak(speak_output).response


class GetNextMealIntentHandler(AbstractRequestHandler):
    """Handler for GetNextMealIntent - asks for the next upcoming meal."""
    
    def can_handle(self, handler_input):
        return is_intent_name("GetNextMealIntent")(handler_input)
    
    def handle(self, handler_input):
        try:
            # Fetch meal plan
            sheets_service = SheetsService()
            meal_plan = sheets_service.fetch_meal_plan()
            
            if not meal_plan.is_valid:
                speak_output = ResponseBuilder.build_error_response("empty_plan")
                return handler_input.response_builder.speak(speak_output).response
            
            # Get next meal using device timezone (per NFR-006)
            meal_service = MealService(meal_plan)
            current_time = TimezoneAwareMealService.get_current_time_for_handler(handler_input)
            logger.info(f"Using device timezone for current time: {current_time}")
            next_meal = meal_service.get_next_meal(current_time)
            
            if next_meal:
                period, meal = next_meal
                speak_output = ResponseBuilder.build_next_meal_response(period, meal)
            else:
                speak_output = "All meals for today have passed. The next meal will be tomorrow's breakfast."
            
        except Exception as e:
            logger.error(f"Error in GetNextMealIntentHandler: {e}", exc_info=True)
            speak_output = ResponseBuilder.build_error_response("sheet_access")
        
        return handler_input.response_builder.speak(speak_output).response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for HelpIntent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        speak_output = ResponseBuilder.build_help_response()
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class RefreshMealPlanIntentHandler(AbstractRequestHandler):
    """
    Handler for RefreshMealPlanIntent - manually refresh meal plan cache.
    Per FR-017: Allows user to invalidate cache and fetch fresh data.
    """
    
    def can_handle(self, handler_input):
        return is_intent_name("RefreshMealPlanIntent")(handler_input)
    
    def handle(self, handler_input):
        logger.info("RefreshMealPlanIntent received - invalidating cache")
        
        try:
            # Import here to avoid circular dependency
            from lambda_function import invalidate_cache
            
            # Clear the cache
            invalidate_cache()
            
            # Fetch fresh data immediately
            from lambda_function import get_cached_meal_plan
            meal_plan, is_stale = get_cached_meal_plan()
            
            speak_output = "I've refreshed your meal plan. What would you like to know?"
            
        except Exception as e:
            logger.error(f"Error refreshing meal plan: {e}")
            speak_output = (
                "I had trouble refreshing your meal plan. "
                "Please check your Google Sheets connection and try again."
            )
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for CancelIntent and StopIntent."""
    
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        speak_output = ResponseBuilder.build_goodbye_response()
        
        return handler_input.response_builder.speak(speak_output).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for SessionEndedRequest."""
    
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        # Log session end for debugging
        print(f"Session ended: {handler_input.request_envelope.request.reason}")
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for FallbackIntent when user says something unexpected."""
    
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        speak_output = (
            "I'm not sure I understand. "
            "You can ask me about meals for the week, like 'what's for dinner today' "
            "or 'what should I cook on Friday'. What would you like to know?"
        )
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handler for all exceptions."""
    
    def can_handle(self, handler_input, exception):
        """Handle all exceptions."""
        return True
    
    def handle(self, handler_input, exception):
        """Handle the exception and return error response."""
        logger.error(f"Encountered exception: {exception}", exc_info=True)
        speak_output = ResponseBuilder.build_error_response()
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
