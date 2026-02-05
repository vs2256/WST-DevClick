@echo off
echo.
echo ====================================================
echo  Workspace Automation - One Click Setup
echo ====================================================
echo.

REM Find Python
set PYTHON_CMD=
py --version >nul 2>&1
if %errorlevel% equ 0 set PYTHON_CMD=py
if "%PYTHON_CMD%"=="" (
  python --version >nul 2>&1
  if %errorlevel% equ 0 set PYTHON_CMD=python
)
if "%PYTHON_CMD%"=="" (
  echo ERROR: Python not found
  exit /b 1
)
echo Found: %PYTHON_CMD%
echo.

REM Create venv
if not exist .venv (
  echo Creating virtual environment...
  %PYTHON_CMD% -m venv .venv
  if %errorlevel% neq 0 exit /b 1
)

REM Activate venv
if not exist .venv\Scripts\activate.bat (
  echo ERROR: venv activation script missing
  exit /b 1
)
call .venv\Scripts\activate.bat

REM Check .env
if not exist .env (
  echo ERROR: .env file not found
  echo Copy .env.example to .env and configure it
  exit /b 1
)

REM Install packages
echo Installing packages...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
echo Done!
echo.

REM Run automation
echo ====================================================
echo Starting automation...
echo ====================================================
echo.
python automation.py

echo.
if %errorlevel% equ 0 (
  echo SUCCESS
  ) else (
  echo FAILED
)
echo.
exit /b %errorlevel%
