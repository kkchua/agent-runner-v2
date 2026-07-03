@echo off
setlocal

rem Delegate to PowerShell so Ctrl+C behaves predictably during pytest runs.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test-runner.ps1" %*
exit /b %ERRORLEVEL%
