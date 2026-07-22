@echo off
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
set "INSTALL_DIR=%PROGRAMFILES%\Hum"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
echo Installing Hum executable...
copy /Y "dist\Hum.exe" "%INSTALL_DIR%\Hum.exe"

REM Create desktop shortcut (delete first so Windows doesn't reuse a cached icon)
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\Desktop\Hum.lnk"
if exist "%SHORTCUT%" del /f /q "%SHORTCUT%"
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%INSTALL_DIR%\Hum.exe'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.IconLocation='%INSTALL_DIR%\Hum.exe,0'; $s.Save()"

REM Create start menu entry
echo Creating start menu entry...
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if exist "%STARTMENU%\Hum.lnk" del /f /q "%STARTMENU%\Hum.lnk"
copy /Y "%SHORTCUT%" "%STARTMENU%\Hum.lnk"

REM Refresh Windows icon cache so the new icon shows immediately
echo Refreshing icon cache...
powershell -Command "Get-ChildItem \"$env:LOCALAPPDATA\Microsoft\Windows\Explorer\" -Filter 'iconcache*' -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue"
ie4uinit.exe -show >nul 2>&1

echo.
echo ==========================================
echo Installation complete!
echo.
echo Hum has been installed to: %INSTALL_DIR%
echo Desktop shortcut created: %USERPROFILE%\Desktop\Hum.lnk
echo.
echo You can now run Hum from:
echo - Desktop shortcut
echo - Start menu
echo - Direct path: %INSTALL_DIR%\Hum.exe
echo.
echo NOTE: If the icon still looks old, restart Windows Explorer
echo (Task Manager -^> Windows Explorer -^> Restart) or reboot.
echo ==========================================
echo.
pause
