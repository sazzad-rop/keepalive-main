@echo off
setlocal enabledelayedexpansion

REM Set project root and command paths
set PROJECT_ROOT=%~dp0
set PY_SCRIPT=ServerAvailabilityCheck.py
set REQUIREMENTS=requirements.txt

REM Determine Python executable
if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set PY_CMD=%PROJECT_ROOT%\.venv\Scripts\python.exe
) else (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        where py >nul 2>&1
        if %errorlevel% neq 0 (
            echo Python is not installed or not on PATH.
            echo Please install Python 3.8+ and rerun this script.
            pause
            exit /b 1
        ) else (
            set PY_CMD=py -3
        )
    ) else (
        set PY_CMD=python
    )
)

REM Use python to check installed dependencies and install missing ones
echo Checking dependencies...
"%PY_CMD%" -m pip install --upgrade pip >nul 2>&1
if exist "%PROJECT_ROOT%%REQUIREMENTS%" (
    "%PY_CMD%" -m pip install -r "%PROJECT_ROOT%%REQUIREMENTS%"
) else (
    echo Missing %REQUIREMENTS%. Please create the file with project dependencies.
    pause
    exit /b 1
)

echo Launching Server Availability Check...
"%PY_CMD%" "%PROJECT_ROOT%%PY_SCRIPT%"
endlocal
