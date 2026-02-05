#!/bin/bash
set -e

echo ""
echo "===================================================="
echo "  Workspace Automation - One Click Setup"
echo "===================================================="
echo ""

# Find Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
  PYTHON_CMD="python"
else
  echo "ERROR: Python not found"
  exit 1
fi
echo "Found: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Create venv
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  $PYTHON_CMD -m venv .venv
fi

# Activate venv
if [ ! -f ".venv/bin/activate" ]; then
  echo "ERROR: venv activation script missing"
  exit 1
fi
source .venv/bin/activate

# Check .env
if [ ! -f ".env" ]; then
  echo "ERROR: .env file not found"
  echo "Copy .env.example to .env and configure it"
  exit 1
fi

# Install packages
echo "Installing packages..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "Done!"
echo ""

# Run automation
echo "===================================================="
echo "Starting automation..."
echo "===================================================="
echo ""

set +e
python automation.py
EXIT_CODE=$?
set -e

echo ""
if [ "$EXIT_CODE" -eq 0 ]; then
  echo "SUCCESS"
else
  echo "FAILED"
fi
echo ""
exit $EXIT_CODE
