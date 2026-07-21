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

REM Copy whisper_cpp folder
echo Installing whisper server...
if not exist "%INSTALL_DIR%\whisper_cpp" mkdir "%INSTALL_DIR%\whisper_cpp"
xcopy /Y /E "whisper_cpp\*" "%INSTALL_DIR%\whisper_cpp\" >nul

REM Copy models folder
echo Installing model files...
if not exist "%INSTALL_DIR%\models" mkdir "%INSTALL_DIR%\models"
xcopy /Y /E "models\*" "%INSTALL_DIR%\models\" >nul

REM Create desktop shortcut
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\Desktop\Hum.lnk"
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%INSTALL_DIR%\Hum.exe'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.Save()"

REM Create start menu entry
echo Creating start menu entry...
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
copy /Y "%SHORTCUT%" "%STARTMENU%\Hum.lnk"

echo.
echo ==========================================
echo Installation complete!
echo.
echo Hum has been installed to: %INSTALL_DIR%
echo Desktop shortcut created: %USERPROFILE%\Desktop\Hum.lnk
echo.
echo Installed files:
echo   %INSTALL_DIR%\Hum.exe
echo   %INSTALL_DIR%\whisper_cpp\whisper-server.exe
echo   %INSTALL_DIR%\models\*.bin
echo.
echo You can now run Hum from:
echo - Desktop shortcut
echo - Start menu
echo - Direct path: %INSTALL_DIR%\Hum.exe
echo ==========================================
echo.
pause
