@echo off
REM run-daemon.bat - Edit the variables below, then run in a console window.
REM
REM Starts the backend-connected workstation daemon in the foreground:
REM   .venv\Scripts\python.exe -m agent_runner_v2.run_agent daemon [worker_id]
REM
REM Typical workflow:
REM   1. Edit the variables below
REM   2. Run this batch file and keep the console open
REM   3. Submit jobs with submit-10_execution_scaffold_v1.bat

setlocal enabledelayedexpansion

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

REM Path to the agent-runner-v2 install / working directory
set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"

REM Optional daemon identity and routing
REM set "WORKER_ID=kode-worker-01"
set "WORKER_LABEL=live"
set "BACKEND_URL="

REM Optional daemon tuning (leave blank to use config.json / CLI defaults)
set "STEP_SPEC_SOURCE=backend"
set "POLL_SECONDS="
set "MAX_PARALLEL="
set "RUNTIME_DIR="
set "LOG_FILE="
set "STALLED_SECONDS="
set "STEP_TIMEOUT_SECONDS="
set "KILL_GRACE_SECONDS="

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent-runner root does not exist: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

set "VENV_PYTHON=%AGENT_RUNNER_ROOT%\.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    echo ERROR: Repo venv Python not found: %VENV_PYTHON%
    echo Create the repo venv and install editable first:
    echo   .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
    pause
    exit /b 1
)

set "FLAGS="
if not "!WORKER_LABEL!"=="" set "FLAGS=!FLAGS! --worker-label !WORKER_LABEL!"
if not "!BACKEND_URL!"=="" set "FLAGS=!FLAGS! --backend-url !BACKEND_URL!"
if not "!STEP_SPEC_SOURCE!"=="" set "FLAGS=!FLAGS! --step-spec-source !STEP_SPEC_SOURCE!"
if not "!POLL_SECONDS!"=="" set "FLAGS=!FLAGS! --poll-seconds !POLL_SECONDS!"
if not "!MAX_PARALLEL!"=="" set "FLAGS=!FLAGS! --max-parallel !MAX_PARALLEL!"
if not "!RUNTIME_DIR!"=="" set "FLAGS=!FLAGS! --runtime-dir ""!RUNTIME_DIR!"""
if not "!LOG_FILE!"=="" set "FLAGS=!FLAGS! --log-file ""!LOG_FILE!"""
if not "!STALLED_SECONDS!"=="" set "FLAGS=!FLAGS! --stalled-seconds !STALLED_SECONDS!"
if not "!STEP_TIMEOUT_SECONDS!"=="" set "FLAGS=!FLAGS! --step-timeout-seconds !STEP_TIMEOUT_SECONDS!"
if not "!KILL_GRACE_SECONDS!"=="" set "FLAGS=!FLAGS! --kill-grace-seconds !KILL_GRACE_SECONDS!"

echo ===========================================================================
echo  Mode:            Daemon Supervisor
echo  Agent-runner:    !AGENT_RUNNER_ROOT!
echo  Python:          !VENV_PYTHON!
if not "!WORKER_ID!"=="" (
echo  Worker ID:       !WORKER_ID!
) else (
echo  Worker ID:       ^<from config.json / CLI default^>
)
if not "!WORKER_LABEL!"=="" (
echo  Worker Label:    !WORKER_LABEL!
) else (
echo  Worker Label:    ^<from config.json / CLI default^>
)
if not "!BACKEND_URL!"=="" (
echo  Backend URL:     !BACKEND_URL!
) else (
echo  Backend URL:     ^<from C:\Users\kengk\.ukbe-runner\config.json / CLI default^>
)
if not "!STEP_SPEC_SOURCE!"=="" (
echo  Step Spec:       !STEP_SPEC_SOURCE!
) else (
echo  Step Spec:       ^<from config.json / CLI default^>
)
echo ===========================================================================
echo(

pushd "%AGENT_RUNNER_ROOT%"
if not "!WORKER_ID!"=="" (
    call "!VENV_PYTHON!" -m agent_runner_v2.run_agent daemon "!WORKER_ID!" !FLAGS!
) else (
    call "!VENV_PYTHON!" -m agent_runner_v2.run_agent daemon !FLAGS!
)
set "EXIT_CODE=!ERRORLEVEL!"
popd

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Daemon exited with code !EXIT_CODE!.
pause
exit /b !EXIT_CODE!

:success
echo(
echo Daemon stopped normally.
exit /b 0

