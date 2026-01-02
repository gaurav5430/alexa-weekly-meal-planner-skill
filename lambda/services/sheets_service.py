"""
Google Sheets service for fetching meal plan data.
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import Optional
from models.meal_plan import Meal, MealPlan
from config.settings import settings


class SheetsService:
    """Service for interacting with Google Sheets."""
    
    def __init__(self):
        """Initialize Google Sheets client."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Set up Google Sheets API client with service account credentials."""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                settings.CREDENTIALS_PATH,
                scope
            )
            self.client = gspread.authorize(creds)
        except Exception as e:
            print(f"Error initializing Google Sheets client: {e}")
            raise
    
    def fetch_meal_plan(self) -> MealPlan:
        """
        Fetch meal plan from Google Sheet.
        
        Returns:
            MealPlan object with all meals
        
        Raises:
            Exception: If sheet cannot be accessed or parsed
        """
        try:
            # Open the spreadsheet
            sheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
            worksheet = sheet.worksheet(settings.WORKSHEET_NAME)
            
            # Get all values
            all_values = worksheet.get_all_values()
            
            # Validate structure
            if not self.validate_sheet_structure(all_values):
                raise ValueError("Invalid sheet structure")
            
            # Parse into MealPlan
            meal_plan = self._parse_sheet_data(all_values)
            meal_plan.sheet_id = settings.GOOGLE_SHEET_ID
            meal_plan.last_updated = datetime.now()
            meal_plan.is_valid = True
            
            return meal_plan
            
        except Exception as e:
            print(f"Error fetching meal plan: {e}")
            raise
    
    def validate_sheet_structure(self, data: list) -> bool:
        """
        Validate that the sheet has the expected structure.
        
        Expected format:
        Row 1: Headers (Day, Breakfast, Morning Snack, Lunch, Evening Snack, Dinner)
        Rows 2-8: Day names and meal data
        
        Args:
            data: All values from the sheet
        
        Returns:
            True if structure is valid, False otherwise
        """
        if not data or len(data) < 2:
            print("Sheet has insufficient rows")
            return False
        
        # Check headers (case-insensitive)
        headers = [h.lower().strip() for h in data[0]]
        expected_headers = ['day', 'breakfast', 'morning snack', 'lunch', 'evening snack', 'dinner']
        
        if headers != expected_headers:
            print(f"Invalid headers. Expected: {expected_headers}, Got: {headers}")
            return False
        
        # Check that we have 7 days of data
        if len(data) < 8:  # header + 7 days
            print(f"Insufficient data rows. Expected 8 (header + 7 days), Got: {len(data)}")
            return False
        
        # Validate day names
        expected_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        actual_days = [row[0].lower().strip() for row in data[1:8] if row]
        
        if len(actual_days) != 7:
            print(f"Expected 7 days, found {len(actual_days)}")
            return False
        
        # Check that all expected days are present (order doesn't matter)
        for day in expected_days:
            if day not in actual_days:
                print(f"Missing day: {day}")
                return False
        
        return True
    
    def _parse_sheet_data(self, data: list) -> MealPlan:
        """
        Parse sheet data into MealPlan object.
        
        Args:
            data: All values from the sheet
        
        Returns:
            MealPlan object
        """
        meal_plan = MealPlan()
        
        # Skip header row, process data rows
        for row in data[1:8]:  # Rows 2-8 (7 days)
            if not row or len(row) < 6:
                continue
            
            day_name = row[0].strip().capitalize()
            
            # Create meals for this day
            day_meals = {}
            
            # Column mapping (based on headers)
            day_meals['breakfast'] = Meal(
                day_of_week=day_name,
                meal_period='breakfast',
                name=row[1].strip() if len(row) > 1 else ""
            )
            day_meals['morning_snack'] = Meal(
                day_of_week=day_name,
                meal_period='morning_snack',
                name=row[2].strip() if len(row) > 2 else ""
            )
            day_meals['lunch'] = Meal(
                day_of_week=day_name,
                meal_period='lunch',
                name=row[3].strip() if len(row) > 3 else ""
            )
            day_meals['evening_snack'] = Meal(
                day_of_week=day_name,
                meal_period='evening_snack',
                name=row[4].strip() if len(row) > 4 else ""
            )
            day_meals['dinner'] = Meal(
                day_of_week=day_name,
                meal_period='dinner',
                name=row[5].strip() if len(row) > 5 else ""
            )
            
            meal_plan.meals[day_name] = day_meals
        
        return meal_plan
