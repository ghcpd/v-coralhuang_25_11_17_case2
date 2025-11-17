@echo off
setlocal
cd /d %~dp0
if not exist ".venv\Scripts\activate.bat" (
  echo Virtual environment missing. Run setup.sh (or python -m venv .venv) first.
  exit /b 1
)
call .venv\Scripts\activate.bat
cd ..
python -m pytest -s fixes/tests
endlocal
