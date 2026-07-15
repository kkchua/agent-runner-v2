@echo off
REM Run ALL tests (unit + integration) for agent-runner-v2
setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

echo ========================================
echo Running ALL Agent-Runner-V2 Tests
echo ========================================
echo.

echo Running Unit Tests...
python -m pytest tests/unit/ -v --tb=short
if errorlevel 1 (
    echo.
    echo WARNING: Some unit tests failed!
    echo.
)

echo.
echo Running Integration Tests...
python -m pytest tests/integration/ -v --tb=short
if errorlevel 1 (
    echo.
    echo WARNING: Some integration tests failed!
    echo.
)

echo.
echo ========================================
echo All tests complete
echo ========================================
