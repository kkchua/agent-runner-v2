@echo off
REM sample-run-delivery.bat — Edit the variables below, then double-click (or run) to scaffold delivery docs.
REM
REM Typical workflow:
REM   1. Copy this file into your project
REM   2. Edit the variables below
REM   3. Double-click or run it — no command-line arguments needed

setlocal enabledelayedexpansion

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

REM Path to the agent-runner-v2 install (where ukbe-run-delivery.bat lives)
set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\VideoExpress\agent-runner-v2"

REM Workflow template group to run (e.g. delivery_scaffold_v1, delivery_planning_v1)
set "TEMPLATE_GROUP=delivery_scaffold_v1"

REM Path to the project you want to scaffold delivery docs into
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\VideoExpress"

REM Job ID to resume (leave blank to auto-create a new job)
set "JOB_ID=SCAFFOLD-GEN-20260626-001"

REM Set DRY_RUN=true to render prompts only (no coder invocation, no cost)
set "DRY_RUN=false"

REM Set NEW_JOB=true to force a fresh scaffold even if a previous job exists
set "NEW_JOB=false"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

REM --- Validate paths ---
if not exist "%AGENT_RUNNER_ROOT%\scripts\ukbe-run-delivery.bat" (
    echo ERROR: Cannot find ukbe-run-delivery.bat at %AGENT_RUNNER_ROOT%\scripts\
    echo Please update AGENT_RUNNER_ROOT in this script.
    pause
    exit /b 1
)

if not exist "%TARGET_PROJECT_ROOT%" (
    echo ERROR: Target project root does not exist: %TARGET_PROJECT_ROOT%
    echo Please update TARGET_PROJECT_ROOT in this script.
    pause
    exit /b 1
)

REM --- Build flags ---
set "FLAGS="
if /I "!DRY_RUN!"=="true" set "FLAGS=!FLAGS! --dry-run"
if /I "!NEW_JOB!"=="true" set "FLAGS=!FLAGS! --new-job"
if not "!JOB_ID!"=="" set "FLAGS=!FLAGS! --job-id !JOB_ID!"

REM --- Run ---
echo ===========================================================================
echo  Workflow: !TEMPLATE_GROUP!
echo  Target:   !TARGET_PROJECT_ROOT!
echo ===========================================================================
echo  Agent-runner:   !AGENT_RUNNER_ROOT!
if not "!JOB_ID!"=="" echo  Job ID:          !JOB_ID!
echo  Dry run:        !DRY_RUN!
echo  New job:        !NEW_JOB!
echo ===========================================================================
echo(

call "!AGENT_RUNNER_ROOT!\scripts\ukbe-run-delivery.bat" ^
    --project-root "!AGENT_RUNNER_ROOT!" ^
    --template-group "!TEMPLATE_GROUP!" ^
    --target-project-root "!TARGET_PROJECT_ROOT!" ^
    !FLAGS!

set "EXIT_CODE=!ERRORLEVEL!"

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Workflow finished with errors (exit code !EXIT_CODE!).
echo Check !TARGET_PROJECT_ROOT!\docs\delivery\ for partial output.
pause
exit /b !EXIT_CODE!

:success
echo(
echo Workflow completed successfully.
exit /b 0
