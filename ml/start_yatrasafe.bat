@echo off
title YatraSafe AI + Real-Time Platform Launcher
color 0A

echo ===============================================================================
echo            YATRASAFE AI + REAL-TIME CROWD INTELLIGENCE PLATFORM
echo ===============================================================================
echo.

:: Resolve script directory
cd /d "%~dp0"
echo [1/4] Project Directory: %CD%

:: Check virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at .venv\Scripts\activate.bat!
    echo Please create the virtual environment first using: python -m venv .venv
    pause
    exit /b 1
)

echo [2/4] Activating Virtual Environment...
call .venv\Scripts\activate.bat

echo [3/4] Launching Background IoT Sensor Simulator...
start "YatraSafe IoT Simulator" cmd /k "title YatraSafe IoT Sensor Simulator && cd /d "%~dp0" && call .venv\Scripts\activate.bat && python realtime/sensor_simulator.py"

echo [4/4] Starting FastAPI High-Performance Backend Service...
start "YatraSafe FastAPI Server" cmd /k "title YatraSafe FastAPI Server (Port 8000) && cd /d "%~dp0" && call .venv\Scripts\activate.bat && python -m uvicorn api.prediction_api:app --host 127.0.0.1 --port 8000"

:: Wait 2 seconds for server initialization
timeout /t 2 /nobreak >nul

echo.
echo ===============================================================================
echo   >> YatraSafe Microservice Running at: http://127.0.0.1:8000
echo   >> Government Command Dashboard:     http://127.0.0.1:8000/dashboard
echo   >> Interactive Swagger API Docs:     http://127.0.0.1:8000/docs
echo ===============================================================================
echo.
echo Opening Government Command Dashboard in default browser...
start http://127.0.0.1:8000/dashboard

echo.
echo YatraSafe is running live. Press any key to exit this launcher window.
pause >nul
