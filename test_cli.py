#!/usr/bin/env python3
"""
Command-line interface for testing Alexa skill with natural language.

Usage:
    python test_cli.py "what's for dinner?"
    python test_cli.py "what should I cook today?"
    python test_cli.py "what's for lunch on Friday?"
    
With virtual environment:
    source venv/bin/activate && python test_cli.py "help"
"""
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.utils.text_to_intent import text_to_intent
import sys
from pathlib import Path

# Add lambda folder to path
sys.path.insert(0, str(Path(__file__).parent / 'lambda'))

from lambda_function import lambda_handler


def main():
    """Run Alexa skill test from command line."""
    if len(sys.argv) < 2:
        print("Usage: python test_cli.py \"<your question>\"")
        print("\nExamples:")
        print('  python test_cli.py "what\'s for dinner?"')
        print('  python test_cli.py "what should I cook today?"')
        print('  python test_cli.py "what\'s for lunch on Friday?"')
        print('  python test_cli.py "help"')
        print('  python test_cli.py "stop"')
        sys.exit(1)
    
    # Get the text prompt from command line
    text_prompt = " ".join(sys.argv[1:])
    
    print(f"\n{'='*60}")
    print(f"📱 User says: \"{text_prompt}\"")
    print(f"{'='*60}\n")
    
    try:
        # Convert text to Alexa intent
        event = text_to_intent(text_prompt)
        
        # Show the detected intent
        intent_name = event['request']['intent']['name']
        slots = event['request']['intent']['slots']
        
        print(f"🔍 Detected Intent: {intent_name}")
        if slots:
            print(f"📋 Slots:")
            for slot_name, slot_data in slots.items():
                print(f"   - {slot_name}: {slot_data.get('value', 'N/A')}")
        print()
        
        # Call the lambda handler
        print("⚙️  Processing request...\n")
        response = lambda_handler(event, None)
        
        # Extract and display the response
        if 'response' in response and 'outputSpeech' in response['response']:
            speech = response['response']['outputSpeech']
            
            if 'ssml' in speech:
                # Remove SSML tags for cleaner display
                import re
                text = speech['ssml']
                # Remove <speak> tags
                text = re.sub(r'<speak>|</speak>', '', text)
                # Remove <break> tags
                text = re.sub(r'<break[^>]*>', ' ', text)
                # Remove <emphasis> tags but keep content
                text = re.sub(r'<emphasis[^>]*>|</emphasis>', '', text)
                text = text.strip()
            elif 'text' in speech:
                text = speech['text']
            else:
                text = "No speech output"
            
            print(f"🔊 Alexa responds:")
            print(f"   \"{text}\"")
        else:
            print("❌ No speech response generated")
        
        # Show if session should end
        should_end = response.get('response', {}).get('shouldEndSession', False)
        if should_end:
            print(f"\n👋 Session ended")
        
        print(f"\n{'='*60}\n")
        
        # Optionally show full JSON response
        if '--json' in sys.argv or '--verbose' in sys.argv or '-v' in sys.argv:
            print("\n📄 Full Response JSON:")
            print(json.dumps(response, indent=2))
            print()
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Tip: Try one of these phrases:")
        print('   - "what\'s for dinner?"')
        print('   - "what should I cook today?"')
        print('   - "what\'s for breakfast on Monday?"')
        print('   - "what\'s next?"')
        print('   - "help"')
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
