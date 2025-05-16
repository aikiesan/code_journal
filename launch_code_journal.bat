@echo off
echo Starting Code Journal...

REM Check if the executable exists in the dist folder
if exist "dist\CodeJournal.exe" (
    echo Found existing CodeJournal.exe. Launching...
    start "" "dist\CodeJournal.exe"
    goto :eof
) else (
    echo CodeJournal.exe not found in dist. Attempting to build...
    python build.py
    if errorlevel 1 (
        echo Error: Failed to build Code Journal.
        echo You can try running the script directly using: python app_gui.py
        pause
        exit /b 1
    )
    echo Build successful. Launching CodeJournal.exe...
    if exist "dist\CodeJournal.exe" (
        start "" "dist\CodeJournal.exe"
    ) else (
        echo Error: CodeJournal.exe not found in dist even after build attempt.
        pause
        exit /b 1
    )
    goto :eof
)

:eof
REM The following lines for direct script execution are now effectively bypassed
REM if the .exe logic above succeeds and uses 'goto :eof'.
REM They can serve as a fallback if you comment out the .exe logic for development.

REM echo Running script directly (fallback or development mode)...
REM REM Ensure your Python environment is correctly set up if needed (e.g., activating a venv)
REM REM Example: CALL path\to\your\venv\Scripts\activate.bat

REM REM Use pythonw.exe to run app_gui.py without a console window
REM pythonw app_gui.py

REM REM Example: CALL deactivate (if you activated a venv) 