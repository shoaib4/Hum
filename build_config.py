"""
Build configuration for Hum executable.
Customize these settings to control the build process.
"""

import os
import sys

# Application metadata
APP_NAME = "Hum"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Voice to Text Desktop Application"
APP_AUTHOR = "Hum Team"

# Build settings
BUILD_DIR = "dist"
BUILD_NAME = "Hum"

# PyInstaller options
PYINSTALLER_OPTIONS = {
    # Basic options
    "onefile": True,  # Create single executable file
    "windowed": True,  # No console window for GUI app
    "optimize": 2,    # Python optimization level

    # Paths and files
    "name": BUILD_NAME,
    "icon": "assets/icons/power.svg",  # App icon
    "add_data": [
        ("assets", "assets"),  # Include assets folder
    ],

    # Dependencies
    "hidden_imports": [
        "PySide6.QtSvg",
        "PySide6.QtWidgets",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "sounddevice",
        "numpy",
        "openai",
    ],

    # Exclusions to reduce size
    "excludes": [
        "matplotlib",
        "scipy",
        "pandas",
        "jupyter",
        "IPython",
        "tkinter",
        "unittest",
        "pydoc",
        "doctest",
    ],

    # Platform-specific options
    "platform_options": {
        "win32": {
            "console": False,  # Set to True for debugging on Windows
            "uac_admin": False,  # Request admin privileges
        },
        "linux": {
            "strip": True,  # Strip debug symbols
        },
        "darwin": {  # macOS
            "osx_bundle_identifier": "com.hum.voice2text",
        }
    }
}

# UPX compression (optional, reduces file size)
USE_UPX = True  # Set to False if UPX is not installed

# Advanced build options
ADVANCED_OPTIONS = {
    # Code optimization
    "bootloader_ignore_signals": False,
    "debug": False,
    "strip": False,

    # Runtime options
    "runtime_tmpdir": None,
    "disable_windowed_traceback": False,
    "argv_emulation": False,
}

def get_platform_icon():
    """Get platform-specific icon path."""
    if sys.platform == "win32":
        return "assets/icons/power.svg"  # Will be converted to .ico
    elif sys.platform == "darwin":
        return "assets/icons/power.svg"  # Will be converted to .icns
    else:
        return "assets/icons/power.svg"  # Linux uses SVG or PNG

def get_build_command():
    """Generate PyInstaller command based on configuration."""
    cmd = ["pyinstaller"]

    # Basic options
    if PYINSTALLER_OPTIONS.get("onefile"):
        cmd.append("--onefile")

    if PYINSTALLER_OPTIONS.get("windowed"):
        cmd.append("--windowed")

    # Name and paths
    cmd.extend(["--name", PYINSTALLER_OPTIONS["name"]])

    icon = get_platform_icon()
    if os.path.exists(icon):
        cmd.extend(["--icon", icon])

    # Data files
    for src, dst in PYINSTALLER_OPTIONS.get("add_data", []):
        if os.path.exists(src):
            separator = ";" if sys.platform == "win32" else ":"
            cmd.extend(["--add-data", f"{src}{separator}{dst}"])

    # Hidden imports
    for imp in PYINSTALLER_OPTIONS.get("hidden_imports", []):
        cmd.extend(["--hidden-import", imp])

    # Exclusions
    for exc in PYINSTALLER_OPTIONS.get("excludes", []):
        cmd.extend(["--exclude-module", exc])

    # Optimization
    if PYINSTALLER_OPTIONS.get("optimize"):
        cmd.extend(["--optimize", str(PYINSTALLER_OPTIONS["optimize"])])

    # Platform-specific options
    platform_opts = PYINSTALLER_OPTIONS.get("platform_options", {}).get(sys.platform, {})

    if sys.platform == "win32":
        if platform_opts.get("console"):
            cmd.append("--console")
        if platform_opts.get("uac_admin"):
            cmd.append("--uac-admin")

    if sys.platform == "linux" and platform_opts.get("strip"):
        cmd.append("--strip")

    if sys.platform == "darwin" and platform_opts.get("osx_bundle_identifier"):
        cmd.extend(["--osx-bundle-identifier", platform_opts["osx_bundle_identifier"]])

    # UPX compression
    if USE_UPX:
        cmd.append("--upx-dir")
        if sys.platform == "win32":
            cmd.append("C:\\upx")  # Default Windows UPX path
        else:
            cmd.append("/usr/bin")  # Default Linux UPX path

    # Main script
    cmd.append("main.py")

    return cmd

# Size optimization tips
SIZE_OPTIMIZATION_TIPS = """
To reduce executable size:

1. Install UPX compressor:
   - Windows: Download from https://upx.github.io/
   - Linux: sudo apt-get install upx-ucl
   - macOS: brew install upx

2. Exclude unnecessary modules in build_config.py

3. Use --optimize=2 flag (already enabled)

4. Consider using --onedir instead of --onefile for faster startup

5. Remove unused assets from assets/ folder before building
"""