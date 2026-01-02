# Alexa Developer Console Deployment Guide

This guide explains how to deploy your Alexa skill through the Alexa Developer Console UI.

## Project Structure

Our Alexa skill is a combination of two things: the business logic /code and the interaction model.

The code resides in the `lambda` folder, is written in pyhton
The interaction model is a json with all the configured intents and invocation info. It is inside the `skill-package` folder

If you make any changes to the interaction model, you can use the `sync_skill` script which uses ask CLI to sync it with alexa developer console. In case that does not work, you can also manually copy paste the json.

If you make any changes to the code inside the `lambda` folder, you can run the deployment package script, and import the created zip folder in the developer console ui under skill -> code -> import 

The project is organized for Developer Console deployment:

```
alexa-skill-weekly-menu/
├── skill-package/              # Skill configuration
│   ├── skill.json             # Skill manifest
│   └── interactionModels/
│       └── custom/
│           └── en-US.json     # Interaction model
│
└── lambda/                     # Lambda function code
    ├── lambda_function.py     # Main handler
    ├── requirements.txt       # Python dependencies
    ├── credentials.json       # Google Sheets credentials
    ├── config/                # Configuration files
    ├── handlers/              # Intent handlers
    ├── models/                # Data models
    ├── services/              # Business logic
    └── utils/                 # Utility functions
```

## Deployment Steps

### 1. Deploy the Skill Configuration

1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click on your skill or create a new one
3. Go to the **Build** tab
4. Click **JSON Editor** in the left sidebar
5. Copy the contents of `skill-package/interactionModels/custom/en-US.json`
6. Paste into the JSON Editor
7. Click **Save Model** and then **Build Model**

### 2. Deploy the Lambda code to Alexa hosted lambda

#### Option A: Upload ZIP (Recommended for first deployment)

1. Create a deployment package:
   ```bash
   ./scripts/deployment/create-deployment-package.sh
   ```

2. Go to [Alexa developer console](https://developer.amazon.com/alexa/console/ask), inside your skill
3. Under **Code** section, click **Import from** → **.zip file**
4. Upload `lambda-deployment.zip`
5. Add environment variables:
   - `GOOGLE_SHEET_ID`: Your Google Sheet ID
   - `WORKSHEET_NAME`: Sheet name (default: Sheet1)
6. Click Deploy in the code tab

#### Option B: Inline Code Editor (For small updates)

1. Go to your Lambda function in AWS Console
2. Update individual files through the inline editor
3. Save your changes
4. Deploy from the code tab

### 5. Test Your Skill

1. Go to the **Test** tab in Alexa Developer Console
2. Enable testing for "Development"
3. Type or speak test utterances like:
   - "open weekly menu"
   - "what's for dinner tonight"
   - "what are we eating today"

## Environment Variables Required

Make sure these environment variables are set in your Lambda function:

- `GOOGLE_SHEET_ID`: Your Google Sheets ID
- `WORKSHEET_NAME`: Name of the worksheet (default: Sheet1)
- `CREDENTIALS_PATH`: Path to credentials.json (default: credentials.json)

## Important Notes

- The `credentials.json` file must be included in your Lambda deployment package
- Make sure all dependencies are installed in the lambda folder before zipping

## Troubleshooting

### Import Errors
- Some dependencies which are implicit in local environment need to be explicitly added in the lambda environment, for e.g "requests" . In case your code breaks due to any of these, you will be able to see cloudwatch logs mentioning the error. Cloudwatch logs are accessible from Code -> Cloudwatch logs

### Credentials Not Found
- Verify `credentials.json` is in the lambda folder
- Check the `CREDENTIALS_PATH` environment variable

