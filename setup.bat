@echo off
REM Clinical Copilot Setup Script for Windows

echo Setting up Clinical Copilot...

REM Setup Python backend
echo Setting up Python backend...
cd src

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Initialize vector database (if patient data exists)
if exist "patient_data.json" (
    echo Initializing vector database...
    python embed.py
)

echo Python backend setup complete!

REM Setup frontend
echo Setting up frontend...
cd ..\frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

echo Frontend setup complete!

echo Setup complete!
echo.
echo To start the application:
echo 1. Start the Python backend: cd src ^&^& python app.py
echo 2. Start the frontend: cd frontend ^&^& npm run dev
echo.
echo Then visit http://localhost:3000

pause