# 🎯 Quick Start: Sync & Debug Your Alexa Skill

## ✅ Setup Complete!

Your local skill is now linked to Alexa Console skill:
- **Skill ID**: `amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746`
- **Skill Name**: Meal Planner

---

## 🔄 Daily Workflow

### 1. Sync from Alexa Console → Local
```bash
./sync_skill.sh pull
```
Downloads latest skill manifest and interaction model to your local files.

### 2. Make Changes Locally
Edit files in `skill-package/` or `lambda/`

### 3. Test Locally
```bash
# Quick CLI test
.venv/bin/python test_cli.py

# Or test specific intent
.venv/bin/python -c "
from tests.utils.text_to_intent import parse_text_to_intent
from src.lambda_function import lambda_handler

text = 'what is for dinner'
request = parse_text_to_intent(text)
response = lambda_handler(request, None)
print(response)
"
```

### 4. Debug in VS Code
- Set breakpoints in your code
- Press `F5` to start debugging
- Run tests in terminal while debugging

### 5. Sync Local → Alexa Console
```bash
./sync_skill.sh push
```
Uploads your skill configuration changes.

### 6. Deploy Lambda Code (when ready)
[DEPLOYMENT](../deployment/DEPLOYMENT_CONSOLE.md)

---

## 🐛 Debugging Options

| Method | When to Use | Command |
|--------|-------------|---------|
| **VS Code debugger** | Step through code | Press `F5` → "Debug Local Test Script" |
| **Text-based** | Fastest iteration | `.venv/bin/python test_cli.py` |
| **Debug script** | Quick test all intents | `.venv/bin/python scripts/debug/debug_skill.py` |
| **ASK Dialog** | Simulate conversation | `ask dialog --locale en-US` |
| **Alexa Simulator** | Full UI testing | Visit Alexa Console > Test |
| **Real device** | Final testing | After deploying Lambda |

[DEBUGGING](../local_debug/DEBUGGING_GUIDE.md)

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `ask-resources.json` | Links local ↔ remote skill |
| `skill-package/skill.json` | Skill metadata |
| `skill-package/interactionModels/custom/en-US.json` | Intents, slots, utterances |
| `lambda/lambda_function.py` | Your skill logic |
| `credentials.json` | Google Sheets access |

---

## ⚡ Quick Commands

```bash
# Check what changed in console
./sync_skill.sh pull && git diff

# Test locally
.venv/bin/python test_cli.py

# Push your changes
./sync_skill.sh push

# Interactive testing (NOT WORKING AS EXPECTED)
ask dialog --locale en-US --skill-id amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746
```

---

## 🔍 Verify Sync Status

```bash
./sync_skill.sh status
```

---

## 📚 More Details

See [LOCAL_DEBUG_GUIDE.md](LOCAL_DEBUG_GUIDE.md) for comprehensive documentation.

---

## 🎉 You're All Set!

Your local and remote skills are now synced. Start coding and testing locally! 🚀
