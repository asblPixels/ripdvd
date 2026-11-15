@echo off
REM ============================================================
REM  RipDvD - Windows Installer (double-click to run)
REM  No technical knowledge required!
REM ============================================================
title RipDvD Installer
color 0A

echo.
echo  ============================================
echo   RipDvD - Windows Installer
echo   From disc to digital - effortlessly
echo  ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python is not installed.
    echo.
    echo  Please install Python first:
    echo  1. Go to https://www.python.org/downloads/
    echo  2. Download Python 3.x
    echo  3. Run the installer
    echo  4. CHECK "Add Python to PATH"
    echo  5. Come back and run this installer again
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)
echo  [OK] Python found.
python --version

REM Check HandBrakeCLI
where HandBrakeCLI >nul 2>&1
if %errorlevel% neq 0 (
    if not exist "C:\Program Files\HandBrake\HandBrakeCLI.exe" (
        if not exist "C:\Program Files (x86)\HandBrake\HandBrakeCLI.exe" (
            echo.
            echo  [!] HandBrake is not installed.
            echo.
            echo  Please install HandBrake first:
            echo  1. Go to https://handbrake.fr/downloads.php
            echo  2. Download HandBrake for Windows
            echo  3. Run the installer (default location is fine)
            echo  4. Come back and run this installer again
            echo.
            pause
            start https://handbrake.fr/downloads.php
            exit /b 1
        )
    )
)
echo  [OK] HandBrake found.

REM Create output directory
if not exist "%USERPROFILE%\Videos\Rips" (
    mkdir "%USERPROFILE%\Videos\Rips"
    echo  [OK] Created output folder: %USERPROFILE%\Videos\Rips
)

REM Create install directory
if not exist "%LOCALAPPDATA%\RipDvD" (
    mkdir "%LOCALAPPDATA%\RipDvD"
)
copy /Y "src\ripdvd-win.py" "%LOCALAPPDATA%\RipDvD\ripdvd.py" >nul
echo  [OK] Installed RipDvD to %LOCALAPPDATA%\RipDvD\

REM Create Desktop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\mkshortcut.vbs"
echo sLinkFile = "%USERPROFILE%\Desktop\RipDvD.lnk" >> "%TEMP%\mkshortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\mkshortcut.vbs"
echo oLink.TargetPath = "python" >> "%TEMP%\mkshortcut.vbs"
echo oLink.Arguments = Chr(34) ^& "%LOCALAPPDATA%\RipDvD\ripdvd.py" ^& Chr(34) >> "%TEMP%\mkshortcut.vbs"
echo oLink.WorkingDirectory = "%LOCALAPPDATA%\RipDvD" >> "%TEMP%\mkshortcut.vbs"
echo oLink.Description = "RipDvD - DVD Ripper" >> "%TEMP%\mkshortcut.vbs"
echo oLink.Save >> "%TEMP%\mkshortcut.vbs"
cscript //nologo "%TEMP%\mkshortcut.vbs"
del "%TEMP%\mkshortcut.vbs"
echo  [OK] Desktop shortcut created.

REM Create Start Menu entry
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\RipDvD" (
    mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\RipDvD"
)
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\mkshortcut2.vbs"
echo sLinkFile = "%APPDATA%\Microsoft\Windows\Start Menu\Programs\RipDvD\RipDvD.lnk" >> "%TEMP%\mkshortcut2.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\mkshortcut2.vbs"
echo oLink.TargetPath = "python" >> "%TEMP%\mkshortcut2.vbs"
echo oLink.Arguments = Chr(34) ^& "%LOCALAPPDATA%\RipDvD\ripdvd.py" ^& Chr(34) >> "%TEMP%\mkshortcut2.vbs"
echo oLink.WorkingDirectory = "%LOCALAPPDATA%\RipDvD" >> "%TEMP%\mkshortcut2.vbs"
echo oLink.Description = "RipDvD - DVD Ripper" >> "%TEMP%\mkshortcut2.vbs"
echo oLink.Save >> "%TEMP%\mkshortcut2.vbs"
cscript //nologo "%TEMP%\mkshortcut2.vbs"
del "%TEMP%\mkshortcut2.vbs"
echo  [OK] Start Menu entry created.

echo.
echo  ============================================
echo   Installation complete!
echo  ============================================
echo.
echo  A shortcut "RipDvD" has been created on your Desktop.
echo  Double-click it to start ripping DVDs!
echo.
echo  Your ripped DVDs will be saved to:
echo  %USERPROFILE%\Videos\Rips
echo.
pause
