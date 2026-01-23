@echo off
REM AgriTech Report Engine Startup Script
REM This script starts all required services for the PDF Report Generation and Email Delivery Engine

echo ========================================
echo AgriTech Report Engine Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if Redis is installed
echo Checking Redis installation...
redis-cli --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Redis is not installed or not in PATH
    echo.
    echo Please install Redis:
    echo 1. Download from: https://github.com/microsoftarchive/redis/releases
    echo 2. Or use WSL: wsl --install, then: sudo apt install redis-server
    echo.
    pause
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please copy .env.example to .env and configure it
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env from .env.example - Please configure it before continuing
    )
    pause
)

echo.
echo Starting services...
echo.

REM Create reports directory if it doesn't exist
if not exist "reports" mkdir reports

REM Start Redis in a new window
echo [1/3] Starting Redis server...
start "Redis Server" cmd /k "redis-server || echo Redis failed to start. Make sure Redis is installed. && pause"
timeout /t 2 /nobreak >nul

REM Start Flask app in a new window
echo [2/3] Starting Flask application...
start "Flask App - AgriTech" cmd /k "python app.py"
timeout /t 3 /nobreak >nul

REM Start Celery worker in a new window
echo [3/3] Starting Celery worker...
start "Celery Worker - Reports" cmd /k "celery -A backend.config.celery_config.celery_app worker --loglevel=info --pool=solo"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Services running in separate windows:
echo   - Redis Server
echo   - Flask App (http://localhost:5000)
echo   - Celery Worker
echo.
echo To stop all services, close each window.
echo.
echo Press any key to exit this window...
pause >nul
