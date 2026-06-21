@echo off
title Build ThereQuickActions EXE

echo.
echo ================================================
echo Building ThereQuickActions.exe
echo ================================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher "py" was not found.
    echo Install Python from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

py -m pip install --upgrade pyinstaller pillow pystray

if errorlevel 1 (
    echo.
    echo Dependency install failed.
    pause
    exit /b 1
)

if exist TQA.ico (
    py -m PyInstaller --noconsole --onefile --name ThereQuickActions --uac-admin --icon TQA.ico --add-data "TQA.ico;." --add-data "TQA.png;." --add-data "kofi.png;." ThereQuickActions_v3_0.py
) else if exist TQA.png (
    py -m PyInstaller --noconsole --onefile --name ThereQuickActions --uac-admin --icon TQA.png --add-data "TQA.png;." --add-data "kofi.png;." ThereQuickActions_v3_0.py
) else (
    py -m PyInstaller --noconsole --onefile --name ThereQuickActions --uac-admin ThereQuickActions_v3_0.py
)

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo DONE.
echo Your EXE is here:
echo dist\ThereQuickActions.exe
echo.
pause
