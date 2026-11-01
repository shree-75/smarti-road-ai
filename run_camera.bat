@echo off
cd /d "%~dp0"
echo Starting SmartRoad AI Camera Tracker...
.\.venv\Scripts\python.exe -m ai.vision.runner
pause
