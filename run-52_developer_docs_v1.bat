@echo off
REM run-52_developer_docs_v1.bat - Edit the variables below, then double-click (or run).
REM
REM Runs ukbe-run-agent for the 52_developer_docs_v1 workflow:
REM   Publish the browsable HTML architecture site for a target repo.
REM
REM Runtime jobs and sidecars are stored under %USERPROFILE%\.ukbe-runner\jobs\
REM Runtime workflow bundles are stored under %USERPROFILE%\.ukbe-runner\workflows\
REM
REM Typical workflow:
REM   1. Edit the variables below
REM   2. Double-click or run it

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

REM Path to the agent-runner-v2 install (where the CLI lives)
set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"

REM Workflow template group
set "TEMPLATE_GROUP=52_developer_docs_v1"

REM Path to the project to publish the architecture site into
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"

REM Job ID to resume (leave blank to auto-create a new job)
set "JOB_ID="

REM Set DRY_RUN=true to render prompts only (no coder invocation)
set "DRY_RUN=false"

REM Set NEW_JOB=true to force a fresh run even if a previous job exists
set "NEW_JOB=false"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

REM --- Validate ---
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

REM --- Build flags ---
set "FLAGS="
if /I "!DRY_RUN!"=="true" set "FLAGS=!FLAGS! --dry-run"
if /I "!NEW_JOB!"=="true" set "FLAGS=!FLAGS! --new-job"
if not "%JOB_ID%"=="" set "FLAGS=!FLAGS! --job-id %JOB_ID%"

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

call "%AGENT_RUNNER_ROOT%\scripts\ukbe-run-delivery.bat" ^
    --project-root "!AGENT_RUNNER_ROOT!" ^
    --template-group "!TEMPLATE_GROUP!" ^
    --target-project-root "!TARGET_PROJECT_ROOT!" !FLAGS!

set "EXIT_CODE=!ERRORLEVEL!"

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Workflow finished with errors (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!

:success
echo(
echo Workflow completed successfully.
exit /b 0
