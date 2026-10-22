@echo off
setlocal
cd /d "%~dp0"

if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if not exist settings.json python setup.py
if errorlevel 1 exit /b 1
python app.py
