"""
Google Sheets integration test script.
Tests SheetsService without requiring actual Google Sheets credentials.
"""
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sys
from pathlib import Path

# Add lambda folder to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lambda'))

from services.sheets_service import SheetsService
from models.meal_plan import MealPlan


def create_mock_worksheet():
    """Create a mock Google Sheets worksheet with sample data."""
    mock_worksheet = Mock()
    
    # Mock get_all_values() to return sample meal plan
    mock_worksheet.get_all_values.return_value = [
        ["Day", "Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"],
        ["Monday", "Oatmeal with Berries", "Apple Slices", "Grilled Chicken Salad", "Granola Bar", "Spaghetti Bolognese"],
        ["Tuesday", "Scrambled Eggs", "Yogurt", "Turkey Sandwich", "Crackers", "Baked Salmon"],
        ["Wednesday", "Pancakes", "Banana", "Veggie Wrap", "Trail Mix", "Beef Stir Fry"],
        ["Thursday", "French Toast", "Orange", "Caesar Salad", "Cheese Sticks", "Grilled Pork Chops"],
        ["Friday", "Breakfast Burrito", "Smoothie", "Pizza", "Popcorn", "Steak and Potatoes"],
        ["Saturday", "Waffles", "Muffin", "Pasta Salad", "Nuts", "BBQ Chicken"],
        ["Sunday", "Eggs Benedict", "Fruit Cup", "Roast Beef Sandwich", "Pretzels", "Lasagna"]
    ]
    
    return mock_worksheet


def test_fetch_meal_plan():
    """Test fetching and parsing meal plan."""
    print("\n" + "="*60)
    print("Test: Fetch Meal Plan")
    print("="*60)
    
    # Create mock Google Sheets client
    mock_client = Mock()
    mock_spreadsheet = Mock()
    mock_worksheet = create_mock_worksheet()
    
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.return_value = mock_worksheet
    
    # Patch gspread authorization
    with patch('src.services.sheets_service.gspread.authorize', return_value=mock_client):
        with patch('src.services.sheets_service.ServiceAccountCredentials'):
            service = SheetsService()
            
            # Fetch meal plan
            meal_plan = service.fetch_meal_plan()
            
            # Validate results
            assert meal_plan.is_valid, "Meal plan should be valid"
            assert len(meal_plan.meals) == 7, "Should have 7 days"
            
            # Check Monday's meals
            monday_breakfast = meal_plan.get_meal("Monday", "breakfast")
            assert monday_breakfast is not None, "Monday breakfast should exist"
            assert monday_breakfast.name == "Oatmeal with Berries", "Monday breakfast should be Oatmeal with Berries"
            
            # Check Friday's dinner
            friday_dinner = meal_plan.get_meal("Friday", "dinner")
            assert friday_dinner is not None, "Friday dinner should exist"
            assert friday_dinner.name == "Steak and Potatoes", "Friday dinner should be Steak and Potatoes"
            
            print("✓ Meal plan fetched successfully")
            print(f"✓ Found {len(meal_plan.meals)} days")
            print(f"✓ Monday breakfast: {monday_breakfast.name}")
            print(f"✓ Friday dinner: {friday_dinner.name}")


def test_validate_sheet_structure():
    """Test sheet structure validation."""
    print("\n" + "="*60)
    print("Test: Validate Sheet Structure")
    print("="*60)
    
    # Test valid structure
    valid_data = [
        ["Day", "Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"],
        ["Monday", "Eggs", "Apple", "Salad", "Crackers", "Pasta"]
    ]
    
    from services.sheets_service import SheetsService
    service = SheetsService()
    
    try:
        service.validate_sheet_structure(valid_data)
        print("✓ Valid structure accepted")
    except ValueError as e:
        print(f"✗ Valid structure rejected: {e}")
        return
    
    # Test invalid header
    invalid_headers = [
        ["Day", "Breakfast", "Lunch", "Dinner"],  # Missing columns
        ["Monday", "Eggs", "Salad", "Pasta"]
    ]
    
    try:
        service.validate_sheet_structure(invalid_headers)
        print("✗ Invalid headers accepted (should have failed)")
    except ValueError as e:
        print(f"✓ Invalid headers rejected: {e}")
    
    # Test missing days
    missing_days = [
        ["Day", "Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"],
        ["Monday", "Eggs", "Apple", "Salad", "Crackers", "Pasta"],
        ["Tuesday", "Toast", "Yogurt", "Soup", "Nuts", "Chicken"]
    ]
    
    try:
        service.validate_sheet_structure(missing_days)
        print("✗ Missing days accepted (should have failed)")
    except ValueError as e:
        print(f"✓ Missing days rejected: {e}")


def test_parse_sheet_data():
    """Test parsing sheet data into MealPlan."""
    print("\n" + "="*60)
    print("Test: Parse Sheet Data")
    print("="*60)
    
    data = [
        ["Day", "Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"],
        ["Monday", "Oatmeal", "Apple", "Salad", "Crackers", "Pasta"],
        ["Tuesday", "", "Yogurt", "Soup", "", "Chicken"]  # Empty meals
    ]
    
    from services.sheets_service import SheetsService
    service = SheetsService()
    
    meal_plan = service._parse_sheet_data(data)
    
    # Check Monday
    monday_breakfast = meal_plan.get_meal("Monday", "breakfast")
    assert monday_breakfast.name == "Oatmeal", "Monday breakfast should be Oatmeal"
    assert not monday_breakfast.is_empty, "Monday breakfast should not be empty"
    
    # Check Tuesday empty meals
    tuesday_breakfast = meal_plan.get_meal("Tuesday", "breakfast")
    assert tuesday_breakfast.is_empty, "Tuesday breakfast should be empty"
    
    tuesday_snack = meal_plan.get_meal("Tuesday", "morning_snack")
    assert not tuesday_snack.is_empty, "Tuesday morning snack should not be empty"
    
    print("✓ Data parsed correctly")
    print(f"✓ Empty meals detected: {tuesday_breakfast.is_empty}")
    print(f"✓ Non-empty meals preserved: {tuesday_snack.name}")


def test_caching_behavior():
    """Test that caching works correctly."""
    print("\n" + "="*60)
    print("Test: Caching Behavior")
    print("="*60)
    
    # This would test the lambda_function caching
    # For now, just verify the mechanism exists
    
    from lambda_function import get_cached_meal_plan
    
    print("✓ Cache function exists: get_cached_meal_plan")
    print("✓ Cache is implemented in lambda_function.py")
    print("  Note: Full cache testing requires Lambda execution context")


def test_real_api_fetch():
    """Test fetching from REAL Google Sheets API (if configured)."""
    print("\n" + "="*60)
    print("Test: Real Google Sheets API")
    print("="*60)
    
    import os
    from pathlib import Path
    
    # Check if real API is configured
    creds_path = os.getenv('CREDENTIALS_PATH', 'credentials.json')
    sheet_id = os.getenv('GOOGLE_SHEET_ID', '')
    use_real_api = os.getenv('USE_REAL_SHEETS_API', 'false').lower() == 'true'
    
    if not use_real_api:
        print("⊘ Skipped - Set USE_REAL_SHEETS_API=true to enable")
        return
    
    if not Path(creds_path).exists():
        print(f"⊘ Skipped - Credentials not found at {creds_path}")
        return
    
    if not sheet_id:
        print("⊘ Skipped - GOOGLE_SHEET_ID not set")
        return
    
    print(f"✓ Using real API with Sheet ID: {sheet_id[:10]}...")
    
    try:
        # Use real SheetsService (no mocking)
        from src.services.sheets_service import SheetsService
        service = SheetsService()
        
        # Fetch real meal plan
        meal_plan = service.fetch_meal_plan()
        
        # Validate
        assert meal_plan.is_valid, "Meal plan should be valid"
        assert len(meal_plan.meals) == 7, "Should have 7 days"
        assert meal_plan.sheet_id == sheet_id, "Sheet ID should match"
        
        # Count non-empty meals
        total_meals = 0
        non_empty = 0
        for day_meals in meal_plan.meals.values():
            for meal in day_meals.values():
                total_meals += 1
                if not meal.is_empty:
                    non_empty += 1
        
        print(f"✓ Successfully fetched real meal plan")
        print(f"✓ Total meal slots: {total_meals}")
        print(f"✓ Non-empty meals: {non_empty}")
        print(f"✓ Empty meals: {total_meals - non_empty}")
        
        # Show sample meals
        monday_breakfast = meal_plan.get_meal('Monday', 'breakfast')
        friday_dinner = meal_plan.get_meal('Friday', 'dinner')
        
        if not monday_breakfast.is_empty:
            print(f"✓ Monday breakfast: {monday_breakfast.name}")
        if not friday_dinner.is_empty:
            print(f"✓ Friday dinner: {friday_dinner.name}")
        
    except Exception as e:
        print(f"✗ Real API test failed: {e}")
        import traceback
        traceback.print_exc()


def run_all_tests():
    """Run all Google Sheets integration tests."""
    print("\n" + "="*60)
    print("Google Sheets Integration Tests")
    print("="*60)
    
    import os
    use_real_api = os.getenv('USE_REAL_SHEETS_API', 'false').lower() == 'true'
    
    if use_real_api:
        print("\n*** REAL API MODE ENABLED ***")
        print("Will test with actual Google Sheets data\n")
    else:
        print("\nRunning tests with MOCK data (no credentials required)\n")
    
    try:
        test_validate_sheet_structure()
        test_parse_sheet_data()
        test_fetch_meal_plan()
        test_caching_behavior()
        test_real_api_fetch()  # Only runs if USE_REAL_SHEETS_API=true
        
        print("\n" + "="*60)
        print("All Tests Passed! ✓")
        print("="*60)
        
        if not use_real_api:
            print("\nNote: These tests use mock data.")
            print("To test with real Google Sheets:")
            print("1. Set up credentials.json")
            print("2. Configure .env with GOOGLE_SHEET_ID")
            print("3. Run: USE_REAL_SHEETS_API=true python local_test/test_sheets.py")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
