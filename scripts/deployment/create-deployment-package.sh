#!/bin/bash
# Quick deployment package creator for AWS Lambda

echo "Creating Lambda deployment package..."

# Get the root directory (2 levels up from scripts/deployment)
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LAMBDA_SOURCE="$ROOT_DIR/lambda"
DIST_DIR="$ROOT_DIR/dist"

# Clean up old package if exists
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# Create deployment directory and nested lambda folder so the ZIP has a top-level lambda/
DEPLOYMENT_PKG="$DIST_DIR/deployment-package"
mkdir -p "$DEPLOYMENT_PKG"
LAMBDA_DIR="$DEPLOYMENT_PKG/lambda"
mkdir -p "$LAMBDA_DIR"

# Copy all lambda code
echo "Copying Lambda code..."
cp -r "$LAMBDA_SOURCE"/*.py "$LAMBDA_DIR"/ 2>/dev/null || true
cp -r "$LAMBDA_SOURCE"/config "$LAMBDA_DIR"/ 2>/dev/null || true
cp -r "$LAMBDA_SOURCE"/handlers "$LAMBDA_DIR"/ 2>/dev/null || true
cp -r "$LAMBDA_SOURCE"/models "$LAMBDA_DIR"/ 2>/dev/null || true
cp -r "$LAMBDA_SOURCE"/services "$LAMBDA_DIR"/ 2>/dev/null || true
cp -r "$LAMBDA_SOURCE"/utils "$LAMBDA_DIR"/ 2>/dev/null || true
cp "$LAMBDA_SOURCE"/requirements.txt "$LAMBDA_DIR"/
cp "$LAMBDA_SOURCE"/credentials.json "$LAMBDA_DIR"/ 2>/dev/null || echo "Warning: credentials.json not found"

cd "$DEPLOYMENT_PKG" || exit 1

# Install dependencies
# echo "Installing Python dependencies..."
# pip install -r "$LAMBDA_DIR"/requirements.txt -t "$LAMBDA_DIR" --quiet

# Create zip file
echo "Creating ZIP file..."
ZIP_FILE="$DIST_DIR/lambda-deployment.zip"
zip -r "$ZIP_FILE" lambda -q

cd "$ROOT_DIR"

# Show result
if [ -f "$ZIP_FILE" ]; then
    SIZE=$(du -h "$ZIP_FILE" | cut -f1)
    echo "✓ Deployment package created successfully!"
    echo "  File: dist/lambda-deployment.zip"
    echo "  Size: $SIZE"
    echo ""
    echo "Next steps:"
    echo "1. Go to AWS Lambda Console"
    echo "2. Upload dist/lambda-deployment.zip"
    echo "3. Set handler to: lambda.lambda_function.lambda_handler"
    echo "4. Set runtime to: Python 3.11"
    echo "5. Configure environment variables (GOOGLE_SHEET_ID, etc.)"
else
    echo "✗ Failed to create deployment package"
    exit 1
fi
