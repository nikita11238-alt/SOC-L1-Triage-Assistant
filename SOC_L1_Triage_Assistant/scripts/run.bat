@echo off
cd /d "%~dp0.."

echo ===============================
echo    SOC L1 Triage Assistant
echo ===============================
echo.

:: Определяем как запускать Python - python или py
set PYTHON=
python --version >nul 2>&1
if not errorlevel 1 set PYTHON=python

if "%PYTHON%"=="" (
    py --version >nul 2>&1
    if not errorlevel 1 set PYTHON=py
)

if "%PYTHON%"=="" (
    echo [ERROR] Python not found!
    echo Download: https://python.org
    echo During install: check "Add Python to PATH"
    pause
    exit /b 1
)

echo [+] Using: %PYTHON%
echo.

if exist "output\final_report.txt" (
    echo [!] Previous report will be saved to output\archive\
    echo.
)

echo [*] Step 1/4 - Parsing logs...
%PYTHON% scripts\triage.py
if errorlevel 1 (
    echo.
    echo [ERROR] Put log files into the logs\ folder and try again
    pause
    exit /b 1
)

echo.
echo [*] Step 2/4 - Scoring severity...
%PYTHON% scripts\severity.py
if errorlevel 1 ( echo [ERROR] severity.py failed & pause & exit /b 1 )

echo.
echo [*] Step 3/4 - Generating report...
%PYTHON% scripts\report.py
if errorlevel 1 ( echo [ERROR] report.py failed & pause & exit /b 1 )

echo.
echo [*] Step 4/4 - Adding assessment...
%PYTHON% scripts\ai_explainer.py
if errorlevel 1 ( echo [ERROR] ai_explainer.py failed & pause & exit /b 1 )

echo.
echo ===============================
echo [OK] DONE - Opening report...
echo ===============================
echo.

start notepad "output\final_report.txt"
