@echo off
echo 🚀 Starting Recruitment System Python Microservices
echo ============================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "shared" (
    echo ✗ Please run this script from the project root directory
    pause
    exit /b 1
)

REM Install requirements if not already installed
echo Installing dependencies...
pip install -r requirements.txt

REM Start all services using Python script
echo Starting services...
python start_services.py

pause 