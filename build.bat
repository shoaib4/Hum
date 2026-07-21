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

REM ==========================================
REM  Check for required dependencies
REM ==========================================

echo [*] Checking required files...
echo.

REM Check for whisper-server.exe (should be included in repo)
if not exist "whisper_cpp\whisper-server.exe" (
    echo ==========================================
    echo  MISSING: whisper_cpp\whisper-server.exe
    echo ==========================================
    echo.
    echo This file should have been included in the repository.
    echo If it's missing, re-clone the repo or download it from:
    echo   https://github.com/ggerganov/whisper.cpp/releases
    echo.
    echo Place whisper-server.exe in the whisper_cpp\ folder.
    echo.
    pause
    exit /b 1
)

REM Check for at least one model file
if not exist "models\ggml-base.bin" (
    if not exist "models\ggml-tiny.bin" (
        echo ==========================================
        echo  MISSING: Whisper model file
        echo ==========================================
        echo.
        echo At least one Whisper model file is required.
        echo.
        echo Download a model from:
        echo   Base model (recommended, ~148 MB):
        echo     https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
        echo.
        echo   Tiny model (faster, less accurate, ~75 MB):
        echo     https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin
        echo.
        echo Place the downloaded .bin file in the models\ folder.
        echo.
        echo After placing the file, run this script again.
        echo.
        pause
        exit /b 1
    )
)

echo [+] whisper-server.exe found.
echo [+] Model file(s) found.
echo.

REM ==========================================
REM  Build
REM ==========================================

REM Install/upgrade build dependencies
echo [*] Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller

REM Install project dependencies
if exist "requirements.txt" (
    echo [*] Installing project dependencies...
    python -m pip install -r requirements.txt
)

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
