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

# Check if venv exists
SKIP_INSTALL=0
if [ -d ".venv" ]; then
  echo "Virtual environment already exists."
  read -p "Do you want to recreate it? (y/N): " RECREATE
  echo ""
  if [[ "$RECREATE" =~ ^[Yy]$ ]]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    echo "Done!"
    echo ""
    SKIP_INSTALL=0
  else
    echo "Using existing virtual environment."
    echo ""
    SKIP_INSTALL=1
  fi
else
  echo "Creating virtual environment..."
  $PYTHON_CMD -m venv .venv
  echo "Done!"
  echo ""
  SKIP_INSTALL=0
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

# Install packages (check if needed)
if [ "$SKIP_INSTALL" -eq 1 ]; then
  echo "Checking installed packages..."
  if ! python -c "import dotenv" &> /dev/null; then
    echo "Required packages not found."
    SKIP_INSTALL=0
  else
    echo "All required packages already installed."
    read -p "Do you want to reinstall packages? (y/N): " REINSTALL
    echo ""
    if [[ "$REINSTALL" =~ ^[Yy]$ ]]; then
      SKIP_INSTALL=0
    fi
  fi
fi

if [ "$SKIP_INSTALL" -eq 0 ]; then
  echo "Installing packages..."
  pip install --upgrade pip --quiet
  pip install -r requirements.txt --quiet
  echo "Done!"
  echo ""
fi

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
read -p "Press Enter to exit..."
exit $EXIT_CODE
