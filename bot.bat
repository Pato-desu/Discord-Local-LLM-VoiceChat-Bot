@echo off
cd /d "%~dp0"

if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found, using global Python.
)

python main.py
pause
