@echo off
REM submit-documentation_validation_v1.bat - Edit the variables below, then run.
REM
REM Submits a new backend job for the documentation_validation_v1 workflow.

setlocal enabledelayedexpansion

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "WORKFLOW_NAME=documentation_validation_v1"
set "PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "WORKER_LABEL=live"
set "WORKER_ID="
set "BACKEND_URL=http://127.0.0.1:8100"
set "CODER="

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent-runner root does not exist: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%" (
    echo ERROR: Project root does not exist: %PROJECT_ROOT%
    pause
    exit /b 1
)

if not exist "%TARGET_PROJECT_ROOT%" (
    echo ERROR: Target project root does not exist: %TARGET_PROJECT_ROOT%
    pause
    exit /b 1
)

where ukbe-run-agent >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot find ukbe-run-agent on PATH.
    pause
    exit /b 1
)

set "FLAGS="
if not "!WORKER_LABEL!"=="" set "FLAGS=!FLAGS! --worker-label !WORKER_LABEL!"
if not "!WORKER_ID!"=="" set "FLAGS=!FLAGS! --worker-id !WORKER_ID!"
if not "!BACKEND_URL!"=="" set "FLAGS=!FLAGS! --backend-url !BACKEND_URL!"
if not "!CODER!"=="" set "FLAGS=!FLAGS! --coder !CODER!"

pushd "%AGENT_RUNNER_ROOT%"
call ukbe-run-agent submit ^
    --workflow-name "!WORKFLOW_NAME!" ^
    --project-root "!PROJECT_ROOT!" ^
    --target-project-root "!TARGET_PROJECT_ROOT!" !FLAGS!
set "EXIT_CODE=!ERRORLEVEL!"
popd

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Job submission failed (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!

:success
echo(
echo Job submitted successfully.
exit /b 0