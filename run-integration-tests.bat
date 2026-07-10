@echo off
REM Run integration tests for agent-runner-v2
setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

echo ========================================
echo Running Agent-Runner-V2 Integration Tests
echo ========================================
echo.
echo NOTE: Integration tests may require:
echo   - Network access (for API calls)
echo   - Pushover credentials (.env file)
echo   - File system permissions
echo.

python -m pytest tests/integration/ -v --tb=short

echo.
echo ========================================
echo Integration test run complete
echo ========================================
