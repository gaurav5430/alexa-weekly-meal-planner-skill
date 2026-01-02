# Command-Line Testing

You can now test your Alexa skill directly from the command line using natural language!

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Test with any natural language query
python test_cli.py "what's for dinner?"
python test_cli.py "what should I cook today?"
python test_cli.py "what's for lunch on Friday?"
python test_cli.py "help"
```

## Examples

### Basic Queries
```bash
# Ask about a specific meal
python test_cli.py "what's for breakfast?"

# Ask about today's meals
python test_cli.py "what should I cook today?"

# Ask about a specific day and meal
python test_cli.py "what's for dinner on Monday?"

# Ask what's next
python test_cli.py "what's next?"
```

### Get Help
```bash
python test_cli.py "help"
```

### See Full JSON Response
```bash
python test_cli.py "what's for dinner?" --json
python test_cli.py "what's for dinner?" -v
```

## Sample Output

```
============================================================
📱 User says: "what's for dinner?"
============================================================

🔍 Detected Intent: GetMealIntent
📋 Slots:
   - MealType: dinner

⚙️  Processing request...

🔊 Alexa responds:
   "For dinner today, you should make Aloo tamatar."

============================================================
```

## Supported Phrases

The CLI supports all the same natural language patterns as the testing framework:

- "what's for [meal]?" - Get specific meal
- "what should I cook today?" - Get all today's meals  
- "what's for [meal] on [day]?" - Get specific day/meal
- "what's next?" - Get next meal
- "help" - Get help
- "stop" / "cancel" - Stop

## Behind the Scenes

The CLI uses the same `text_to_intent()` utility from the test framework:

1. Converts your text to an Alexa intent request
2. Passes it through your lambda_handler
3. Displays the response in a friendly format

## Integration with pytest

You can also run automated tests with text prompts:

```bash
# Run all text-based tests
pytest tests/test_text_based_intents.py -v

# Run a specific test
pytest tests/test_text_based_intents.py::TestTextBasedIntents::test_whats_for_dinner -v
```

## Tips

- Make sure your Google Sheets credentials are configured
- The responses come from your actual meal plan data
- Use quotes around multi-word phrases: `"what's for dinner?"`
- Add `--json` to see the full Alexa response structure
