@echo off
cd /d "%~dp0"

if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found, using global Python.
)

echo Updating interactions.py and voice dependencies...
python -m pip install --upgrade discord.py-interactions[voice] PyNaCl

echo.
echo Done! Please restart the bot using bot.bat
pause
