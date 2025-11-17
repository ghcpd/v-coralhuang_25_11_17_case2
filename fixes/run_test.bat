@echo off
setlocal enabledelayedexpansion
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r %~dp0\requirements.txt
if not exist fixes\artifacts mkdir fixes\artifacts
pytest -q --maxfail=1 > fixes\artifacts\pytest_output.txt
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
