@echo off
REM 00_repo_master_docs_bootstrap_v1.bat - Edit the variables below, then run.
REM
REM Submits a new backend job for the 00_repo_master_docs_bootstrap_v1 workflow:
REM   ukbe-run-agent submit --workflow-name 00_repo_master_docs_bootstrap_v1 ...

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "WORKFLOW_NAME=00_repo_master_docs_bootstrap_v1"
set "PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "INITIATIVE_ID="
set "WORKER_LABEL=live"
set "WORKER_ID="
set "BACKEND_URL="
set "CODER="

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

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
    echo Install the package first, for example: pip install -e .
    pause
    exit /b 1
)

set "FLAGS="
if not "!INITIATIVE_ID!"=="" set "FLAGS=!FLAGS! --initiative-id !INITIATIVE_ID!"
if not "!WORKER_LABEL!"=="" set "FLAGS=!FLAGS! --worker-label !WORKER_LABEL!"
if not "!WORKER_ID!"=="" set "FLAGS=!FLAGS! --worker-id !WORKER_ID!"
if not "!BACKEND_URL!"=="" set "FLAGS=!FLAGS! --backend-url !BACKEND_URL!"
if not "!CODER!"=="" set "FLAGS=!FLAGS! --coder !CODER!"

echo ===========================================================================
echo  Workflow:        !WORKFLOW_NAME!
echo  Agent-runner:    !AGENT_RUNNER_ROOT!
echo  Project Root:    !PROJECT_ROOT!
echo  Target Root:     !TARGET_PROJECT_ROOT!
echo  Routing:         Queue label
if not "!WORKER_LABEL!"=="" (
echo  Worker Label:    !WORKER_LABEL!
) else (
echo  Worker Label:    ^<from config.json / CLI default^>
)
if not "!WORKER_ID!"=="" (
echo  Worker ID:       !WORKER_ID!
) else (
echo  Worker ID:       ^<not pinned^>
)
if not "!BACKEND_URL!"=="" (
echo  Backend URL:     !BACKEND_URL!
) else (
echo  Backend URL:     ^<from C:\Users\kengk\.ukbe-runner\config.json / CLI default^>
)
echo ===========================================================================
echo(

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
