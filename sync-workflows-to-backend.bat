@echo off
REM sync-workflows-to-backend.bat - Publish runner workflow definitions into the backend registry.
REM
REM Discovers workflows from both TEMPLATE_GROUPS (bootstrap) and plugin
REM workflow.toml packages in workflows/<name>/.  Each definition is POSTed
REM to the backend API at /api/admin/workflows/sync.
REM
REM Usage:
REM   sync-workflows-to-backend.bat
REM   sync-workflows-to-backend.bat codebase_bootstrap_v1
REM   sync-workflows-to-backend.bat delivery_scaffold_v1 bug_fix_v1

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "BACKEND_URL=http://127.0.0.1:8100"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent-runner root does not exist: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

echo ===========================================================================
echo  Workflow Sync Publish
echo ===========================================================================
echo  Backend URL:  %BACKEND_URL%
echo ===========================================================================
echo(

REM Use .venv Python to call the runner-side sync script
"%~dp0.venv\Scripts\python.exe" -m agent_runner_v2.sync_workflows --backend-url "%BACKEND_URL%" %*
set "EXIT_CODE=!ERRORLEVEL!"

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Workflow publish failed (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!

:success
echo(
echo Workflow definitions published successfully.
exit /b 0
