@echo off
REM Setup script for Windows
REM Creates virtual environment and installs dependencies
REM Usage: setup.bat

setlocal enabledelayedexpansion

echo === Microblog Translation CLI - Setup ===
echo.

REM Check if we're in the fixes directory
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found. Run this script from the fixes\ directory.
    exit /b 1
)

REM Create virtual environment
echo [1/2] Creating virtual environment...
python -m venv .venv

REM Activate and install
echo [2/2] Activating virtual environment and installing dependencies...
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo ✓ Setup complete!
echo.
echo To activate the virtual environment in future terminal sessions:
echo   .venv\Scripts\activate.bat
echo.
echo To run tests:
echo   run_test.bat
echo.
