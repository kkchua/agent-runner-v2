@echo off
REM submit-sdlc_80_review_v1.bat - Edit the variables below, then run.
REM
REM Submits a new backend job for the sdlc_80_review_v1 workflow:
REM   ukbe-run-agent submit --workflow-name sdlc_80_review_v1 ...
REM
REM This workflow generates review, memory, and closure documents from
REM approved validation, producing approved REV_FILE, MEM_FILE, and CLOSE_FILE.

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "WORKFLOW_NAME=sdlc_80_review_v1"
set "INITIATIVE_ID="
set "WORKER_LABEL=live"
set "WORKER_ID="
set "BACKEND_URL="
set "CODER="

REM Approved validation document (filename only, e.g., VAL-20260722-001_console-sdlc10-support.md)
REM Must exist in docs/repo/agent_runner/sdlc/delivery/70_validations/
set "VAL_FILE=VAL-20260722-001_console-sdlc10-support.md"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

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

REM --- Build --input flags for seed artifacts ---
set "INPUT_FLAGS="
if not "!VAL_FILE!"=="" (
    set "VAL_PATH=%~dp0docs\repo\agent_runner\sdlc\delivery\70_validations\!VAL_FILE!"
    if not exist "!VAL_PATH!" (
        echo ERROR: Validation file not found: !VAL_PATH!
        pause
        exit /b 1
    )
    set "INPUT_FLAGS=--input VAL_FILE=!VAL_PATH!"
)

echo ===========================================================================
echo  Workflow:        !WORKFLOW_NAME!
echo  Repository Root: %~dp0
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
if not "!VAL_FILE!"=="" echo  Val File:        !VAL_FILE!
echo ===========================================================================
echo(

call ukbe-run-agent submit ^
    --workflow-name "!WORKFLOW_NAME!" ^
    !FLAGS! ^
    !INPUT_FLAGS!
set "EXIT_CODE=!ERRORLEVEL!"

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Job submission failed (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!

:success
echo(
echo Job submitted successfully.
exit /b 0
