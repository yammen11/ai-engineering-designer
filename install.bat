@echo off
setlocal
cd /d %~dp0

echo ============================================
echo AI Engineering Designer v0.1 - Installation
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python Launcher "py" wurde nicht gefunden.
    echo Bitte Python 3.11 64-bit installieren.
    pause
    exit /b 1
)

echo [1/4] Virtuelle Umgebung mit Python 3.11...
py -3.11 -m venv .venv
if errorlevel 1 (
    echo.
    echo [ERROR] Python 3.11 wurde nicht gefunden.
    echo Bitte Python 3.11 64-bit installieren.
    pause
    exit /b 1
)

echo [2/4] Umgebung aktivieren...
call .venv\Scripts\activate.bat

echo [3/4] pip aktualisieren...
python -m pip install --upgrade pip

echo [4/4] Bibliotheken installieren...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Installation fehlgeschlagen.
    echo Kopiere die komplette Fehlermeldung und sende sie mir.
    pause
    exit /b 1
)

if not exist .env (
    copy .env.example .env >nul
)

echo.
echo ============================================
echo Installation fertig.
echo 1. OPENAI_API_KEY in .env eintragen
echo 2. run.bat starten
echo ============================================
pause
