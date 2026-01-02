"""
Application settings loaded from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application configuration settings."""
    
    # Google Sheets configuration
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '')
    CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH', 'credentials.json')
    
    # Worksheet name (default tab in Google Sheet)
    WORKSHEET_NAME = os.getenv('WORKSHEET_NAME', 'Sheet1')
    
    # Cache settings
    CACHE_DURATION_MINUTES = int(os.getenv('CACHE_DURATION_MINUTES', '60'))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required settings are configured.
        
        Returns:
            True if settings are valid, False otherwise
        """
        if not cls.GOOGLE_SHEET_ID:
            print("ERROR: GOOGLE_SHEET_ID not set in environment")
            return False
        
        if not os.path.exists(cls.CREDENTIALS_PATH):
            print(f"ERROR: Credentials file not found at {cls.CREDENTIALS_PATH}")
            return False
        
        return True


# Create singleton instance
settings = Settings()
