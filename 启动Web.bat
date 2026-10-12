@echo off
cd /d "%~dp0"

echo ============================================
echo   Student Growth Platform - Web Launcher
echo ============================================

rem --- Step 1: Backend API (port 8000) ---
curl -s -o nul --max-time 2 http://127.0.0.1:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo [1/2] Starting backend API on :8000 ...
    start "Backend API :8000" cmd /k "py -3.12 -m web.main"
) else (
    echo [1/2] Backend already running on :8000
)

rem --- Step 2: Frontend dev server (port 5174) ---
curl -s -o nul --max-time 2 http://localhost:5174/ >nul 2>&1
if errorlevel 1 (
    echo [2/2] Starting frontend on :5174 ...
    start "Frontend :5174" cmd /k "cd frontend && npm run dev"
) else (
    echo [2/2] Frontend already running on :5174
)

echo.
echo Waiting for services to be ready ...
timeout /t 6 /nobreak >nul

echo Opening http://localhost:5174 in your browser ...
start http://localhost:5174

echo.
echo Keep the two console windows open to keep services running.
echo If the page does not load, wait a few seconds and refresh.
echo.
pause
