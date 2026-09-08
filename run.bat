@echo off
setlocal
cd /d %~dp0

if not exist .venv\Scripts\python.exe (
    echo [ERROR] .venv fehlt. Bitte zuerst install.bat starten.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python app.py

if errorlevel 1 (
    echo.
    echo Programm wurde mit einem Fehler beendet.
    echo Kopiere die Fehlermeldung und sende sie mir.
    pause
)
