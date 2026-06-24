@echo off
title Ozone DD Dashboard — Data Updater
color 0A
echo.
echo  =====================================================
echo   Ozone Overseas - Direct Dealer Dashboard Updater
echo  =====================================================
echo.
echo  Updating dashboard with latest Excel data...
echo.

python "%~dp0update_data.py"

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  Something went wrong. See error above.
    pause
)
