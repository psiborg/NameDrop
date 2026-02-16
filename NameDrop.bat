@echo off
REM Launch NameDrop - Smart File Renaming Tool
echo Starting NameDrop...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check for optional dependencies
echo Checking optional dependencies...
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Pillow not installed - EXIF date extraction unavailable
    echo Install with: pip install pillow
    echo.
)

python -c "import tkinterdnd2" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] tkinterdnd2 not installed - Drag-and-drop unavailable
    echo Install with: pip install tkinterdnd2
    echo.
)

echo Starting application...
echo.

REM Run the application
python "%~dp0namedrop.py"

if errorlevel 1 (
    echo.
    echo Application closed with an error.
    echo.
    pause
)
