"""
Integration tests for Google Sheets service.
Tests SheetsService with mock Google Sheets responses per T050.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add lambda folder to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'lambda'))

from services.sheets_service import SheetsService
from models.meal_plan import Meal, MealPlan


class TestSheetsServiceIntegration:
    """Integration tests for SheetsService with mocked Google Sheets API."""
    
    @pytest.fixture
    def mock_sheet_data_valid(self):
        """Fixture providing valid sheet data structure."""
        return [
            ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner'],
            ['Monday', 'Oatmeal', 'Apple', 'Grilled Chicken Salad', 'Yogurt', 'Pasta'],
            ['Tuesday', 'Scrambled Eggs', 'Banana', 'Turkey Sandwich', 'Carrots', 'Stir Fry'],
            ['Wednesday', 'Pancakes', 'Orange', 'Soup and Salad', 'Nuts', 'Tacos'],
            ['Thursday', 'Toast', 'Grapes', 'Pizza', 'Cheese', 'Fish'],
            ['Friday', 'Cereal', 'Berries', 'Burrito', 'Hummus', 'Steak'],
            ['Saturday', 'Smoothie', 'Trail Mix', 'Pasta Salad', 'Crackers', 'BBQ Chicken'],
            ['Sunday', 'French Toast', 'Fruit Salad', 'Roast Beef', 'Popcorn', 'Lasagna']
        ]
    
    @pytest.fixture
    def mock_sheet_data_empty_meals(self):
        """Fixture with some empty meal slots."""
        return [
            ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner'],
            ['Monday', 'Oatmeal', '', 'Grilled Chicken Salad', 'Yogurt', 'Pasta'],
            ['Tuesday', 'Scrambled Eggs', 'Banana', '', 'Carrots', 'Stir Fry'],
            ['Wednesday', '', 'Orange', 'Soup and Salad', 'Nuts', 'Tacos'],
            ['Thursday', 'Toast', 'Grapes', 'Pizza', '', 'Fish'],
            ['Friday', 'Cereal', 'Berries', 'Burrito', 'Hummus', ''],
            ['Saturday', 'Smoothie', 'Trail Mix', 'Pasta Salad', 'Crackers', 'BBQ Chicken'],
            ['Sunday', 'French Toast', 'Fruit Salad', 'Roast Beef', 'Popcorn', 'Lasagna']
        ]
    
    @pytest.fixture
    def mock_sheet_data_invalid_headers(self):
        """Fixture with invalid headers."""
        return [
            ['Date', 'Morning', 'Snack1', 'Lunch', 'Snack2', 'Dinner'],
            ['Monday', 'Oatmeal', 'Apple', 'Salad', 'Yogurt', 'Pasta']
        ]
    
    @pytest.fixture
    def mock_sheet_data_insufficient_rows(self):
        """Fixture with insufficient data rows."""
        return [
            ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner'],
            ['Monday', 'Oatmeal', 'Apple', 'Salad', 'Yogurt', 'Pasta'],
            ['Tuesday', 'Eggs', 'Banana', 'Sandwich', 'Carrots', 'Stir Fry']
        ]
    
    @pytest.fixture
    def mock_gspread_client(self):
        """Fixture providing a mocked gspread client."""
        mock_client = MagicMock()
        mock_sheet = MagicMock()
        mock_worksheet = MagicMock()
        
        mock_client.open_by_key.return_value = mock_sheet
        mock_sheet.worksheet.return_value = mock_worksheet
        
        return {
            'client': mock_client,
            'sheet': mock_sheet,
            'worksheet': mock_worksheet
        }
    
    @patch('services.sheets_service.gspread.authorize')
    @patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name')
    def test_fetch_meal_plan_success(self, mock_creds, mock_authorize, 
                                     mock_sheet_data_valid, mock_gspread_client):
        """Test successful meal plan fetch with valid data."""
        # Setup mocks
        mock_authorize.return_value = mock_gspread_client['client']
        mock_gspread_client['worksheet'].get_all_values.return_value = mock_sheet_data_valid
        
        # Create service and fetch data
        service = SheetsService()
        meal_plan = service.fetch_meal_plan()
        
        # Assertions
        assert isinstance(meal_plan, MealPlan)
        assert meal_plan.is_valid is True
        assert meal_plan.last_updated is not None
        assert len(meal_plan.meals) == 7  # 7 days
        
        # Verify Monday's meals
        monday_meals = meal_plan.meals.get('Monday')
        assert monday_meals is not None
        assert monday_meals['breakfast'].name == 'Oatmeal'
        assert monday_meals['morning_snack'].name == 'Apple'
        assert monday_meals['lunch'].name == 'Grilled Chicken Salad'
        assert monday_meals['evening_snack'].name == 'Yogurt'
        assert monday_meals['dinner'].name == 'Pasta'
        
        # Verify Sunday's dinner
        sunday_meals = meal_plan.meals.get('Sunday')
        assert sunday_meals is not None
        assert sunday_meals['dinner'].name == 'Lasagna'
    
    @patch('services.sheets_service.gspread.authorize')
    @patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name')
    def test_fetch_meal_plan_with_empty_slots(self, mock_creds, mock_authorize,
                                               mock_sheet_data_empty_meals, mock_gspread_client):
        """Test meal plan fetch handles empty meal slots correctly."""
        # Setup mocks
        mock_authorize.return_value = mock_gspread_client['client']
        mock_gspread_client['worksheet'].get_all_values.return_value = mock_sheet_data_empty_meals
        
        # Create service and fetch data
        service = SheetsService()
        meal_plan = service.fetch_meal_plan()
        
        # Assertions
        assert meal_plan.is_valid is True
        
        # Verify empty slots are handled
        monday_meals = meal_plan.meals.get('Monday')
        assert monday_meals['morning_snack'].name == ''  # Empty slot
        
        tuesday_meals = meal_plan.meals.get('Tuesday')
        assert tuesday_meals['lunch'].name == ''  # Empty slot
        
        wednesday_meals = meal_plan.meals.get('Wednesday')
        assert wednesday_meals['breakfast'].name == ''  # Empty slot
        
        friday_meals = meal_plan.meals.get('Friday')
        assert friday_meals['dinner'].name == ''  # Empty slot
    
    @patch('services.sheets_service.gspread.authorize')
    @patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name')
    def test_validate_sheet_structure_invalid_headers(self, mock_creds, mock_authorize,
                                                       mock_sheet_data_invalid_headers,
                                                       mock_gspread_client):
        """Test that invalid headers are rejected."""
        # Setup mocks
        mock_authorize.return_value = mock_gspread_client['client']
        mock_gspread_client['worksheet'].get_all_values.return_value = mock_sheet_data_invalid_headers
        
        # Create service and attempt to fetch
        service = SheetsService()
        
        with pytest.raises(ValueError, match="Invalid sheet structure"):
            service.fetch_meal_plan()
    
    @patch('services.sheets_service.gspread.authorize')
    @patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name')
    def test_validate_sheet_structure_insufficient_rows(self, mock_creds, mock_authorize,
                                                         mock_sheet_data_insufficient_rows,
                                                         mock_gspread_client):
        """Test that sheets with insufficient rows are rejected."""
        # Setup mocks
        mock_authorize.return_value = mock_gspread_client['client']
        mock_gspread_client['worksheet'].get_all_values.return_value = mock_sheet_data_insufficient_rows
        
        # Create service and attempt to fetch
        service = SheetsService()
        
        with pytest.raises(ValueError, match="Invalid sheet structure"):
            service.fetch_meal_plan()
    
    @patch('services.sheets_service.gspread.authorize')
    @patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name')
    def test_sheets_api_connection_error(self, mock_creds, mock_authorize, mock_gspread_client):
        """Test handling of Google Sheets API connection errors."""
        # Setup mocks to raise an exception
        mock_authorize.return_value = mock_gspread_client['client']
        mock_gspread_client['client'].open_by_key.side_effect = Exception("API connection failed")
        
        # Create service and attempt to fetch
        service = SheetsService()
        
        with pytest.raises(Exception, match="API connection failed"):
            service.fetch_meal_plan()
    
    @patch('services.sheets_service.gspread.authorize')
    @patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name')
    def test_sheets_worksheet_not_found(self, mock_creds, mock_authorize, mock_gspread_client):
        """Test handling when worksheet is not found."""
        # Setup mocks to raise worksheet not found error
        mock_authorize.return_value = mock_gspread_client['client']
        mock_gspread_client['sheet'].worksheet.side_effect = Exception("Worksheet not found")
        
        # Create service and attempt to fetch
        service = SheetsService()
        
        with pytest.raises(Exception, match="Worksheet not found"):
            service.fetch_meal_plan()
    
    def test_validate_sheet_structure_empty_data(self):
        """Test validation with completely empty data."""
        service = SheetsService.__new__(SheetsService)  # Create without __init__
        
        # Test with empty list
        assert service.validate_sheet_structure([]) is False
        
        # Test with only headers
        assert service.validate_sheet_structure([
            ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner']
        ]) is False
    
    def test_validate_sheet_structure_missing_day(self):
        """Test validation when a day is missing."""
        service = SheetsService.__new__(SheetsService)
        
        data = [
            ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Evening Snack', 'Dinner'],
            ['Monday', 'Oatmeal', 'Apple', 'Salad', 'Yogurt', 'Pasta'],
            ['Tuesday', 'Eggs', 'Banana', 'Sandwich', 'Carrots', 'Stir Fry'],
            ['Wednesday', 'Pancakes', 'Orange', 'Soup', 'Nuts', 'Tacos'],
            ['Thursday', 'Toast', 'Grapes', 'Pizza', 'Cheese', 'Fish'],
            ['Friday', 'Cereal', 'Berries', 'Burrito', 'Hummus', 'Steak'],
            ['Saturday', 'Smoothie', 'Trail Mix', 'Pasta Salad', 'Crackers', 'BBQ']
            # Sunday is missing
        ]
        
        assert service.validate_sheet_structure(data) is False
    
    @patch('services.sheets_service.gspread.authorize')
    @patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name')
    def test_meal_plan_metadata(self, mock_creds, mock_authorize, 
                                mock_sheet_data_valid, mock_gspread_client):
        """Test that meal plan metadata is properly set."""
        # Setup mocks
        mock_authorize.return_value = mock_gspread_client['client']
        mock_gspread_client['worksheet'].get_all_values.return_value = mock_sheet_data_valid
        
        # Create service and fetch data
        service = SheetsService()
        before_fetch = datetime.now()
        meal_plan = service.fetch_meal_plan()
        after_fetch = datetime.now()
        
        # Assertions on metadata
        assert meal_plan.sheet_id is not None
        assert meal_plan.is_valid is True
        assert meal_plan.last_updated is not None
        assert before_fetch <= meal_plan.last_updated <= after_fetch
    
    @patch('services.sheets_service.gspread.authorize')
    @patch('services.sheets_service.ServiceAccountCredentials.from_json_keyfile_name')
    def test_case_insensitive_headers(self, mock_creds, mock_authorize, mock_gspread_client):
        """Test that header validation is case-insensitive."""
        # Data with mixed case headers
        data = [
            ['DAY', 'BREAKFAST', 'Morning Snack', 'lunch', 'Evening SNACK', 'Dinner'],
            ['Monday', 'Oatmeal', 'Apple', 'Salad', 'Yogurt', 'Pasta'],
            ['Tuesday', 'Eggs', 'Banana', 'Sandwich', 'Carrots', 'Stir Fry'],
            ['Wednesday', 'Pancakes', 'Orange', 'Soup', 'Nuts', 'Tacos'],
            ['Thursday', 'Toast', 'Grapes', 'Pizza', 'Cheese', 'Fish'],
            ['Friday', 'Cereal', 'Berries', 'Burrito', 'Hummus', 'Steak'],
            ['Saturday', 'Smoothie', 'Trail Mix', 'Pasta Salad', 'Crackers', 'BBQ'],
            ['Sunday', 'French Toast', 'Fruit', 'Roast', 'Popcorn', 'Lasagna']
        ]
        
        # Setup mocks
        mock_authorize.return_value = mock_gspread_client['client']
        mock_gspread_client['worksheet'].get_all_values.return_value = data
        
        # Should succeed despite mixed case
        service = SheetsService()
        meal_plan = service.fetch_meal_plan()
        
        assert meal_plan.is_valid is True
        assert len(meal_plan.meals) == 7
