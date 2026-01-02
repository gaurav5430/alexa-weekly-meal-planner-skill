# Local Debugging Guide for Alexa Skill

## Overview
This guide explains how to sync your local skill with Alexa Developer Console and debug locally.

## Skill Information
- **Skill ID**: `amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746`
- **Skill Name**: Meal Planner
- **Lambda ARN**: Check your Alexa Console for the current Lambda function

---

## 1. Syncing Local and Remote

### One-Time Setup (Already Done ✅)
- ASK CLI is configured
- `ask-resources.json` updated with skill ID
- Skill linked to your local project

### Pull Latest from Alexa Console
```bash
./sync_skill.sh pull
```
This downloads:
- Skill manifest → `skill-package/skill.json`
- Interaction model → `skill-package/interactionModels/custom/en-US.json`

### Push Local Changes to Alexa Console
```bash
./sync_skill.sh push
```
This uploads your local:
- Skill manifest
- Interaction model

**Note**: Lambda code deployment is separate (see below)

### Check Skill Status
```bash
./sync_skill.sh status
```

---

## 2. Local Testing (Without Lambda Deployment)

### Option A: Text-Based Testing (Fastest)
Test intents directly without deploying to AWS:

```bash
# Run your existing text-based tests
python test_cli.py
```

Or test individual intents:
```python
python -c "
from tests.utils.text_to_intent import parse_text_to_intent
from src.lambda_function import lambda_handler

text = 'what is for dinner'
request = parse_text_to_intent(text)
response = lambda_handler(request, None)
print(response)
"
```

### Option B: Mock Alexa Requests
Use your existing mock testing:
```bash
python local_test/manual_test.py
```

### Option C: ASK Dialog (Interactive)
Test with simulated Alexa conversation:
```bash
ask dialog --locale en-US --skill-id amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746
```

---

## 3. VS Code Debugging

### Setup Python Debugger
Your `.vscode/launch.json` is already configured. To debug:

1. **Set breakpoints** in your code (e.g., in `src/lambda_function.py`)

2. **Run debug configuration**:
   - Press `F5` or go to Run → Start Debugging
   - Select "Python: Debug Alexa Skill"

3. **Invoke test**:
```bash
# In another terminal
python test_cli.py
```

The debugger will pause at your breakpoints.

---

## 4. Deploy Lambda Code to AWS

When you're ready to test on real Alexa devices: [DEPLOYMENT](../deployment/DEPLOYMENT_CONSOLE.md)

---

## 5. Testing on Real Alexa Device

After deploying Lambda code:

1. **Open Alexa Developer Console**: https://developer.amazon.com/alexa/console/ask
2. **Go to Test tab**
3. **Enable Testing** for Development stage
4. **Test via**:
   - Simulator: Type or speak utterances
   - Physical device: "Alexa, open weekly meal planner"

---

## 6. Common Workflows

### Making Interaction Model Changes
```bash
# 1. Edit locally
vim skill-package/interactionModels/custom/en-US.json

# 2. Push to Alexa
./sync_skill.sh push

# 3. Test
ask dialog --locale en-US --skill-id amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746
```

### Making Code Changes
```bash
# 1. Edit code
vim src/lambda_function.py

# 2. Test locally
python test_cli.py

# 3. Debug if needed (F5 in VS Code)

# 4. Deploy when ready
```

### Syncing After Console Changes
```bash
# Pull latest from console
./sync_skill.sh pull

# Review changes
git diff
```

---

## 7. Environment Variables

### Local Testing
Your Google Sheets credentials are in `credentials.json` - the code should pick this up automatically.

### AWS Lambda
Make sure your Lambda function has:
- **Environment variable**: `GOOGLE_CREDENTIALS` (with JSON content)
- **Permissions**: Appropriate IAM role

---

## Quick Reference

| Action | Command |
|--------|---------|
| Pull from console | `./sync_skill.sh pull` |
| Push to console | `./sync_skill.sh push` |
| Test locally | `python test_cli.py` |
| Debug in VS Code | `F5` |
| Deploy Lambda | `ask deploy --target lambda` |
| Interactive test | `ask dialog --locale en-US` |
| Check status | `./sync_skill.sh status` |

---

## Troubleshooting

### "Skill not found"
- Verify skill ID: `ask smapi list-skills-for-vendor`
- Check `ask-resources.json` has correct `skillId`

### "Permission denied" on sync_skill.sh
```bash
chmod +x sync_skill.sh
```

### Changes not reflecting
- After interaction model changes: Wait for build to complete
- After Lambda code changes: Ensure you deployed
- Clear Alexa app cache or use new utterance

### Google Sheets not working locally
- Check `credentials.json` exists
- Verify service account has access to your Google Sheet
- Check sheet ID in your code matches your actual sheet

---

## Next Steps

1. ✅ Run `./sync_skill.sh pull` to get latest from console
2. ✅ Test locally with `python test_cli.py`
3. ✅ Make code changes and debug with VS Code (F5)
4. ✅ Deploy when ready: `ask deploy --target lambda`
5. ✅ Test on real device

Happy debugging! 🎉
