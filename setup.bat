@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0
set VENV=%ROOT%\.venv
set PY_SCRIPT=ServerAvailabilityCheck.py
set REQUIREMENTS=requirements.txt

REM Locate Python interpreter
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

REM Create virtual environment if necessary
if not exist "%VENV%\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY_CMD% -m venv "%VENV%"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

set VENV_PY=%VENV%\Scripts\python.exe

echo Upgrading pip in the virtual environment...
"%VENV_PY%" -m pip install --upgrade pip >nul 2>&1

if exist "%ROOT%%REQUIREMENTS%" (
    echo Installing dependencies from %REQUIREMENTS%...
    "%VENV_PY%" -m pip install -r "%ROOT%%REQUIREMENTS%"
    if %errorlevel% neq 0 (
        echo Dependency installation failed.
        pause
        exit /b 1
    )
) else (
    echo Missing %REQUIREMENTS%. Please add the file and rerun setup.
    pause
    exit /b 1
)

echo Setup complete.
echo Run ServerAvailabilityCheck.bat to launch the application.
echo Run build_server_availability_check.bat to create the executable.
pause
endlocal
