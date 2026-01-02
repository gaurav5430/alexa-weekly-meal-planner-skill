# ASK Remote Debugging Setup [NOT WORKING AS EXPECTED]

## Overview

The "Debug Alexa Skill (ASK Remote)" configuration allows you to debug your skill with **real Alexa requests** from:
- Alexa Developer Console Test Simulator
- Physical Alexa devices
- Alexa mobile app

When you trigger your skill, the request goes to your local VS Code debugger instead of AWS Lambda!

---

## Quick Setup (3 Steps)

### Step 1: Generate Credentials
```bash
./setup_debug_creds.sh
```

This creates `.alexa-debug` file with:
- Access token (valid for 1 hour)
- Skill ID
- Region

### Step 2: Start Debugging
1. Set breakpoints in your code
2. Press `F5`
3. Select **"Debug Alexa Skill (ASK Remote)"**

You'll see:
```
Alexa Skill Local Debug Wrapper
========================================
Skill ID: amzn1.ask.skill.e19ca2d0...
Region: NA
Token: Atza|gQD8z0nCAwEBABv... (truncated)

Creating LocalDebuggerInvoker...
Starting WebSocket connection...
Keep this running and test your skill in the Alexa Developer Console
```

### Step 3: Test Your Skill
Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask) > Your Skill > Test tab

Enable testing and say:
- "Alexa, open weekly meal planner"
- "What's for dinner?"

Your breakpoints will trigger! 🎉

---

## Files

| File | Purpose |
|------|---------|
| `.alexa-debug` | Your credentials (git-ignored) |
| `.alexa-debug.template` | Template for credentials file |
| `debug_wrapper.py` | Loads credentials and starts debugger |
| `setup_debug_creds.sh` | Helper script to generate credentials |

---

## Troubleshooting

### "ERROR: .alexa-debug not found!"
Run: `./setup_debug_creds.sh`

### Debugging Suddenly Stops Working
Access tokens expire after 1 hour. Regenerate:
```bash
./setup_debug_creds.sh
```

### "Connection refused" or "WebSocket error"
1. Check your internet connection
2. Verify skill ID is correct in `.alexa-debug`
3. Regenerate access token: `./setup_debug_creds.sh`

### Breakpoints Don't Trigger
1. Make sure debugger is running (check Debug Console)
2. Verify "Development" is enabled in Alexa Test tab
3. Check that requests are actually being sent (look for JSON in console)

---

## Manual Setup (Alternative)

If the script doesn't work, create `.alexa-debug` manually:

### 1. Generate Access Token
```bash
ask util generate-lwa-tokens --no-browser --scopes alexa::ask:skills:debug
```

Copy the access token (starts with `Atza|...`)

### 2. Create .alexa-debug
```bash
cat > .alexa-debug << EOF
ACCESS_TOKEN=Atza|your_token_here
SKILL_ID=amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746
REGION=NA
EOF
```

### 3. Start Debugging
Press `F5` → Select "Debug Alexa Skill (ASK Remote)"

---

## How It Works

```
Alexa Device/Simulator
        ↓
   [Your Request]
        ↓
Alexa Service (AWS)
        ↓
   [WebSocket]
        ↓
debug_wrapper.py (reads .alexa-debug)
        ↓
Your Local Code (with breakpoints!)
        ↓
   [Response]
        ↓
Alexa Device/Simulator
```

---

## Tips

### Keep Token Fresh
Set a reminder to regenerate every hour if debugging for extended periods.

### Multiple Sessions
You can only have ONE debugger connected at a time. Stop any running debug sessions before starting a new one.

### Use with Physical Devices
Make sure your Amazon account is the same one used for:
- Alexa Developer Console
- Physical Alexa devices
- ASK CLI login

### Quick Restart
If you need to restart:
1. Stop debugger (`Shift+F5`)
2. Wait 5 seconds
3. Start again (`F5`)

---

## Next Steps

1. Run `./setup_debug_creds.sh`
2. Press `F5` → Select "Debug Alexa Skill (ASK Remote)"
3. Test in Alexa Console
4. Watch your breakpoints trigger! 🚀

For more debugging options, see [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md)
