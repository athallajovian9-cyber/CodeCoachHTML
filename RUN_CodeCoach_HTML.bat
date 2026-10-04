@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found on PATH.
    pause
    exit /b 1
)

set TARGET=%~1
if "%TARGET%"=="" set TARGET=%~dp0kidcode

if not exist "%TARGET%" (
    mkdir "%TARGET%" 2>nul
    echo.
    echo   Made a folder called kidcode. Put your kid's HTML files in there!
    echo   Or drag any folder onto this file.
    echo.
    pause
    exit /b 0
)

echo.
echo   CodeCoach HTML is watching:
echo     %TARGET%
echo.
echo   Save a file and this refreshes. Ctrl-C to stop.
echo.
python "htmlcoach.py" --watch --folder "%TARGET%"
pause
exit /b 0
