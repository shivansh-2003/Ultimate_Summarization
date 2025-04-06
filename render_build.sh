#!/usr/bin/env bash
# Build script for Render deployment

set -e

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright and its dependencies
pip install playwright
playwright install-deps
playwright install chromium

echo "Build completed successfully" 