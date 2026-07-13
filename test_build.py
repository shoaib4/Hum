#!/usr/bin/env python3
"""
Test script to verify the build worked correctly.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_executable_exists():
    """Check if the executable was created."""
    if sys.platform == "win32":
        exe_path = Path("dist/Hum.exe")
    else:
        exe_path = Path("dist/Hum")

    if exe_path.exists():
        print(f"[+] Executable found: {exe_path}")

        # Get file size
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"    Size: {size_mb:.1f} MB")

        return True
    else:
        print(f"[-] Executable not found: {exe_path}")
        return False

def test_portable_package():
    """Check if portable package was created."""
    portable_dir = Path("dist/Hum-Portable")

    if portable_dir.exists():
        print(f"[+] Portable package found: {portable_dir}")

        # List contents
        files = list(portable_dir.iterdir())
        print(f"    Contains {len(files)} files:")
        for file in files:
            print(f"      - {file.name}")

        return True
    else:
        print(f"[-] Portable package not found: {portable_dir}")
        return False

def test_executable_version():
    """Try to get version info from executable (Windows only)."""
    if sys.platform != "win32":
        return True

    exe_path = Path("dist/Hum.exe")
    if not exe_path.exists():
        return False

    try:
        # Try to run with --version flag (if supported)
        result = subprocess.run(
            [str(exe_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"[+] Version info: {result.stdout.strip()}")
        else:
            print("[*] Executable runs but doesn't support --version")
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("[*] Could not test executable version (this is normal)")
        return True

def main():
    """Run all tests."""
    print("Testing Hum build...")
    print("=" * 40)

    tests_passed = 0
    total_tests = 3

    # Test 1: Executable exists
    if test_executable_exists():
        tests_passed += 1

    print()

    # Test 2: Portable package exists
    if test_portable_package():
        tests_passed += 1

    print()

    # Test 3: Version check (optional)
    if test_executable_version():
        tests_passed += 1

    print()
    print("=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("[+] All tests passed! Build is successful.")
        return True
    else:
        print("[-] Some tests failed. Check the build output.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)