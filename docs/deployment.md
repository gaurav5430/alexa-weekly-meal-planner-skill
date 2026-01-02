# Deployment Guide - Alexa-Hosted Skills (Recommended)

**Updated per NFR-001**: This skill is designed for Alexa-hosted infrastructure, which provides free hosting and requires no AWS account.

## Overview

Alexa-hosted skills provide:
- **Free hosting** - No AWS account needed
- **Automatic deployment** - Code updates deploy automatically
- **Built-in storage** - For small files like credentials
- **Zero configuration** - Amazon manages infrastructure

For advanced users who prefer AWS Lambda, see [AWS Lambda Deployment](#alternative-aws-lambda-deployment) below.

---

## Alexa-Hosted Deployment (Recommended)

### Prerequisites

- Alexa Developer Console account (free)
- Google Sheets API credentials (service account JSON file)
- Your meal plan Google Sheet

### Step 1: Create Alexa-Hosted Skill

1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click "Create Skill"
3. Enter skill name: **Weekly Meal Planner**
4. Choose language: **English (US)** (or your preference)
5. Choose model: **Custom**
6. Choose hosting: **Alexa-Hosted (Python)**
7. Click "Create skill"

### Step 2: Upload Interaction Model

1. In the Alexa Developer Console, go to **Build** tab
2. Click **Interaction Model** > **JSON Editor**
3. Copy the contents of `skill-package/interactionModels/custom/en-US.json` from this repository
4. Paste into the JSON Editor
5. Click **Save Model**
6. Click **Build Model** (wait for build to complete)

### Step 3: Deploy Code to Alexa-Hosted Backend

#### Option A: Via Alexa Developer Console (Web IDE)

1. Go to **Code** tab in Alexa Developer Console
2. You'll see a web-based code editor with these files:
   - `lambda/lambda_function.py`
   - `lambda/requirements.txt`
   - Other default files

3. **Replace `lambda_function.py`**:
   - Delete the default content
   - Copy entire contents of `src/lambda_function.py` from this repo
   - Also copy all other files from `src/` directory:
     - Create folders: `config/`, `handlers/`, `models/`, `services/`, `utils/`
     - Upload all Python files to respective folders

4. **Update `requirements.txt`**:
   - Replace with contents from this repo's `requirements.txt`:
   ```
   ask-sdk-core==1.19.0
   gspread==5.12.0
   oauth2client==4.1.3
   pytz==2024.1
   ```

5. **Upload Google Sheets Credentials**:
   - In the Code editor, create a new file: `credentials.json`
   - Paste your Google service account credentials
   - **IMPORTANT**: This file will be stored securely in Alexa-hosted backend

6. **Set Environment Variables** (if not using default paths):
   - The skill expects these environment variables (can be set in code or via console):
     - `GOOGLE_SHEET_ID`: Your Google Sheet ID
     - `WORKSHEET_NAME`: "Weekly Meal Plan" (default)
     - `CREDENTIALS_PATH`: "./credentials.json" (default)
   
   - To set in Alexa Console, there's no UI for env vars, so hardcode in `src/config/settings.py` or use defaults

7. Click **Save** then **Deploy**

#### Option B: Via Git (Advanced)

#### Option B: Via Git (Advanced)

Alexa-hosted skills provide a Git repository:

1. In **Code** tab, click **Export Code**
2. Copy the Git repository URL
3. Clone locally:
   ```bash
   git clone <alexa-hosted-git-url>
   cd <repo-name>
   ```

4. Copy project files:
   ```bash
   # Copy source code to lambda/ directory
   cp -r /path/to/your/project/src/* lambda/
   
   # Copy requirements.txt
   cp /path/to/your/project/requirements.txt lambda/
   
   # Copy credentials
   cp /path/to/your/credentials.json lambda/
   ```

5. Commit and push:
   ```bash
   git add .
   git commit -m "Deploy Weekly Meal Planner skill"
   git push origin master
   ```

6. The skill will auto-deploy (check **Code** tab for deployment status)

### Step 4: Configure Skill Settings

1. Go to **Build** > **Invocation**
2. Set invocation name: **weekly meal planner**
3. Go to **Build** > **Intents**
4. Verify all intents are loaded from the JSON model:
   - `GetMealIntent`
   - `GetTodayMealsIntent`
   - `GetSpecificDayMealIntent`
   - `GetNextMealIntent`
   - `RefreshMealPlanIntent`
   - Built-in intents (Help, Cancel, Stop, Fallback)

### Step 5: Test the Skill

1. Go to **Test** tab
2. Enable testing: Select **Development**
3. Try these commands:
   - "Open weekly meal planner"
   - "What's for dinner?"
   - "What should I cook today?"
   - "What's for lunch on Friday?"
   - "What's the next meal?"
   - "Refresh my meal plan"

### Step 6: Update Google Sheet Configuration

Before the skill works, ensure:

1. **Google Sheet Setup**:
   - Sheet structure matches expected format (see `quickstart.md`)
   - Headers: Day, Breakfast, Morning Snack, Lunch, Evening Snack, Dinner
   - 7 rows for Monday-Sunday

2. **Service Account Access**:
   - Share your Google Sheet with the service account email
   - Grant "Editor" or "Viewer" permissions
   - Service account email is in your `credentials.json` file

3. **Update Sheet ID in Code**:
   - Open `lambda/src/config/settings.py` in Code editor
   - Update `GOOGLE_SHEET_ID` with your sheet ID
   - Or set as environment variable (see configuration below)

### Step 7: Monitor and Debug

**View Logs**:
1. In **Code** tab, click **Logs** at bottom
2. Or go to Amazon CloudWatch (automatically configured)
3. Check for errors in skill invocation

**Common Issues**:
- **"Credentials not found"**: Ensure `credentials.json` is in `lambda/` directory
- **"Sheet access denied"**: Share sheet with service account email
- **"Invalid sheet structure"**: Check headers and day names

---

## Configuration Options

### Environment Variables (Optional)

If you need to override defaults, edit `lambda/src/config/settings.py`:

```python
import os

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', 'your-default-sheet-id')
WORKSHEET_NAME = os.getenv('WORKSHEET_NAME', 'Weekly Meal Plan')
CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH', './credentials.json')
```

### Cache Configuration

The skill uses a 24-hour cache (per FR-016):
- Cache automatically refreshes after 24 hours
- Use "refresh my meal plan" voice command to manually refresh
- Cache persists across Lambda invocations (global variable)

### Timezone Support

The skill extracts device timezone from Alexa request (per NFR-006):
- Automatically uses user's device timezone
- Falls back to Eastern Time if not available
- Ensures accurate "what's next" meal calculations

---

## Updating the Skill

### Update Code

**Via Web IDE**:
1. Go to **Code** tab
2. Edit files directly
3. Click **Save**
4. Click **Deploy**

**Via Git**:
```bash
# Make changes locally
git add .
git commit -m "Update skill logic"
git push origin master
```

### Update Interaction Model

1. Go to **Build** > **Interaction Model** > **JSON Editor**
2. Make changes
3. Click **Save Model**
4. Click **Build Model**

---

## Publishing the Skill (Optional)

To make your skill available to others:

1. Go to **Distribution** tab
2. Fill out skill details:
   - Public name
   - Description
   - Example phrases
   - Icons (512x512 and 108x108)
   - Category: Lifestyle or Food & Drink
   - Keywords
   - Privacy policy URL (if collecting data)

3. Go to **Certification** tab
4. Complete certification testing
5. Submit for review

**Note**: For private/personal use, you don't need to publish. The skill works in Development mode on your account.

---

## Alternative: AWS Lambda Deployment

<details>
<summary>Click to expand AWS Lambda instructions (advanced users)</summary>
If you prefer to host on your own AWS account instead of using Alexa-hosted infrastructure:

### Prerequisites
- AWS Account with Lambda access
- AWS CLI configured locally
- Alexa Developer Console access

### Step 1: Create Lambda Function

```bash
# Package dependencies
cd /tmp/lambda-package
pip install -r /path/to/requirements.txt -t .
cp -r /path/to/src .
cp /path/to/credentials.json .

# Create ZIP
zip -r lambda-package.zip .

# Create Lambda function
aws lambda create-function \
  --function-name weekly-meal-planner \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler src.lambda_function.lambda_handler \
  --zip-file fileb://lambda-package.zip \
  --timeout 10 \
  --memory-size 256 \
  --environment "Variables={GOOGLE_SHEET_ID=YOUR_SHEET_ID}"
```

### Step 2: Configure Alexa Skill Trigger

```bash
aws lambda add-permission \
  --function-name weekly-meal-planner \
  --statement-id alexa-skill-trigger \
  --action lambda:InvokeFunction \
  --principal alexa-appkit.amazonaws.com \
  --event-source-token YOUR_SKILL_ID
```

### Step 3: Link to Alexa Skill

1. In Alexa Developer Console, go to **Build** > **Endpoint**
2. Select **AWS Lambda ARN**
3. Paste Lambda ARN: `arn:aws:lambda:REGION:ACCOUNT_ID:function:weekly-meal-planner`
4. Save

### Updating Code

```bash
# Update function code
aws lambda update-function-code \
  --function-name weekly-meal-planner \
  --zip-file fileb://lambda-package.zip
```

**Costs**: ~$0.20/month for typical usage

</details>

---

## Troubleshooting

### Skill Not Responding

1. Check **Code** tab logs for errors
2. Verify `credentials.json` is uploaded
3. Test sheet access manually
4. Ensure interaction model is built

### "Sheet access denied"

1. Get service account email from `credentials.json`
2. Share Google Sheet with that email
3. Grant Editor or Viewer permissions

### "Cache not refreshing"

- Wait 24 hours for automatic refresh
- Or say "refresh my meal plan" to force refresh
- Check CloudWatch logs for cache timestamps

### Invalid Responses

1. Verify sheet structure (headers, day names)
2. Check for empty cells
3. Ensure timezone is set correctly

---

## Next Steps

- **Test on Alexa device**: Link your Amazon account and test on Echo
- **Customize responses**: Edit `response_builder.py` to personalize SSML
- **Add more features**: Create new intents for recipes, shopping lists, etc.
- **Monitor usage**: Check analytics in Alexa Developer Console

---

## Support

- **Logs**: Check Code tab > Logs or CloudWatch
- **Documentation**: See `quickstart.md` for setup guide
- **Issues**: Open GitHub issue for bugs or questions

---

## Summary

✅ **Recommended**: Use Alexa-hosted deployment (free, easy)  
⚙️ **Advanced**: Use AWS Lambda (more control, costs apply)  
📱 **Testing**: Always test in Development mode first  
🔄 **Updates**: Deploy via Code tab or Git push  
📊 **Monitoring**: Use CloudWatch logs for debugging