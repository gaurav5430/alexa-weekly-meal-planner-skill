# 🎉 Local Debugging is Ready!

## ✅ What's Been Set Up

### 1. **VS Code Launch Configurations** ([.vscode/launch.json](.vscode/launch.json))
   - ✅ Debug Local Test Script (recommended)
   - ✅ Debug Manual Test
   - ✅ Debug E2E Tests
   - ✅ Debug Current File
   - ✅ Debug Alexa Skill (ASK Remote)

### 2. **VS Code Tasks** ([.vscode/tasks.json](.vscode/tasks.json))
   - ✅ Run Debug Script
   - ✅ Run CLI Tests
   - ✅ Pull from Alexa Console
   - ✅ Push to Alexa Console
   - ✅ Deploy Lambda to AWS

### 3. **Helper Scripts**
   - ✅ [debug_skill.py](debug_skill.py) - Comprehensive test script
   - ✅ [sync_skill.sh](sync_skill.sh) - Sync with Alexa Console

### 4. **Documentation**
   - ✅ [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) - Complete debugging guide
   - ✅ [.vscode/SHORTCUTS.md](.vscode/SHORTCUTS.md) - Keyboard shortcuts
   - ✅ [SYNC_QUICK_START.md](SYNC_QUICK_START.md) - Quick reference

---

## 🚀 Start Debugging in 3 Steps

### Step 1: Set a Breakpoint
Open [src/lambda_function.py](src/lambda_function.py) and click in the gutter (left of line numbers) at line 50.

### Step 2: Press F5
Select **"Debug Local Test Script"** from the dropdown.

### Step 3: Watch It Work!
The debugger will:
- Run tests for all intents
- Pause at your breakpoints
- Let you inspect variables
- Step through your code

---

## 🎯 Common Tasks

| What You Want | What to Do |
|---------------|------------|
| **Test code changes quickly** | Press `F5` → "Debug Local Test Script" |
| **Test specific scenario** | Edit [debug_skill.py](debug_skill.py) → Press `F5` |
| **Pull latest from Console** | Terminal → Run Task → "Pull from Alexa Console" |
| **Push your changes** | Terminal → Run Task → "Push to Alexa Console" |
| **Deploy to AWS** | Terminal → Run Task → "Deploy Lambda to AWS" |
| **Test with real Alexa** | Press `F5` → "Debug Alexa Skill (ASK Remote)" |

---

## 📖 Quick Reference

### Debugging Keyboard Shortcuts
- `F5` - Start debugging
- `F9` - Toggle breakpoint
- `F10` - Step over
- `F11` - Step into
- `Shift+F5` - Stop debugging

### Run Tasks
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Run Task"
3. Select the task you want

---

## 💡 Pro Tips

### Tip 1: Quick Test Loop
```
Set breakpoint → F5 → Inspect → Fix code → Ctrl+Shift+F5 (restart) → Repeat
```

### Tip 2: Test Just One Intent
Edit [debug_skill.py](debug_skill.py) to call only the function you want:
```python
def main():
    test_get_meal_intent()  # Just test this one
```

### Tip 3: Use Conditional Breakpoints
Right-click a breakpoint → Edit Breakpoint → Add condition:
```python
meal_type == "dinner"
```

### Tip 4: Debug Console
While paused, use Debug Console to run Python commands:
```python
>>> meal_type
'dinner'
>>> len(meals)
5
```

---

## 🧪 Example Debugging Session

Let's debug the GetMealIntent:

```bash
# 1. Open the handler file
code src/handlers/intent_handlers.py

# 2. Find handle_get_meal_intent function
# 3. Click in gutter to set breakpoint
# 4. Press F5
# 5. Select "Debug Local Test Script"
# 6. When it pauses:
#    - Inspect meal_type variable
#    - Check meal_data
#    - Step through with F10
# 7. Make changes if needed
# 8. Restart with Ctrl+Shift+F5
```

---

## 🔄 Daily Workflow

### Morning
```bash
./sync_skill.sh pull    # Get latest from Console
git status              # Check local changes
```

### Coding
```
Edit code → F5 → Debug → Fix → Repeat
```

### Ready to Deploy
```bash
./sync_skill.sh push              # Upload skill config
ask deploy --target lambda        # Deploy code to AWS
```

### Test on Device
```
Alexa, open weekly meal planner
What's for dinner?
```

### Setup Remote Debugging (First Time)
```bash
./setup_debug_creds.sh           # Generate access token for ASK remote debugging
```

---

## 📚 Documentation

- **[DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md)** - Detailed debugging instructions
- **[SYNC_QUICK_START.md](SYNC_QUICK_START.md)** - Sync and testing guide  
- **[.vscode/SHORTCUTS.md](.vscode/SHORTCUTS.md)** - Keyboard shortcuts
- **[LOCAL_DEBUG_GUIDE.md](LOCAL_DEBUG_GUIDE.md)** - Comprehensive local testing

---

## ❓ Troubleshooting

### Breakpoint Not Hit
- Verify you selected the right debug configuration
- Check the code path is executed
- Try adding a print statement to verify

### Import Errors
```bash
.venv/bin/pip install -r requirements.txt
```

### Can't See Variables
- Make sure debugger is paused
- Check you're looking at the right scope

---

## 🎉 You're All Set!

**Press F5 now to start your first debugging session!** 🐛✨

For detailed instructions, see [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md)
