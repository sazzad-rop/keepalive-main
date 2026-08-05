@echo off
setlocal enabledelayedexpansion

REM Build a standalone executable for the Server Availability Check application
set PROJECT_ROOT=%~dp0
set PY_SCRIPT=ServerAvailabilityCheck.py
set SPEC_NAME=server_availability_check.spec

if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set PY_CMD=%PROJECT_ROOT%\.venv\Scripts\python.exe
) else (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        where py >nul 2>&1
        if %errorlevel% neq 0 (
            echo Python is not installed or not on PATH.
            pause
            exit /b 1
        ) else (
            set PY_CMD=py -3
        )
    ) else (
        set PY_CMD=python
    )
)

echo Checking PyInstaller dependency...
%PY_CMD% -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found; installing into the active Python environment...
    %PY_CMD% -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

echo Building executable with PyInstaller...
%PY_CMD% -m PyInstaller --onefile --windowed --name ServerAvailabilityCheck "%PROJECT_ROOT%%PY_SCRIPT%"

if %errorlevel% neq 0 (
    echo Build failed. Please check PyInstaller output above.
    pause
    exit /b 1
)

echo Build complete. Executable available at dist\ServerAvailabilityCheck.exe
pause
endlocal
