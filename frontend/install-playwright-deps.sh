#!/bin/bash

# Install system dependencies for Playwright Chromium browser
# This script requires sudo privileges

echo "Installing Playwright system dependencies..."
echo "This requires sudo password..."

sudo apt-get update && sudo apt-get install -y libnspr4 libnss3 libasound2t64

if [ $? -eq 0 ]; then
    echo "✅ System dependencies installed successfully!"
    echo ""
    echo "Now you can run the Playwright tests:"
    echo "  cd /mnt/c/Users/Solomon-PC/Documents/Planning\ Explorer/frontend"
    echo "  npx playwright test tests/report-page.spec.ts --reporter=list"
else
    echo "❌ Failed to install dependencies. Please check your sudo privileges."
    exit 1
fi
