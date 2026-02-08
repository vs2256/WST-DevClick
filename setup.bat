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

REM Check if venv exists
set VENV_EXISTS=0
set SKIP_INSTALL=0
if exist .venv (
  set VENV_EXISTS=1
  echo Virtual environment already exists.
  set /p RECREATE="Do you want to recreate it? (y/N): "
  if /i "!RECREATE!"=="y" (
    echo Removing existing virtual environment...
    rmdir /s /q .venv
    set VENV_EXISTS=0
  ) else (
    echo Using existing virtual environment.
    set SKIP_INSTALL=1
  )
  echo.
)

REM Create venv if needed
if %VENV_EXISTS% equ 0 (
  echo Creating virtual environment...
  %PYTHON_CMD% -m venv .venv
  if %errorlevel% neq 0 exit /b 1
  echo Done!
  echo.
  set SKIP_INSTALL=0
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

REM Install packages (check if needed)
if %SKIP_INSTALL% equ 1 (
  echo Checking installed packages...
  python -c "import dotenv" >nul 2>&1
  if %errorlevel% neq 0 (
    echo Required packages not found.
    set SKIP_INSTALL=0
  ) else (
    echo All required packages already installed.
    set /p REINSTALL="Do you want to reinstall packages? (y/N): "
    if /i "!REINSTALL!"=="y" (
      set SKIP_INSTALL=0
    )
    echo.
  )
)

if %SKIP_INSTALL% equ 0 (
  echo Installing packages...
  python -m pip install --upgrade pip --quiet
  python -m pip install -r requirements.txt --quiet
  echo Done!
  echo.
)

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
pause
exit /b %errorlevel%
