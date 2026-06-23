@echo off
REM Enterprise AI Platform — Windows Quick Start
REM Opens backend (port 8000) and frontend (port 5173) in separate windows.

echo.
echo ==========================================
echo   Enterprise AI Platform — Starting...
echo ==========================================
echo.

REM Check .env exists
if not exist ".env" (
    echo ERROR: .env not found. Run setup.ps1 first.
    pause
    exit /b 1
)

REM Create data dirs if missing
if not exist "data\qdrant" mkdir data\qdrant
if not exist "data\logs"   mkdir data\logs

echo [1/2] Starting backend on http://localhost:8000
start "AI Platform - Backend" cmd /k "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

REM Give backend 3 seconds to start
timeout /t 3 /nobreak >nul

echo [2/2] Starting frontend on http://localhost:5173
start "AI Platform - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo   Both services starting in new windows.
echo.
echo   API:  http://localhost:8000/health
echo   UI:   http://localhost:5173
echo   Docs: http://localhost:8000/docs
echo.
echo   Login: admin / admin123
echo ==========================================
echo.
