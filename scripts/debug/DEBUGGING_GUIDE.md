# 🐛 VS Code Debugging Guide

## ✅ Setup Complete!

Your [.vscode/launch.json](.vscode/launch.json) is configured with **5 debugging options**:

---

## Publishing the skill to make it available in alexa devices / app
You don't need to publish the skill on alexa developer console, you can just keep it in development for your own personal usage. It would be available in "Your skills" in all the devices and apps which are logged in with the same email id.


## 🎯 Debugging Options

### Local debugging
debugging just the code, no need for ask cli or alexa developer console

#### 1. **Debug Local Test Script** ⭐ RECOMMENDED
**Best for**: Quick debugging with multiple test cases
This does not need the Alexa developer console at all

**How to use**:
1. Open [debug_skill.py](debug_skill.py)
2. Set breakpoints in your skill code (e.g., [src/lambda_function.py](src/lambda_function.py))
3. Press `F5` or click Run → "Debug Local Test Script"
4. Watch it test all intents and stop at your breakpoints!

**Example**:
- Set breakpoint at line 50 in [src/lambda_function.py](src/lambda_function.py)
- Press `F5`
- Debugger will pause when handling each intent

---

#### 2. **Debug Manual Test**
**Best for**: Testing specific scenarios you've written
This does not need the Alexa developer console at all

**How to use**:
1. Edit [local_test/manual_test.py](local_test/manual_test.py) with your test
2. Set breakpoints in skill code
3. Select "Debug Manual Test" from debug dropdown
4. Press `F5`

---

#### 3. **Debug E2E Tests**
**Best for**: Running your full test suite with debugging
This does not need the Alexa developer console at all

**How to use**:
1. Set breakpoints in skill code
2. Select "Debug E2E Tests" from debug dropdown
3. Press `F5`

---

#### 4. **Debug Current File**
**Best for**: Debugging any Python file you're working on
This does not need the Alexa developer console at all

**How to use**:
1. Open any `.py` file
2. Set breakpoints
3. Select "Debug Current File"
4. Press `F5`

---

### Remote debugging
[REMOTE DEBUG GUIDE](./REMOTE_DEBUG_GUIDE.md)

#### ASK CLI
Using ASK CLI and the ask sdk local debug, it would theoretically have been possible to create a tunnel from your local to the deployed skill, but it didn't work, somehow the Alexa development UI or the ask dialog command was never able to connect / send to the local debug. Anyway, if the local debugging was to work, these are the prerequisities:
- the skill should be in Development stage, to make sure debugging can happen. This is to be enabled on Skill -> Test -> drop down select to Development
- the `ask run` command needs a token which should have the `alexa::ask:skills:debug` scope. This can be created using `ask util generate-lwa-tokens --scopes alexa::ask:skills:debug`
- run the debugger in vscode, F5, it uses a local wrapper, and should log specific info regaring websoket connection failures, if any. This will help you understand if your creds are fine.
- IT is also important to make sure that the region is set to 'EU' , the default region for the skill, as well as your local code. But tried `ask run` with all different region combinations, wasn't able to make the local debugging work.
- The expectation after doing this is that the Alexa simulator on the alexa developer console as well as the `ask dialog` both would connect 
- (To use the ask cli, you would have done ask configure and other commands already)

#### VSCODE ASK Extension
I was not able to use the VSCODE Ask extension for debugging. The extension was not able to idenitfy the current skill , as well as wasn't helpful in even creating a new skill. the debug script did not work as well as it was not able to find the extensions' required variables. Now, we are using a debug script, which does not use the extension, but uses ask cli (indirectly for tokens) and other local scripts.

#### **Debug Alexa Skill (ASK Remote)** 🌐 (NOT WORKING AS EXPECTED)
**Best for**: Testing with real Alexa voice/simulator requests

**First-time setup**:
```bash
./setup_debug_creds.sh
```
This generates an access token and creates `.alexa-debug` file.

**How to use**:
1. Set breakpoints in your skill code
2. Select "Debug Alexa Skill (ASK Remote)"
3. Press `F5` → It will start local debugging server
4. In Alexa Developer Console Test tab:
   - Type or speak: "what's for dinner"
   - Or use your physical Alexa device
5. Your breakpoints will trigger when Alexa sends request!

**Note**: Access tokens expire after 1 hour. If debugging stops, re-run `./setup_debug_creds.sh`

---


### Device debugging
Once you deploy your extension to the alexa developer console in development mode, It would be available to all your alexa devices which are singed in with the same email id. 

- Make sure you are logged in with the same email Id on the alexa app / device with which you have hosted the alexa skill
- Make sure that you can find your skill in the "Your skills" section of the alexa app
- [IMPORTANT] Make sure that the locale / language of your device is set to one of the languages that the skill supports, otherwise it will lead to silent failures, where alexa would be able to identify your skill but would not be able to invoke it, and you would not be able to see any cloudwatch logs for these failures as the requests do not even reach the skill lambda. The only hint is that within the alexa app you would see "there was some problem with your skill" in Alexa history
- If the lambda was invoked, and then there were some errors, you would be able to see them in Cloudwatch logs, which can be accessed from the Code tab in developer console.



## 🚀 Quick Start: Your First Debug Session

### Step 1: Open Your Code
```bash
code lambda/lambda_function.py
```

### Step 2: Set a Breakpoint
- Click in the gutter (left of line numbers) at line 50 in `lambda_function.py`
- You'll see a red dot appear

### Step 3: Start Debugging
- Press `F5`
- Select "Debug Local Test Script"

### Step 4: Watch It Work!
- The script will run and pause at your breakpoint
- Inspect variables, step through code, etc.

---

## 🔍 Debugging Controls

| Key | Action |
|-----|--------|
| `F5` | Start/Continue |
| `F9` | Toggle breakpoint |
| `F10` | Step over |
| `F11` | Step into |
| `Shift+F11` | Step out |
| `Shift+F5` | Stop debugging |

---

## 📍 Common Breakpoint Locations

| File | Line Area | Why |
|------|-----------|-----|
| [lambda/lambda_function.py](lambda/lambda_function.py) | `lambda_handler` function | See every request |
| [lambda/handlers/intent_handlers.py](lambda/handlers/intent_handlers.py) | Intent handler functions | Debug specific intents |
| [lambda/services/sheets_service.py](lambda/services/sheets_service.py) | `get_meal` function | Debug Google Sheets calls |
| [lambda/services/meal_service.py](lambda/services/meal_service.py) | Business logic functions | Debug meal planning logic |

---

## 💡 Pro Tips

### Tip 1: Conditional Breakpoints
Right-click breakpoint → Edit Breakpoint → Add condition
```python
meal_type == "dinner"
```

### Tip 2: Debug Console
While paused, use Debug Console to run Python code:
```python
>>> meal_type
'dinner'
>>> response
{...}
```

### Tip 3: Watch Variables
Add variables to Watch panel to track them across execution

### Tip 4: Quick Test Loop
1. Set breakpoints
2. Press `F5`
3. Make changes while paused
4. Restart debugger (`Ctrl+Shift+F5`)
5. Repeat!

---

## 🧪 Testing Workflow

### For Quick Tests (No Alexa needed)
```
Edit code → Set breakpoint → F5 → Fix → Repeat
```

### For Real Alexa Testing
```
Edit code → Test locally (F5) → Deploy → Test on device
```

---

## 📝 Example: Debug a Specific Intent

Let's debug the "GetMealIntent":

1. **Open** [src/handlers/intent_handlers.py](src/handlers/intent_handlers.py)

2. **Find** the `handle_get_meal_intent` function

3. **Set breakpoint** on the first line of the function

4. **Edit** [debug_skill.py](debug_skill.py) to only test dinner:
```python
def main():
    request = create_intent_request('GetMealIntent', {
        'MealType': {'name': 'MealType', 'value': 'dinner'}
    })
    response = lambda_handler(request, None)
    print(response)
```

5. **Press** `F5` → Select "Debug Local Test Script"

6. **Debugger pauses** → Inspect `meal_type`, `meal_data`, etc.

7. **Step through** with `F10` to see each line execute

---

## ❓ Troubleshooting

### "No module named 'ask_sdk_core'"
```bash
.venv/bin/pip install -r requirements.txt
```

### Breakpoint not hit
- Check you selected the right debug configuration
- Verify code path is actually executed
- Check PYTHONPATH is set correctly (should be automatic)

### Can't see variables
- Make sure you're paused at a breakpoint
- Check variable is in current scope

### "Access token" error (for ASK Remote debugging)
- Install ASK Toolkit extension
- Sign in to Amazon Developer account
- Or use local debugging options instead

---

## 🎯 Recommended Daily Workflow

**Morning coding session**:
1. Open VS Code
2. Run `./sync_skill.sh pull` to get latest
3. Set breakpoints in area you're working on
4. Press `F5` → Debug Local Test Script
5. Make changes, re-run with `Ctrl+Shift+F5`

**Ready to test on Alexa**:
1. All local tests passing
2. Run `./sync_skill.sh push`
3. Deploy: `ask deploy --target lambda`
4. Test on device or simulator

---

## 🎉 You're Ready!

Press `F5` and start debugging! 🐛✨
