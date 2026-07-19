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

set "BACKEND_URL="
if not exist "%CD%\workflows" (
    echo ERROR: Required workflow source folder is missing: %CD%\workflows
    pause
    exit /b 1
)

echo ===========================================================================
echo  Workflow Sync Publish
echo ===========================================================================
if not "%BACKEND_URL%"=="" (
echo  Backend URL:  %BACKEND_URL%
) else (
echo  Backend URL:  ^<from C:\Users\kengk\.ukbe-runner\config.json / CLI default^>
)
echo ===========================================================================
echo(

if exist "%~dp0.venv\Scripts\python.exe" (
    if not "%BACKEND_URL%"=="" (
        "%~dp0.venv\Scripts\python.exe" -m agent_runner_v2.sync_workflows --backend-url "%BACKEND_URL%" %*
    ) else (
        "%~dp0.venv\Scripts\python.exe" -m agent_runner_v2.sync_workflows %*
    )
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Cannot find Python or .venv\Scripts\python.exe.
        pause
        exit /b 1
    )
    if not "%BACKEND_URL%"=="" (
        python -m agent_runner_v2.sync_workflows --backend-url "%BACKEND_URL%" %*
    ) else (
        python -m agent_runner_v2.sync_workflows %*
    )
)
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
