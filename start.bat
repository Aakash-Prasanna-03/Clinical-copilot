@echo off
REM Start both frontend and backend services

echo Starting Clinical Copilot services...

REM Start Python backend in new window
echo Starting Python backend...
start "Python Backend" cmd /k "cd src && venv\Scripts\activate.bat && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo Starting frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo Both services are starting...
echo Backend will be available at http://localhost:5000
echo Frontend will be available at http://localhost:3000

pause