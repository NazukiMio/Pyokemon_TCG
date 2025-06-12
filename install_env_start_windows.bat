@echo off
setlocal enabledelayedexpansion

REM Auto-detect Python interpreter
set PYTHON_CMD=

where python >nul 2>nul && set PYTHON_CMD=python
if not defined PYTHON_CMD (
    where py >nul 2>nul && set PYTHON_CMD=py
)
if not defined PYTHON_CMD (
    where python3 >nul 2>nul && set PYTHON_CMD=python3
)

if not defined PYTHON_CMD (
    echo [ERROR] No suitable Python interpreter found. Please install Python and add it to your PATH.
    pause
    exit /b 1
)

echo Using Python command: %PYTHON_CMD%

@echo off
REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Uninstall all packages
pip freeze > uninstall.txt
for /F %%i in (uninstall.txt) do pip uninstall -y %%i
del uninstall.txt

REM Install required packages
pip install pygame-cards
pip uninstall -y pygame
pip install pygame-gui
pip install requests pillow opencv-python tqdm graphviz

REM Run the main script
%PYTHON_CMD% main.py

REM Maintain the console open (optional)
pause
