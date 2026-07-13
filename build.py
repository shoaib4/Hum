#!/usr/bin/env python3
"""
Build script for creating Hum executable using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"[+] {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] {description} failed:")
        print(f"Command: {cmd}")
        print(f"Error: {e.stderr}")
        return False

def clean_build():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"[-] Cleaned {dir_name}/")

    for pattern in files_to_clean:
        import glob
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"[-] Cleaned {file}")

def check_dependencies():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print("[+] PyInstaller is installed")
        return True
    except ImportError:
        print("[-] PyInstaller not found. Installing...")
        return run_command(f"{sys.executable} -m pip install pyinstaller", "Installing PyInstaller")

def build_executable():
    """Build the executable using PyInstaller."""

    # Create the PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window (GUI app)
        "--name=Hum",
        "--icon=assets/icons/power.svg",  # App icon (will be converted)
        "--add-data=assets;assets",  # Include assets folder
        "--hidden-import=PySide6.QtSvg",  # Ensure QtSvg is included
        "--hidden-import=sounddevice",
        "--hidden-import=numpy",
        "--exclude-module=matplotlib",  # Reduce size
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--optimize=2",  # Python optimization
        "main.py"
    ]

    # Platform-specific adjustments
    if sys.platform == "win32":
        cmd.insert(-1, "--console")  # Keep console on Windows for debugging
        cmd.insert(-1, "--uac-admin")  # Request admin for text insertion

    cmd_str = " ".join(cmd)
    return run_command(cmd_str, "Building executable")

def create_spec_file():
    """Create a custom spec file for more control."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Data files to include
datas = [
    ('assets', 'assets'),
]

# Hidden imports
hiddenimports = [
    'PySide6.QtSvg',
    'sounddevice',
    'numpy',
    'openai',
]

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary modules to reduce size
a.binaries = [x for x in a.binaries if not x[0].startswith(('tcl', 'tk'))]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Hum',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

    with open('hum.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("[+] Created hum.spec file")

def build_with_spec():
    """Build using the custom spec file."""
    return run_command("pyinstaller hum.spec", "Building with spec file")

def create_installer_script():
    """Create a simple installer script for Windows."""
    if sys.platform != "win32":
        return

    installer_content = '''@echo off
echo.
echo ==========================================
echo         Hum Voice-to-Text Setup
echo ==========================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo.
    echo WARNING: Not running as administrator.
    echo Some features may not work properly.
    echo.
)

REM Create installation directory
set "INSTALL_DIR=%PROGRAMFILES%\\Hum"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
echo Installing Hum executable...
copy /Y "dist\\Hum.exe" "%INSTALL_DIR%\\Hum.exe"

REM Create desktop shortcut
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\\Desktop\\Hum.lnk"
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%INSTALL_DIR%\\Hum.exe'; $s.Save()"

REM Create start menu entry
echo Creating start menu entry...
set "STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"
copy /Y "%SHORTCUT%" "%STARTMENU%\\Hum.lnk"

echo.
echo ==========================================
echo Installation complete!
echo.
echo Hum has been installed to: %INSTALL_DIR%
echo Desktop shortcut created: %USERPROFILE%\\Desktop\\Hum.lnk
echo.
echo You can now run Hum from:
echo - Desktop shortcut
echo - Start menu
echo - Direct path: %INSTALL_DIR%\\Hum.exe
echo ==========================================
echo.
pause
'''

    with open('install.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    print("[+] Created install.bat installer script")

def create_portable_package():
    """Create a portable package with all necessary files."""
    if not os.path.exists('dist/Hum.exe'):
        print("[-] Executable not found. Build first.")
        return False

    # Create portable package directory
    portable_dir = Path('dist/Hum-Portable')
    portable_dir.mkdir(exist_ok=True)

    # Copy executable
    shutil.copy2('dist/Hum.exe', portable_dir / 'Hum.exe')

    # Copy assets if they exist
    if os.path.exists('assets'):
        shutil.copytree('assets', portable_dir / 'assets', dirs_exist_ok=True)

    # Create readme for portable version
    portable_readme = '''# Hum Portable

This is a portable version of Hum Voice-to-Text application.

## Quick Start
1. Double-click Hum.exe to launch
2. The floating pill will appear at the bottom of your screen
3. Click the microphone to start recording
4. Speak naturally, then click pause to transcribe

## Requirements
- Windows 10/11
- Microphone access
- Buzz application installed (for Whisper server)

## Troubleshooting
If the app doesn't start:
- Right-click Hum.exe -> "Run as administrator"
- Check if Buzz is properly installed
- Ensure microphone permissions are granted

For more help, visit: [GitHub Repository URL]
'''

    with open(portable_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(portable_readme)

    print(f"[+] Created portable package: {portable_dir}")
    return True

def main():
    """Main build process."""
    print("Building Hum executable...")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("[-] main.py not found. Run this script from the project root.")
        return False

    # Clean previous builds
    clean_build()

    # Check dependencies
    if not check_dependencies():
        return False

    # Create spec file for better control
    create_spec_file()

    # Build executable
    if not build_with_spec():
        return False

    # Create installer and portable package
    if sys.platform == "win32":
        create_installer_script()

    create_portable_package()

    # Test the build
    print("\n" + "=" * 50)
    print("Testing build...")
    test_result = run_command(f"{sys.executable} test_build.py", "Running build tests")

    # Final summary
    print("\n" + "=" * 50)
    print("[+] Build completed successfully!")
    print("\nGenerated files:")
    print("    dist/Hum.exe - Main executable")
    print("    dist/Hum-Portable/ - Portable package")
    if sys.platform == "win32":
        print("    install.bat - Windows installer script")

    # Show file sizes
    exe_path = Path('dist/Hum.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\nExecutable size: {size_mb:.1f} MB")

    print("\n[+] Ready for distribution!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)