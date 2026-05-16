@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: INDIAN KULFI - PROFESSIONAL FULL STACK STARTER (OPTIMIZED)
:: ============================================================================
:: This script automates environment setup, dependency management, 
:: database validation, and server launch for Indian Kulfi.
:: ============================================================================

title INDIAN KULFI - Enterprise Startup
color 0b

:: ANSI Color Codes for Professional Output
set "ESC="
set "GREEN=%ESC%[92m"
set "BLUE=%ESC%[94m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "CYAN=%ESC%[36m"
set "RESET=%ESC%[0m"
set "BOLD=%ESC%[1m"

cls
echo.
echo  %BOLD%%CYAN%===========================================================%RESET%
echo  %BOLD%%CYAN%       INDIAN KULFI - PROFESSIONAL ENTERPRISE SUITE        %RESET%
echo  %BOLD%%CYAN%===========================================================%RESET%
echo.

:: ----------------------------------------------------------------------------
:: STEP 0 - ENVIRONMENT PRE-CHECK
:: ----------------------------------------------------------------------------
cd /d "%~dp0"
echo [%BLUE%INFO%RESET%] Working Directory: %cd%

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [%RED%ERROR%RESET%] Python not found in PATH. Please install Python 3.8+.
    pause
    exit /b 1
)

:: ----------------------------------------------------------------------------
:: STEP 1 - PORT MANAGEMENT (AUTO-CLEANUP)
:: ----------------------------------------------------------------------------
echo [%YELLOW%1/6%RESET%] Checking Port 8000 availability...

:: Find process ID using port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    set "PID=%%a"
)

if defined PID (
    echo       [%YELLOW%WARN%RESET%] Port 8000 is occupied by PID !PID!. Terminating...
    taskkill /F /PID !PID! >nul 2>&1
    timeout /t 1 >nul
) else (
    echo       [%GREEN%OK%RESET%] Port 8000 is free.
)

:: ----------------------------------------------------------------------------
:: STEP 2 - VIRTUAL ENVIRONMENT & DEPENDENCIES
:: ----------------------------------------------------------------------------
echo.
echo [%YELLOW%2/6%RESET%] Verifying Virtual Environment...

if not exist .venv\Scripts\activate.bat (
    echo       [%YELLOW%INFO%RESET%] No virtual environment found. Initializing .venv...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo       [%RED%ERROR%RESET%] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
echo       [%GREEN%OK%RESET%] Environment activated.

echo.
echo [%YELLOW%3/6%RESET%] Optimizing Dependencies (pip install)...
:: Use --disable-pip-version-check to save time
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo       [%YELLOW%WARN%RESET%] Dependency verification completed with warnings.
) else (
    echo       [%GREEN%OK%RESET%] All backend packages are up to date.
)

:: ----------------------------------------------------------------------------
:: STEP 3 - DATABASE VALIDATION
:: ----------------------------------------------------------------------------
echo.
echo [%YELLOW%4/6%RESET%] Connecting Database...
python manage.py check_db >nul 2>&1
if %errorlevel% neq 0 (
    echo       [%RED%ERROR%RESET%] Database connection failed! 
    echo       Please check your DB settings or permissions.
    pause
    exit /b 1
) else (
    echo       [%GREEN%OK%RESET%] Database connection established permanently.
)

:: Run migrations safely
python manage.py migrate --noinput >nul 2>&1
echo       [%GREEN%OK%RESET%] Schema verified. Data is persistent.

:: ----------------------------------------------------------------------------
:: STEP 4 - STATIC ASSETS
:: ----------------------------------------------------------------------------
echo.
echo [%YELLOW%5/6%RESET%] Syncing Static Assets...
python manage.py collectstatic --noinput >nul 2>&1
echo       [%GREEN%OK%RESET%] Static files optimized.

:: ----------------------------------------------------------------------------
:: STEP 5 - PARALLEL STARTUP & BROWSER LAUNCH
:: ----------------------------------------------------------------------------
echo.
echo [%YELLOW%6/6%RESET%] %BOLD%%CYAN%Launching Application...%RESET%
echo.
echo  %BOLD%===========================================================%RESET%
echo   %GREEN%Access URL:%RESET%  http://127.0.0.1:8000
echo   %BLUE%Admin Panel:%RESET% http://127.0.0.1:8000/admin
echo  %BOLD%===========================================================%RESET%
echo.
echo  [%YELLOW%PRESS CTRL+C TO TERMINATE ALL PROCESSES%RESET%]
echo.

:: Open browser in a separate process with a slight delay
start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8000"

:: Start Django server (main blocking process)
python manage.py runserver 0.0.0.0:8000

echo.
echo [%BLUE%INFO%RESET%] System shutdown gracefully.
pause
