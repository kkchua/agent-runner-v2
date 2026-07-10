@echo off
REM sync-workflows-to-backend.bat - Publish runner workflow definitions into the backend registry.
REM
REM This is a thin wrapper around the backend sync command so you can run the
REM publish flow from the runner repo without switching directories.
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

REM Ensure Python is in PATH for backend scripts
if not defined PYTHON (
    where python >nul 2>&1 && set "PYTHON=python" || echo WARNING: python not found in PATH
)

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "BACKEND_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-backend"
set "BACKEND_SYNC_BAT=%BACKEND_ROOT%\sync-workflows.bat"

REM Optional override for the backend URL used by the backend sync helper.
set "BACKEND_URL=http://127.0.0.1:8100"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent-runner root does not exist: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

if not exist "%BACKEND_ROOT%" (
    echo ERROR: Backend root does not exist: %BACKEND_ROOT%
    pause
    exit /b 1
)

if not exist "%BACKEND_SYNC_BAT%" (
    echo ERROR: Backend sync launcher does not exist: %BACKEND_SYNC_BAT%
    pause
    exit /b 1
)

set "ARGS="
if not "%~1"=="" (
    :collect_args
    if "%~1"=="" goto :args_done
    set "ARGS=!ARGS! "%~1""
    shift
    goto :collect_args
)

:args_done
echo ===========================================================================
echo  Workflow Sync Publish
echo ===========================================================================
echo  Runner Root:    %AGENT_RUNNER_ROOT%
echo  Backend Root:   %BACKEND_ROOT%
echo  Backend URL:     %BACKEND_URL%
if not "!ARGS!"=="" (
    echo  Workflows:      !ARGS!
) else (
    echo  Workflows:      ^<all^>
)
echo ===========================================================================
echo(

REM Use .venv Python to directly call the backend's sync script
pushd "%BACKEND_ROOT%"
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" sync-workflows.py --backend-url "%BACKEND_URL%" %*
) else (
    python sync-workflows.py --backend-url "%BACKEND_URL%" %*
)
set "EXIT_CODE=!ERRORLEVEL!"
popd

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Workflow publish failed (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!

:success
echo(
echo Workflow definitions published successfully.
exit /b 0
