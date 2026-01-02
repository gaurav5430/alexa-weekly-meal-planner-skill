"""
Test configuration for switching between mock and real API calls.

This module provides configuration for running tests with either mocked
or real Google Sheets API calls, enabling true end-to-end testing.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class TestConfig:
    """Configuration for test execution."""
    
    # Check if real credentials are available
    USE_REAL_SHEETS_API = os.getenv('USE_REAL_SHEETS_API', 'false').lower() == 'true'
    
    # Path to credentials file
    CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH', 'credentials.json')
    
    # Google Sheet ID for testing
    TEST_GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '')
    
    @classmethod
    def can_run_real_api_tests(cls) -> bool:
        """
        Check if real API tests can be run.
        
        Returns:
            True if credentials and sheet ID are available
        """
        credentials_exist = Path(cls.CREDENTIALS_PATH).exists()
        sheet_id_set = bool(cls.TEST_GOOGLE_SHEET_ID)
        
        return credentials_exist and sheet_id_set and cls.USE_REAL_SHEETS_API
    
    @classmethod
    def get_test_mode_info(cls) -> str:
        """
        Get information about current test mode.
        
        Returns:
            String describing the test mode
        """
        if cls.can_run_real_api_tests():
            return f"REAL API MODE - Using Sheet ID: {cls.TEST_GOOGLE_SHEET_ID[:10]}..."
        else:
            reasons = []
            if not cls.USE_REAL_SHEETS_API:
                reasons.append("USE_REAL_SHEETS_API not set to 'true'")
            if not Path(cls.CREDENTIALS_PATH).exists():
                reasons.append(f"Credentials not found at {cls.CREDENTIALS_PATH}")
            if not cls.TEST_GOOGLE_SHEET_ID:
                reasons.append("GOOGLE_SHEET_ID not set")
            
            return f"MOCK MODE - Reason: {', '.join(reasons)}"
    
    @classmethod
    def print_test_mode(cls):
        """Print current test mode to console."""
        print("\n" + "="*70)
        print("TEST MODE CONFIGURATION")
        print("="*70)
        print(f"Mode: {cls.get_test_mode_info()}")
        print("="*70 + "\n")
