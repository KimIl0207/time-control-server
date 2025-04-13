@echo off
for /f "delims=" %%i in ('where pythonw') do (
    set PYW=%%i
    goto run
)

:run
echo [LOG] 실행 경로: %PYW%
start "" "%PYW%" shutDownManager.py