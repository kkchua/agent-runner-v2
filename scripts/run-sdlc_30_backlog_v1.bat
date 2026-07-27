@echo off
REM run-sdlc_30_backlog_v1.bat - Edit the variables below, then double-click (or run).
REM
REM Runs ukbe-run-agent for the sdlc_30_backlog_v1 workflow (plugin package):
REM   Generates backlog from approved plan document.
REM   Loads the workflow definition from workflows/sdlc_30_backlog_v1/workflow.toml.
REM
REM Runtime jobs and sidecars are stored under %USERPROFILE%\.ukbe-runner\jobs\
REM
REM Typical workflow:
REM   1. Edit the variables below (especially PLAN_FILE)
REM   2. Double-click or run it

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

REM Workflow template group (loaded from workflows/<name>/workflow.toml)
set "TEMPLATE_GROUP=sdlc_30_backlog_v1"

REM Job ID to resume (leave blank to auto-create a new job)
set "JOB_ID="

REM Set DRY_RUN=true to render prompts only (no coder invocation)
set "DRY_RUN=false"

REM Set NEW_JOB=true only when you intentionally want a fresh run
set "NEW_JOB=false"

REM Set MODE=manual/daemon
set "MODE=manual"
set "JOB_NO="

REM Approved plan document (filename only, e.g., PLAN-20260722-001_console-sdlc10-support.md)
REM Must exist in docs/repo/agent_runner/sdlc/delivery/20_plans/
set "PLAN_FILE=PLAN-20260722-001_console-sdlc10-support.md"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

REM --- Validate ---
where ukbe-run-agent >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot find ukbe-run-agent on PATH.
    echo Install the package first, for example: pip install -e .
    pause
    exit /b 1
)

REM --- Build flags ---
set "FLAGS="
if /I "!DRY_RUN!"=="true" set "FLAGS=!FLAGS! --dry-run"
if /I "!NEW_JOB!"=="true" set "FLAGS=!FLAGS! --new-job"

if not "!JOB_ID!"=="" set "FLAGS=!FLAGS! --job-id !JOB_ID!"

set "FLAGS=!FLAGS! --mode !MODE!"
if not "!JOB_NO!"=="" set "FLAGS=!FLAGS! --job-no !JOB_NO!"

REM --- Build --set flags for seed artifacts ---
set "SEED_FLAGS="
if not "!PLAN_FILE!"=="" (
    set "PLAN_PATH=%CD%\docs\repo\agent_runner\sdlc\delivery\20_plans\!PLAN_FILE!"
    if not exist "!PLAN_PATH!" (
        echo ERROR: Plan file not found: !PLAN_PATH!
        pause
        exit /b 1
    )
    set "SEED_FLAGS=--set PLAN_FILE=!PLAN_PATH!"
)

REM --- Run ---
echo ===========================================================================
echo  Workflow: !TEMPLATE_GROUP!
echo  Repo:     %CD%
echo ===========================================================================
if not "!JOB_ID!"=="" echo  Job ID:          !JOB_ID!
if not "!PLAN_FILE!"=="" echo  Plan File:       !PLAN_FILE!
echo  Dry run:        !DRY_RUN!
echo  New job:        !NEW_JOB!
echo ===========================================================================
echo(

ukbe-run-agent run ^
    --template-group "!TEMPLATE_GROUP!" ^
    !FLAGS! ^
    !SEED_FLAGS!

set "EXIT_CODE=!ERRORLEVEL!"

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Workflow finished with errors (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!

:success
echo(
if not "!JOB_ID!"=="" (
    if not exist "%CD%\temp" mkdir "%CD%\temp" >nul 2>nul
    set "STATUS_FILE=%CD%\temp\run-sdlc-30-backlog-status-!RANDOM!.txt"
    ukbe-run-agent run --template-group "!TEMPLATE_GROUP!" --job-id "!JOB_ID!" --check-job-status > "!STATUS_FILE!"
    set "STATUS_EXIT=!ERRORLEVEL!"
    if "!STATUS_EXIT!"=="0" (
        set "JOB_STATUS="
        for /f "tokens=1,* delims=:" %%A in ('findstr /B /C:"Status:" "!STATUS_FILE!"') do set "JOB_STATUS=%%B"
        set "JOB_STATUS=!JOB_STATUS: =!"
        if /I "!JOB_STATUS!"=="COMPLETED" (
            echo Workflow completed successfully.
        ) else (
            echo Workflow command completed. Job status: !JOB_STATUS!
        )
        del "!STATUS_FILE!" >nul 2>nul
        exit /b 0
    )
    del "!STATUS_FILE!" >nul 2>nul
)
echo Workflow command completed successfully.
exit /b 0
