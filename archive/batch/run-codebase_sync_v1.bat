@echo off
REM run-codebase_sync_v1.bat - Legacy alias for codebase bootstrap/reconcile runs.
REM
REM Runs the codebase documentation workflow against a target repository:
REM   - codebase_bootstrap_v1: initial scan/bootstrap of /docs/codebase
REM   - codebase_reconcile_v1: follow-up scan to reconcile drift
REM
REM Prefer using:
REM   - run-codebase_bootstrap_v1.bat
REM   - run-codebase_reconcile_v1.bat
REM
REM Typical workflow:
REM   1. Edit the variables below
REM   2. Set TEMPLATE_GROUP to codebase_bootstrap_v1 for the first baseline
REM      or codebase_reconcile_v1 for an ad hoc refresh
REM   3. Double-click or run it

setlocal enabledelayedexpansion

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

REM Path to the agent-runner-v2 install (where the CLI lives)
set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"

REM Workflow template group
set "TEMPLATE_GROUP=codebase_reconcile_v1"

REM Path to the project whose /docs/codebase tree you want to update
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"

REM Job ID to resume (leave blank to auto-create a new job)
set "JOB_ID=CDRECON-GEN-20260630-001"

REM Set DRY_RUN=true to render prompts only (no coder invocation)
set "DRY_RUN=false"

REM Set NEW_JOB=true to force a fresh run even if a previous job exists
set "NEW_JOB=false"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

if not exist "%AGENT_RUNNER_ROOT%\scripts\ukbe-run-delivery.bat" (
    echo ERROR: Cannot find ukbe-run-delivery.bat at %AGENT_RUNNER_ROOT%\scripts\
    pause
    exit /b 1
)

if not exist "%TARGET_PROJECT_ROOT%" (
    echo ERROR: Target project root does not exist: %TARGET_PROJECT_ROOT%
    pause
    exit /b 1
)

set "FLAGS="
if /I "!DRY_RUN!"=="true" set "FLAGS=!FLAGS! --dry-run"
if /I "!NEW_JOB!"=="true" set "FLAGS=!FLAGS! --new-job"
if not "!JOB_ID!"=="" set "FLAGS=!FLAGS! --job-id !JOB_ID!"

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

call "%AGENT_RUNNER_ROOT%\scripts\ukbe-run-delivery.bat" ^
    --project-root "!AGENT_RUNNER_ROOT!" ^
    --template-group "!TEMPLATE_GROUP!" ^
    --target-project-root "!TARGET_PROJECT_ROOT!" !FLAGS!

set "EXIT_CODE=!ERRORLEVEL!"

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Workflow finished with errors (exit code !EXIT_CODE!).
echo Check !TARGET_PROJECT_ROOT!\docs\codebase\ for partial output.
pause
exit /b !EXIT_CODE!

:success
echo(
echo Workflow completed successfully.
exit /b 0
