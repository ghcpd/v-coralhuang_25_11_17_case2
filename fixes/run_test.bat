@echo off
setlocal enabledelayedexpansion
set ROOT=%~dp0
set VENV=%ROOT%\.venv
if not exist "%VENV%\Scripts\activate.bat" (
  echo Virtual environment not found at %VENV%. Run fixes\setup.sh (with WSL) or create the venv manually.
  exit /b 1
)
call "%VENV%\Scripts\activate.bat"
if not exist "%ROOT%\artifacts" mkdir "%ROOT%\artifacts"
set LOG=%ROOT%\artifacts\pytest-windows.log
set "PYTHONPATH=%ROOT%\src;%PYTHONPATH%"
pytest -s "%ROOT%\tests" -vv %* > "%LOG%" 2>&1
set STATUS=%ERRORLEVEL%
type "%LOG%"
echo Pytest finished with status %STATUS% (log: %LOG%)
exit /b %STATUS%
