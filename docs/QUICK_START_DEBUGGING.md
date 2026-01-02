# VS Code Debugging Setup - Quick Start

Since you don't have a skill created yet, here are the **simplest options** to get started with debugging:

## Option 1: Create Skill via Alexa Developer Console (Easiest)

1. **Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)**

2. **Click "Create Skill"**
   - Skill name: `Weekly Meal Planner`
   - Primary locale: `English (US)`
   - Type: `Custom`
   - Hosting: `Provision your own`
   - Click **Create skill**

3. **Choose a template**: `Start from Scratch`

4. **Copy your Skill ID** from the top of the page (starts with `amzn1.ask.skill...`)

5. **Import the interaction model**:
   - In the left sidebar, click `JSON Editor`
   - Copy the contents from `skill-package/interactionModels/custom/en-US.json`
   - Paste into the editor
   - Click **Save Model** then **Build Model**

6. **Configure endpoint** (Test tab):
   - Go to **Test** tab at the top
   - Enable testing: Change dropdown from "Off" to "Development"
   - You can now test with the simulator!

7. **Start debugging in VS Code**:
   - Copy the **access token** from earlier (or generate a new one):
     ```bash
     ask util generate-lwa-tokens --no-browser
     ```
   - Press **F5** in VS Code
   - Paste the access token when prompted
   - Paste your Skill ID when prompted
   - Set breakpoints in your code
   - Test in the Alexa Simulator in browser

## Option 2: Test Locally Without Alexa Service (No Skill ID needed)

You can test your Lambda function directly without connecting to Alexa:

### Create a simple test script:

```python
# test_local_debug.py
import json
from src.lambda_function import lambda_handler

# Sample Alexa request
event = {
    "version": "1.0",
    "session": {
        "new": True,
        "sessionId": "test-session",
        "application": {"applicationId": "test-app"},
        "user": {"userId": "test-user"}
    },
    "request": {
        "type": "IntentRequest",
        "requestId": "test-request",
        "intent": {
            "name": "GetMealIntent",
            "slots": {
                "MealType": {
                    "name": "MealType",
                    "value": "dinner"
                },
                "RelativeDay": {
                    "name": "RelativeDay",
                    "value": "today"
                }
            }
        }
    }
}

# Call your handler
response = lambda_handler(event, None)
print(json.dumps(response, indent=2))
```

### Run with debugging:
1. Open `test_local_debug.py` in VS Code
2. Set breakpoints in your intent handlers
3. Press **F5** and select **Python: Current File**
4. Step through your code!

## Your Current Credentials

**Access Token** (expires in 1 hour):
```
Atza|gQAxXNh-AwEBAPCXo2iqk_uQSThDySAAhfTGkoH1do1X8xmmNDq3L3uiQCTKFR8cKAOxj_bkbINMOcWoUzlA25q6WoLMX5c2a7cEI1BxuUnPFKYWSPms9n9GAdvdMmju8DDzpaZ9vF0ZRBYuQztUKrcsv_P5DM6RZWINIGynPh_g4C3wH6fSB5JJ421VOLMlWxvl7ctIP0tyfFMKyfbVS-0ETEN3E0NBlTkQ09mAYTzKXRiuR2b5m7QTr6lvB2QWl_85oMfWRtf9raSgErVTidHD60vdpFu77-8kWK4FJRVEDiCmhpOBgEO7Cdednu2RO2xK5yk0xtzVmJzluabXgXILM61_AHnEhF6IkhREYPMASkBmwLNiiDGjAAr_MkNZiisN7C6wnX7UKJ9M1wkSKwy-iFJ3cN-9E6PvfkzaPkbZWVNCQYPGwzVM3Cv6kuw7zbaHa81pjdr3fvPjz3_ws1XwJUZj5-V8kuDOGDkVBF9pu4p2rfTRT9puLLdev6ln2KLJWzdiUy2TlTYgM0UZs6NCVVI_WGFw1rDO-ohACufHkP6HBqjUqZe7nDZGFQBWt0dAoebFTsAAr6DNSYyuOtk_5cO32NBMREoxB6MIfijEifG9im7NqK5vH30Zxho1acYO2wPgJsH2zFbqmQKvPbLvTDEpz68D1jF0pF0mU3GiV9AjCkAoKtlZd__gip4DmSJ1lLhIMPzW0Ve_rSrA6CoytkicYbQspXXP8a6NrJs4UhQ8FspdyQROYTPClN7kTLad3pji
```

**Refresh this token when it expires:**
```bash
ask util generate-lwa-tokens --no-browser
```

**Vendor ID:** `M4GQE8JH9X551`

## Recommendation

**Go with Option 1** - it takes 5 minutes and gives you the full Alexa testing experience with voice simulator, session management, and real Alexa request/response handling.

Once you have your Skill ID, debugging is as simple as pressing **F5**!
