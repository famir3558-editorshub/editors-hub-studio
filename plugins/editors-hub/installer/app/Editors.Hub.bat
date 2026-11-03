@echo off
rem Double-click on Windows: starts Editors.Hub and opens Home in your browser.
cd /d "%~dp0"
where py >nul 2>nul && (py studio.py open --browser & goto :eof)
where python >nul 2>nul && (python studio.py open --browser & goto :eof)
echo Editors.Hub needs Python 3: https://www.python.org/downloads/  (tick "Add python.exe to PATH")
pause
