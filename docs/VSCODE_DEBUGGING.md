# VS Code Alexa Skill Debugging Guide

This guide explains how to debug your Alexa skill locally using VS Code and the Alexa Skills Toolkit extension.

## Prerequisites

### 1. Install Required Software

- **VS Code**: [Download VS Code](https://code.visualstudio.com/)
- **Python 3.8+**: Ensure Python is installed and in your PATH
- **ASK CLI**: Install the Alexa Skills Kit CLI

```bash
npm install -g ask-cli
```

### 2. Install VS Code Extension

1. Open VS Code
2. Go to Extensions (⌘+Shift+X on macOS, Ctrl+Shift+X on Windows/Linux)
3. Search for "Alexa Skills Kit (ASK) Toolkit"
4. Click Install on the extension by Amazon.com

### 3. Install Python Dependencies

The required `ask-sdk-local-debug` package is already in `requirements.txt`. Install it:

```bash
pip install -r requirements.txt
```

Or install it individually:

```bash
pip install ask-sdk-local-debug
```

## Setup

### 1. Configure ASK CLI

Initialize the ASK CLI with your Amazon Developer credentials:

```bash
ask configure
```

Follow the prompts to:
- Sign in with your Amazon Developer account
- Choose your AWS profile (if using AWS Lambda)

### 2. Get Your Skill ID

You need your Alexa Skill ID from one of these sources:

**Option A: From skill.json**
```bash
cat skill-package/skill.json
```

Look for the skill ID in the manifest.

**Option B: From Alexa Developer Console**
1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Open your skill
3. Copy the Skill ID from the top of the page

**Option C: Using ASK CLI**
```bash
ask smapi list-skills-for-vendor
```

### 3. Verify Your Environment

Ensure your `.env` file contains the Google Sheets credentials:

```bash
cat .env.example  # See the required format
```

Your `.env` should have:
```
GOOGLE_SHEETS_CREDS_FILE=/path/to/credentials.json
SPREADSHEET_ID=your-spreadsheet-id
```

## Debugging Your Skill

### Method 1: Using ASK Toolkit Extension (Recommended)

1. **Open the ASK Toolkit**
   - Click the Alexa icon in the VS Code activity bar (left sidebar)
   - Or use Command Palette (⌘+Shift+P): "Alexa: Open Toolkit"

2. **Sign in to Alexa**
   - Click "Sign in" in the ASK Toolkit panel
   - Authorize with your Amazon Developer account

3. **Download Your Skill** (if not already in workspace)
   - In ASK Toolkit, click "Download Skill"
   - Select your skill from the list
   - Choose the workspace folder

4. **Set Breakpoints**
   - Open any Python file (e.g., `src/handlers/intent_handlers.py`)
   - Click in the gutter (left of line numbers) to set breakpoints

5. **Start Debugging**
   - Press **F5** or click "Run and Debug" in the sidebar
   - Select "Debug Alexa Skill (Local)" from the dropdown
   - The debug session will start in the integrated terminal

6. **Test Your Skill**
   - Open the Alexa Simulator in the ASK Toolkit panel
   - Type or speak your test utterances
   - Your breakpoints will be hit when the code executes

### Method 2: Manual Configuration

If you prefer to manually enter credentials:

1. **Generate Access Token**
```bash
ask util generate-lwa-tokens --no-browser
```

Copy the access token from the output.

2. **Start Debug Session**
   - Press **F5**
   - Select "Debug Alexa Skill (Custom Handler)"
   - When prompted, paste your access token
   - Enter your Skill ID

3. **Test Using Alexa Simulator**
   - Use the ASK Toolkit simulator panel
   - Or use the Alexa Developer Console test page

## Debug Configurations

The `.vscode/launch.json` file contains two configurations:

### Configuration 1: Debug Alexa Skill (Local)
Uses ASK Toolkit extension commands to automatically fetch credentials.

**Pros:**
- Automatic credential management
- Integrates with ASK Toolkit extension
- No manual token handling

**Cons:**
- Requires ASK Toolkit extension to be signed in

### Configuration 2: Debug Alexa Skill (Custom Handler)
Prompts for manual token and skill ID entry.

**Pros:**
- Works without ASK Toolkit extension
- Useful for CI/CD or custom workflows

**Cons:**
- Manual token generation required
- Tokens expire after 1 hour

## Testing Workflow

### 1. Start Debug Session
```
F5 → Select configuration → Debug starts
```

### 2. Test With Sample Utterances

**Launch Intent:**
```
Open weekly meal planner
```

**Get Specific Meal:**
```
What's for dinner tonight?
What's for lunch on Wednesday?
What am I having for breakfast tomorrow?
```

**Get All Meals for a Day:**
```
What's on the menu today?
What am I eating tomorrow?
What's planned for Saturday?
```

**Get Next Meal:**
```
What's my next meal?
What am I eating next?
```

### 3. Inspect Variables

When breakpoints are hit:
- **Variables panel**: View local variables, arguments, and globals
- **Watch panel**: Add expressions to monitor
- **Call Stack**: Navigate through function calls
- **Debug Console**: Evaluate expressions and run Python code

### 4. Step Through Code

- **F10**: Step over (next line)
- **F11**: Step into (enter function)
- **Shift+F11**: Step out (exit function)
- **F5**: Continue to next breakpoint

## Common Testing Scenarios

### Test Intent Handler
Set breakpoint in `src/handlers/intent_handlers.py`:

```python
class GetMealIntentHandler(AbstractRequestHandler):
    def handle(self, handler_input):
        # Set breakpoint here
        slots = handler_input.request_envelope.request.intent.slots
```

### Test Meal Service Logic
Set breakpoint in `src/services/meal_service.py`:

```python
def get_meal_for_period(self, target_time):
    # Set breakpoint here
    day_of_week = self.time_period.get_day_of_week(target_time)
```

### Test Google Sheets Integration
Set breakpoint in `src/services/sheets_service.py`:

```python
def load_meal_plan(self):
    # Set breakpoint here
    sheet = self.spreadsheet.get_worksheet(0)
```

## Troubleshooting

### Issue: "Module 'ask_sdk_local_debug' not found"

**Solution:**
```bash
pip install ask-sdk-local-debug
```

Verify installation:
```bash
python -c "import ask_sdk_local_debug; print('OK')"
```

### Issue: "Access token expired"

Access tokens expire after 1 hour.

**Solution:**
Regenerate the token:
```bash
ask util generate-lwa-tokens --no-browser
```

Restart the debug session with the new token.

### Issue: "Skill ID not found"

**Solution:**
Manually specify the skill ID in the debug configuration or when prompted.

### Issue: "Cannot connect to Alexa service"

**Check:**
1. Internet connection is active
2. ASK CLI is configured: `ask configure list`
3. Credentials are valid: Try `ask smapi list-skills-for-vendor`

### Issue: "Google Sheets authentication failed"

**Check:**
1. `.env` file exists and contains correct credentials path
2. `credentials.json` file exists at the specified path
3. Spreadsheet ID is correct
4. Service account has access to the spreadsheet

### Issue: Breakpoints not hitting

**Check:**
1. Debug session is running (green play icon in status bar)
2. Breakpoints are in executed code paths
3. Test utterance matches the intent
4. `PYTHONPATH` includes workspace folder

**Solution:**
Add logging to verify code execution:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Handler executing")
```

## Testing Without Alexa Device

You don't need a physical Alexa device! Use these methods:

### 1. ASK Toolkit Simulator (Built into VS Code)
- Text input or voice input (with microphone)
- Shows JSON request/response
- Simulates device capabilities

### 2. Alexa Developer Console
- [https://developer.amazon.com/alexa/console/ask](https://developer.amazon.com/alexa/console/ask)
- Open your skill → Test tab
- Enable testing for "Development"

### 3. Automated Tests
Run the existing test suite:
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/

# Text-based intent tests
python test_cli.py
```

## Best Practices

### 1. Use Meaningful Breakpoints
Set breakpoints at:
- Intent handler entry points
- Business logic decision points
- External service calls (Google Sheets)
- Error handling blocks

### 2. Inspect Alexa Request Objects
When debugging, examine:
```python
handler_input.request_envelope.request  # Intent, slots, etc.
handler_input.request_envelope.session  # Session attributes
handler_input.request_envelope.context  # Device info
```

### 3. Test Edge Cases
- Invalid slot values
- Missing required slots
- Time zone boundary cases (midnight, week transitions)
- Empty meal plan data

### 4. Monitor Performance
Check execution time:
```python
import time
start = time.time()
# Your code
duration = time.time() - start
logger.info(f"Execution took {duration:.3f}s")
```

Lambda functions have timeouts (default 3s for Alexa skills).

### 5. Clean Up After Testing
Stop debug sessions when done (Shift+F5) to free resources.

## Additional Resources

- [ASK CLI Documentation](https://developer.amazon.com/docs/smapi/ask-cli-intro.html)
- [Alexa Skills Kit SDK for Python](https://alexa-skills-kit-python-sdk.readthedocs.io/)
- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [ASK Toolkit VS Code Extension](https://developer.amazon.com/docs/ask-toolkit/vs-code-ask-skills.html)

## Quick Reference

| Action | Shortcut | Description |
|--------|----------|-------------|
| Start Debugging | F5 | Launch debug session |
| Stop Debugging | Shift+F5 | End debug session |
| Step Over | F10 | Execute current line |
| Step Into | F11 | Enter function call |
| Step Out | Shift+F11 | Exit current function |
| Continue | F5 | Run to next breakpoint |
| Toggle Breakpoint | F9 | Add/remove breakpoint |
| Open Debug Console | ⌘+Shift+Y | Interactive Python console |

## Support

If you encounter issues:
1. Check the Output panel: "Alexa Skills Kit" channel
2. Check the Debug Console for Python errors
3. Review the integrated terminal for startup messages
4. Check ASK CLI configuration: `ask configure list`
