@echo off
REM Run unit tests for agent-runner-v2
setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

echo ========================================
echo Running Agent-Runner-V2 Unit Tests
echo ========================================
echo.

python -m pytest tests/unit/ -v --tb=short

echo.
echo ========================================
echo Unit test run complete
echo ========================================
