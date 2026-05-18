@echo off
setlocal enabledelayedexpansion
title Kulfi Management System - Shop Hosting Mode
color 0B

:: 1. Detect Local IP Address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
)

:: 2. Environment Check
if not exist .venv (
    echo [CRITICAL] Environment Missing!
    pause
    exit /b
)

set PYTHON_EXE=.\.venv\Scripts\python.exe

:: 3. Port Cleanup (Ensure Port 8000 is free)
echo [SYSTEM] Preparing Network Port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1

:: 4. Database Check & Migration
echo [SYSTEM] Hardening Database...
%PYTHON_EXE% manage.py migrate --noinput > nul

:: 5. Background Server Start (Bind to all interfaces)
echo [SYSTEM] Booting Shop Cloud at !IP!:8000...
start /b "" %PYTHON_EXE% manage.py runserver 0.0.0.0:8000 > nul 2>&1

:: 6. Intelligent Wait & Launch
echo [SYSTEM] Opening Admin Interface...
timeout /t 5 /nobreak > nul
start http://127.0.0.1:8000/

:: 7. Success Notification
echo.
echo ===================================================
echo [SUCCESS] KULFI SYSTEM IS NOW LIVE ON YOUR NETWORK
echo ===================================================
echo PC Access: http://localhost:8000
echo PHONE Access: http://!IP!:8000
echo ===================================================
echo (This window will close in 10 seconds...)

:: Show a popup with the IP for the user
echo msgbox "Kulfi System is LIVE!" ^& vbCrLf ^& "Open this on your Phone/Tablet:" ^& vbCrLf ^& "http://!IP!:8000", vbInformation, "Shop Cloud Active" > %temp%\kulfi_msg.vbs
start %temp%\kulfi_msg.vbs

timeout /t 10 /nobreak > nul
exit
