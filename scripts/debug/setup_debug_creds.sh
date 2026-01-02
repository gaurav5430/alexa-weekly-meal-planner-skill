#!/bin/bash

# Setup script for Alexa remote debugging credentials

set -e

CREDS_FILE=".alexa-debug"
TEMPLATE_FILE=".alexa-debug.template"

echo "================================================"
echo "Alexa Skill Remote Debug Setup"
echo "================================================"
echo ""

# Check if credentials file already exists
if [ -f "$CREDS_FILE" ]; then
    echo "⚠️  $CREDS_FILE already exists!"
    read -p "Do you want to regenerate it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing credentials file."
        exit 0
    fi
fi

echo "Step 1: Generating access token..."
echo "This will open a browser for you to authenticate."
echo ""

# Generate token
TOKEN_OUTPUT=$(ask util generate-lwa-tokens --no-browser 2>&1)

# Extract access token from output
ACCESS_TOKEN=$(echo "$TOKEN_OUTPUT" | grep -o 'Atza|[^"]*' | head -1)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to generate access token!"
    echo ""
    echo "Please run manually:"
    echo "  ask util generate-lwa-tokens --no-browser"
    echo ""
    echo "Then copy the token and paste it into $CREDS_FILE"
    echo "Use $TEMPLATE_FILE as a template."
    exit 1
fi

echo "✅ Access token generated!"
echo ""

# Create credentials file
echo "Step 2: Creating $CREDS_FILE..."

cat > "$CREDS_FILE" << EOF
# Alexa Skill Local Debug Credentials
# Generated on $(date)
# DO NOT commit this file to git

ACCESS_TOKEN=$ACCESS_TOKEN
SKILL_ID=amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746
REGION=NA
EOF

echo "✅ Credentials file created!"
echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "You can now use the 'Debug Alexa Skill (ASK Remote)' configuration."
echo ""
echo "To start debugging:"
echo "  1. Press F5 in VS Code"
echo "  2. Select 'Debug Alexa Skill (ASK Remote)'"
echo "  3. Go to Alexa Developer Console > Test tab"
echo "  4. Test your skill - breakpoints will trigger!"
echo ""
echo "Note: Access tokens expire after 1 hour."
echo "If debugging stops working, re-run this script."
echo ""
