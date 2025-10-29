@echo off
REM Optional: activate a virtual environment that lives next to this script
if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate"
)

REM Launch the installed WinMonitor GUI entry point
winmonitor-gui
