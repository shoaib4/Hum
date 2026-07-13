@echo off
REM Build script for Hum executable on Windows

echo.
echo ==========================================
echo         Building Hum Executable
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [-] Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    echo [-] main.py not found. Please run this from the project root.
    pause
    exit /b 1
)

REM Install/upgrade build dependencies
echo [*] Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller

REM Run the build script
echo [*] Building executable...
python build.py

REM Check if build succeeded
if exist "dist\Hum.exe" (
    echo.
    echo [+] Build completed successfully!
    echo.
    echo Generated files:
    echo     dist\Hum.exe - Main executable
    echo     dist\Hum-Portable\ - Portable package
    echo     install.bat - Installer script
    echo.
    echo You can now:
    echo 1. Run dist\Hum.exe directly
    echo 2. Use install.bat to install system-wide
    echo 3. Distribute the portable package
    echo.
) else (
    echo.
    echo [-] Build failed. Check the output above for errors.
    echo.
)

pause