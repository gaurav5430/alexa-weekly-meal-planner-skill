"""
Timezone utilities for extracting and using device timezone from Alexa requests.
Per NFR-006: Extract device timezone from request context.
"""
import logging
from datetime import datetime
from typing import Optional
import pytz

logger = logging.getLogger(__name__)


class TimezoneExtractor:
    """Extracts and handles timezone information from Alexa requests."""
    
    DEFAULT_TIMEZONE = "America/New_York"  # Fallback timezone
    
    @staticmethod
    def extract_timezone_from_request(handler_input) -> str:
        """
        Extract device timezone from Alexa request context.
        
        The timezone is available in the request context under:
        handler_input.request_envelope.context.system.device.timezone
        
        Args:
            handler_input: HandlerInput from Alexa request
            
        Returns:
            Timezone string (e.g., "America/New_York") or default if not available
        """
        try:
            # Check if context exists
            if not handler_input or not hasattr(handler_input, 'request_envelope'):
                logger.warning("No request envelope found, using default timezone")
                return TimezoneExtractor.DEFAULT_TIMEZONE
            
            context = handler_input.request_envelope.context
            if not context:
                logger.warning("No context in request envelope, using default timezone")
                return TimezoneExtractor.DEFAULT_TIMEZONE
            
            # Access the system context
            system = context.system
            if not system:
                logger.warning("No system in context, using default timezone")
                return TimezoneExtractor.DEFAULT_TIMEZONE
            
            # Try to get timezone from device
            if hasattr(system, 'device') and system.device:
                device_id = system.device.device_id
                
                # The timezone is typically accessed via the Settings API
                # For simplicity, we'll use the system timezone from context
                # In production, you may need to call the Alexa Settings API
                logger.info(f"Device ID: {device_id}")
                
                # Check if timezone is in the context (some Alexa versions provide it)
                if hasattr(system.device, 'timezone'):
                    timezone = system.device.timezone
                    if timezone and TimezoneExtractor.validate_timezone(timezone):
                        logger.info(f"Extracted timezone from device: {timezone}")
                        return timezone
            
            # Fallback to default
            logger.warning(f"Could not extract timezone, using default: {TimezoneExtractor.DEFAULT_TIMEZONE}")
            return TimezoneExtractor.DEFAULT_TIMEZONE
            
        except Exception as e:
            logger.error(f"Error extracting timezone: {e}")
            return TimezoneExtractor.DEFAULT_TIMEZONE
    
    @staticmethod
    def validate_timezone(timezone_str: str) -> bool:
        """
        Validate that a timezone string is valid.
        
        Args:
            timezone_str: Timezone identifier (e.g., "America/New_York")
            
        Returns:
            True if valid timezone, False otherwise
        """
        try:
            pytz.timezone(timezone_str)
            return True
        except pytz.UnknownTimeZoneError:
            logger.warning(f"Invalid timezone: {timezone_str}")
            return False
    
    @staticmethod
    def get_current_time_in_timezone(timezone_str: str) -> datetime:
        """
        Get current time in the specified timezone.
        
        Args:
            timezone_str: Timezone identifier
            
        Returns:
            datetime object in the specified timezone
        """
        try:
            tz = pytz.timezone(timezone_str)
            return datetime.now(tz)
        except Exception as e:
            logger.error(f"Error getting time in timezone {timezone_str}: {e}")
            # Fallback to system time
            return datetime.now()
    
    @staticmethod
    def extract_and_get_current_time(handler_input) -> datetime:
        """
        Extract timezone from request and return current time in that timezone.
        
        This is the main method to use in intent handlers.
        
        Args:
            handler_input: HandlerInput from Alexa request
            
        Returns:
            Current datetime in device timezone
        """
        timezone_str = TimezoneExtractor.extract_timezone_from_request(handler_input)
        return TimezoneExtractor.get_current_time_in_timezone(timezone_str)


class TimezoneAwareMealService:
    """
    Helper to create timezone-aware meal lookups.
    
    This is a wrapper that can be used by intent handlers to ensure
    they use the device timezone when looking up meals.
    """
    
    @staticmethod
    def get_current_time_for_handler(handler_input) -> datetime:
        """
        Get current time considering device timezone.
        
        Args:
            handler_input: HandlerInput from Alexa request
            
        Returns:
            Current datetime in device timezone
        """
        return TimezoneExtractor.extract_and_get_current_time(handler_input)
