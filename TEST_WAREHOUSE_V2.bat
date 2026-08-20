@echo off
setlocal
cd /d "%~dp0"
title NinjaClaat - Warehouse V2 Test

echo ==============================================
echo       NINJACLAAT - WAREHOUSE V2 TEST
echo ==============================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY=python"
  ) else (
    echo Python was not found on this computer.
    echo Install Python, then run this launcher again.
    pause
    exit /b 1
  )
)

echo Preparing Warehouse V2...
%PY% warehouse_v2\apply_warehouse_v2.py
if errorlevel 1 (
  echo.
  echo Warehouse V2 could not be prepared.
  echo The original game files were left backed up by the installer.
  pause
  exit /b 1
)

echo.
echo Starting local NinjaClaat test server...
start "NinjaClaat Warehouse V2 Server" /min cmd /c "%PY% -m http.server 8000"
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/warehouse_v2/warehouse_test.html"

echo.
echo Warehouse V2 is opening in your browser.
echo You can close this window.
timeout /t 3 /nobreak >nul
exit /b 0
