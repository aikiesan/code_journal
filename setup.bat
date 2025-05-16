@echo off
echo Setting up Code Journal...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Get Python Scripts directory and add it to PATH temporarily
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXE=%%i
set SCRIPTS_DIR=%PYTHON_EXE:\python.exe=\Scripts%
set PATH=%SCRIPTS_DIR%;%PATH%

echo Installing required packages...

REM Install/upgrade pip first
python -m pip install --upgrade pip --user
if errorlevel 1 (
    echo Error: Failed to upgrade pip
    pause
    exit /b 1
)

REM Install all required packages with --user flag
echo Installing CustomTkinter...
python -m pip install customtkinter --user
if errorlevel 1 (
    echo Error: Failed to install CustomTkinter
    pause
    exit /b 1
)

echo Installing PyWin32...
python -m pip install pywin32 --user
if errorlevel 1 (
    echo Error: Failed to install PyWin32
    pause
    exit /b 1
)

echo Installing PyInstaller...
python -m pip install --upgrade pyinstaller --user
if errorlevel 1 (
    echo Error: Failed to install PyInstaller
    pause
    exit /b 1
)

echo Installing Pillow...
python -m pip install pillow --user
if errorlevel 1 (
    echo Error: Failed to install Pillow
    pause
    exit /b 1
)

REM Verify PyInstaller installation
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Warning: PyInstaller not found in PATH. Adding Python user scripts to PATH...
    for /f "tokens=*" %%i in ('python -m site --user-site') do set USER_SITE=%%i
    set USER_SCRIPTS=%USER_SITE:site-packages=Scripts%
    set PATH=%USER_SCRIPTS%;%PATH%
)

echo.
echo Setup complete! You can now run the application.
echo.
echo Press any key to exit...
pause 