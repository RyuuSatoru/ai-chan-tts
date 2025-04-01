@echo off
REM ------------------------------------------
REM This batch file sets up the environment, installs required packages, and runs the Discord bot
REM ------------------------------------------

REM Check if Python is installed
python --version
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python from https://www.python.org/downloads/
    exit /b
)

REM Set up virtual environment (optional but recommended)
IF NOT EXIST venv (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install required packages
pip install -r caidat.txt

REM Set PYTHONPATH to include the bot directory
set PYTHONPATH=%PYTHONPATH%;%CD%\bot

REM Check if ffmpeg.exe exists in the expected directory
IF NOT EXIST "venv\Lib\site-packages\ffmpeg\bin\ffmpeg.exe" (
    echo ffmpeg.exe not found. Please ensure ffmpeg is installed in venv\Lib\site-packages\ffmpeg\bin\.
    exit /b
)

REM Run the Python script
python data\watch.py main.py

REM Pause the console (optional, for debugging purposes)
pause