@echo off
setlocal enabledelayedexpansion

if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "WORKFLOW_NAME=00_bootstrap_lifecycle_admin_v1"
set "PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "WORKER_LABEL=live"
set "WORKER_ID="
set "BACKEND_URL="

set "FLAGS="
if not "!WORKER_LABEL!"=="" set "FLAGS=!FLAGS! --worker-label !WORKER_LABEL!"
if not "!WORKER_ID!"=="" set "FLAGS=!FLAGS! --worker-id !WORKER_ID!"
if not "!BACKEND_URL!"=="" set "FLAGS=!FLAGS! --backend-url !BACKEND_URL!"

pushd "%AGENT_RUNNER_ROOT%"
call ukbe-run-agent submit ^
    --workflow-name "!WORKFLOW_NAME!" ^
    --project-root "!PROJECT_ROOT!" ^
    --target-project-root "!TARGET_PROJECT_ROOT!" !FLAGS!
set "EXIT_CODE=!ERRORLEVEL!"
popd

if "!EXIT_CODE!"=="0" exit /b 0
echo(
echo Job submission failed (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!
