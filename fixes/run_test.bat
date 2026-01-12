@echo off
REM Windows batch test runner script
REM Usage: run_test.bat

setlocal enabledelayedexpansion

echo === Microblog Translation CLI - Windows Test Run ===
echo.

REM Check if we're in the fixes directory
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found. Run this script from the fixes\ directory.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [1/4] Creating virtual environment...
    python -m venv .venv
) else (
    echo [1/4] Virtual environment already exists
)

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo [3/4] Installing dependencies...
pip install -q -r requirements.txt

REM Run tests with coverage
echo [4/4] Running tests...
python -m pytest tests\test_translate_cli.py -v --tb=short 2>&1 | tee artifacts\test_output.log

REM Capture exit code
set TEST_EXIT=%ERRORLEVEL%

echo.
echo === Test Run Complete ===
if %TEST_EXIT% equ 0 (
    echo ✓ All tests passed
    exit /b 0
) else (
    echo ✗ Tests failed with exit code: %TEST_EXIT%
    exit /b %TEST_EXIT%
)
