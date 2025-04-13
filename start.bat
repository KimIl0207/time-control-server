@echo off
echo 시스템 시작
start "" /min pythonw.exe server.py
timeout /t 2 > nul
start "" /min python shutDownManager.py