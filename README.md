# Windows System Monitor & Analytics Tool 🖥️

A Python-based system monitoring tool that provides real-time system information, analysis, and notifications for Windows machines.

## Features
- 🔍 Real-time system metrics monitoring
- 📊 Network and disk usage analytics
- 🌡️ CPU temperature tracking
- 💾 Automated report generation
- 🔔 Windows toast notifications
- 📝 Custom report generation
- 🤖 AI-powered system analysis using Ollama
- 🖼️ Simple GUI interface

## Installation

This project is packaged via `pyproject.toml`, so it can be installed directly with `pip`:

```bash
pip install .
```

If you plan to use the optional Ollama integration, install the extra dependency as well:

```bash
pip install .[ollama]
```

## Running the GUI

After installation a console script named `winmonitor-gui` is available. Run it to start the GUI without opening a console window on Windows:

```bash
winmonitor-gui
```

Alternatively, the module can be executed directly:

```bash
python -m startup_info
```

## Packaging & Distribution

The project can be distributed as a wheel that bundles the GUI and its dependencies:

1. Build the distributable artifacts:
   ```bash
   python -m build
   ```
   This generates `.whl` and `.tar.gz` files in the `dist/` directory.
2. Copy the wheel to the target Windows machine and install it with `pip install <wheel-file>.whl` inside the desired virtual environment.
3. The installer creates the `winmonitor-gui.exe` launcher in the environment's `Scripts` directory. You can execute this shortcut directly or wire it into automation scripts.
4. To ship a clickable helper for non-technical users, provide a `run_agent.bat` file next to the virtual environment that contains:
   ```bat
   @echo off
   call "%~dp0venv\Scripts\activate"
   winmonitor-gui
   ```
   Adjust the activation path to your deployment layout. The batch file ensures the GUI launches with `pythonw` behind the scenes, so no console window remains open.

These steps make it straightforward to redistribute the monitoring GUI or bundle it with other tooling.
