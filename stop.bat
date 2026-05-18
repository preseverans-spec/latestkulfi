@echo off
title Kulfi Management System - Shutdown
echo ===================================================
echo [STOP] Terminating Kulfi Management System...
echo ===================================================

:: Kill Python processes running manage.py
echo [PROCESS] Killing Django server...
taskkill /F /FI "IMAGENAME eq python.exe" /T 2>nul

echo [SUCCESS] All services stopped.
echo ===================================================
timeout /t 3
exit
