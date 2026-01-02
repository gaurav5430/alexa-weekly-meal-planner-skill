"""
Local testing script for Alexa skill without deployment.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add lambda to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lambda.lambda_function import lambda_handler


def load_mock_request(request_name: str) -> dict:
    """Load mock Alexa request from fixtures."""
    fixtures_path = Path(__file__).parent.parent / "tests" / "fixtures" / "mock_alexa_requests.json"
    
    with open(fixtures_path, 'r') as f:
        requests = json.load(f)
    
    if request_name not in requests:
        raise ValueError(f"Request '{request_name}' not found in fixtures")
    
    return requests[request_name]


def test_intent(request_name: str):
    """
    Test a specific intent locally.
    
    Args:
        request_name: Name of request from mock_alexa_requests.json
    """
    print(f"\n{'='*60}")
    print(f"Testing: {request_name}")
    print(f"{'='*60}\n")
    
    # Load mock request
    try:
        event = load_mock_request(request_name)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Add timestamp to context
    context = {
        "requestId": "test-request-123",
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke lambda handler
    try:
        response = lambda_handler(event, context)
        
        # Extract and display response
        if 'response' in response:
            speech_output = response['response'].get('outputSpeech', {}).get('ssml', '')
            # Remove SSML tags for cleaner output
            speech_text = speech_output.replace('<speak>', '').replace('</speak>', '').strip()
            
            print("✓ Success!")
            print(f"\nAlexa says: \"{speech_text}\"\n")
            
            # Show full response in debug mode
            if '--debug' in sys.argv:
                print("\nFull Response:")
                print(json.dumps(response, indent=2))
        else:
            print("✗ Error: No response returned")
            print(json.dumps(response, indent=2))
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def run_all_tests():
    """Run all test scenarios."""
    test_scenarios = [
        "LaunchRequest",
        "GetMealIntent_Dinner",
        "GetTodayMealsIntent",
        "GetSpecificDayMealIntent_Friday_Breakfast",
        "GetNextMealIntent",
        "HelpIntent",
        "CancelIntent"
    ]
    
    print("\n" + "="*60)
    print("Running All Test Scenarios")
    print("="*60)
    
    for scenario in test_scenarios:
        test_intent(scenario)
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")


def interactive_mode():
    """Interactive testing mode."""
    print("\n" + "="*60)
    print("Alexa Skill - Interactive Test Mode")
    print("="*60)
    
    available_requests = [
        "LaunchRequest",
        "GetMealIntent_Dinner",
        "GetTodayMealsIntent",
        "GetSpecificDayMealIntent_Friday_Breakfast",
        "GetNextMealIntent",
        "HelpIntent",
        "CancelIntent"
    ]
    
    print("\nAvailable test scenarios:")
    for i, req in enumerate(available_requests, 1):
        print(f"  {i}. {req}")
    print("  0. Run all tests")
    print("  q. Quit")
    
    while True:
        choice = input("\nSelect a scenario (number or name): ").strip()
        
        if choice.lower() == 'q':
            print("Goodbye!")
            break
        
        if choice == '0':
            run_all_tests()
            continue
        
        # Try numeric selection
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available_requests):
                test_intent(available_requests[idx])
                continue
        except ValueError:
            pass
        
        # Try name selection
        if choice in available_requests:
            test_intent(choice)
        else:
            print(f"Invalid selection: {choice}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            run_all_tests()
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python manual_test.py                    # Interactive mode")
            print("  python manual_test.py --all              # Run all tests")
            print("  python manual_test.py <request_name>     # Test specific request")
            print("  python manual_test.py --debug            # Show full responses")
        else:
            # Test specific request
            request_name = sys.argv[1]
            test_intent(request_name)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
