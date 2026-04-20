@echo off
cd /d "%~dp0"
"C:\ProgramData\anaconda3\python.exe" main.py
if %errorlevel% neq 0 pause
exit
