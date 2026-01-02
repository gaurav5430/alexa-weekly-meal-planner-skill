#!/bin/bash

# Sync script for Alexa Skill
# This script helps sync between local and remote Alexa skill

set -e

SKILL_ID="amzn1.ask.skill.e19ca2d0-3c60-433d-a0c3-2fdd8a609746"

echo "========================================="
echo "Alexa Skill Sync Script"
echo "========================================="
echo ""

# Function to pull from remote
pull_from_remote() {
    echo "📥 Pulling latest from Alexa Developer Console..."
    
    # Pull skill manifest
    echo "  - Fetching skill manifest..."
    ask smapi get-skill-manifest -s $SKILL_ID -g development > skill-package/skill.json
    
    # Pull interaction model
    echo "  - Fetching interaction model (en-US)..."
    ask smapi get-interaction-model -s $SKILL_ID -l en-US -g development > skill-package/interactionModels/custom/en-US.json
    # also pull interaction models for en-IN
    ask smapi get-interaction-model -s $SKILL_ID -l en-IN -g development > skill-package/interactionModels/custom/en-IN.json
    echo "✅ Pull complete!"
}

# Function to push to remote
push_to_remote() {
    echo "📤 Pushing local changes to Alexa Developer Console..."
    
    # Update skill manifest
    echo "  - Updating skill manifest..."
    ask smapi update-skill-manifest -s $SKILL_ID -g development --manifest "file:skill-package/skill.json"
    
    # Update interaction model
    echo "  - Updating interaction model (en-US)..."
    ask smapi update-interaction-model -s $SKILL_ID -l en-US -g development --interaction-model "file:skill-package/interactionModels/custom/en-US.json"
    
    # Build the model
    echo "  - Building interaction model..."
    ask smapi get-skill-status -s $SKILL_ID
    
    echo "✅ Push complete!"
    echo "⚠️  Remember: Your Lambda code changes need to be deployed separately"
}

# Function to show status
show_status() {
    echo "📊 Skill Status:"
    echo "  Skill ID: $SKILL_ID"
    ask smapi get-skill-status -s $SKILL_ID
}

# Main menu
case "${1:-}" in
    pull)
        pull_from_remote
        ;;
    push)
        push_to_remote
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {pull|push|status}"
        echo ""
        echo "  pull   - Download latest skill config from Alexa Console"
        echo "  push   - Upload local skill config to Alexa Console"
        echo "  status - Check skill build status"
        echo ""
        exit 1
        ;;
esac
