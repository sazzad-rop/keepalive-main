Server Availability Check
=========================

A Python application that simulates system activity to keep Teams from going idle during specified hours.

Quick Start
-----------
1. Run setup.bat to create the virtual environment and install dependencies.
2. Launch the app with ServerAvailabilityCheck.bat.
3. Configure start/end times and click Start.

Features
--------
- GUI for setting active hours (start and end time)
- Simulates invisible mouse movements and keyboard presses
- Runs in background with system tray integration
- Works on Windows using ctypes

Requirements
------------
- Python 3.8+
- tkinter (usually included with Python)
- Pillow
- pystray

Installation
------------
One-step setup:
   setup.bat

This will:
- create the virtual environment at .venv
- install dependencies from requirements.txt
- prepare the project for launch

Manual install:
1. Create and activate a virtual environment:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
2. Install dependencies:
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Usage
-----
Run the application with:
   ServerAvailabilityCheck.bat

This batch file uses the virtual environment if it exists, or falls back to the system Python installation.

Build Executable
----------------
To build a standalone Windows executable, run:
   build_server_availability_check.bat

The compiled executable will be created in the dist folder as ServerAvailabilityCheck.exe.

Running the App
---------------
1. Enter start time (hours and minutes)
2. Enter end time (hours and minutes)
3. Click Start to begin monitoring
4. The application will minimize to the system tray
5. Activity simulation runs during specified hours
6. Right-click the tray icon and select Quit to stop

How It Works
------------
- Uses Windows API via ctypes to simulate mouse and keyboard activity
- Checks current time periodically (every 60 seconds by default)
- Only simulates activity between the configured hours
- Runs as a background daemon thread

Notes
-----
- Simulation is subtle and should not interfere with normal work
- Requires Windows OS because it uses ctypes.windll
- setup.bat should be run once before first use
