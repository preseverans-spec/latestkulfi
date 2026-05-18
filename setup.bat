@echo off
title Kulfi Management System - Initial Setup
color 0E

echo ===================================================
echo [SETUP] CONFIGURING KULFI MANAGEMENT SYSTEM...
echo ===================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

:: Create virtual environment
if not exist .venv (
    echo [PROCESS] Creating Virtual Environment...
    python -m venv .venv
) else (
    echo [INFO] Virtual environment already exists.
)

:: Install requirements
echo [PROCESS] Installing Dependencies...
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

:: Initialize Database
echo [PROCESS] Initializing Database...
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py collectstatic --noinput

echo ===================================================
echo [SUCCESS] SETUP COMPLETE!
echo [ACTION] You can now run 'start.bat' to launch the app.
echo ===================================================
pause
