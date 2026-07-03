@echo off
REM run-system_docs_bootstrap_v1.bat - Edit the variables below, then double-click (or run).
REM
REM Runs ukbe-run-agent for the system_docs_bootstrap_v1 workflow:
REM   Generate stakeholder, functional, architecture, developer, and operations docs.

setlocal enabledelayedexpansion

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "TEMPLATE_GROUP=system_docs_bootstrap_v1"
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "JOB_ID=SYSDOC-GEN-20260701-002"
set "DRY_RUN=false"
set "NEW_JOB=true"

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
echo Check !TARGET_PROJECT_ROOT!\docs\system\, !TARGET_PROJECT_ROOT!\docs\engineering\, and !TARGET_PROJECT_ROOT!\docs\operations\ for partial output.
pause
exit /b !EXIT_CODE!

:success
echo(
echo Workflow completed successfully.
exit /b 0
