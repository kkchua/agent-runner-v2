@echo off
REM run-30_delivery_planning_v1.bat - Edit the variables below, then double-click (or run).
REM
REM Runs ukbe-run-agent for the 30_delivery_planning_v1 workflow:
REM   Generate a delivery plan and task graph from an approved initiative. Produces plan document,
REM   task graph, and associated artifacts through review/refine loops.
REM
REM Runtime jobs and sidecars are stored under %USERPROFILE%\.ukbe-runner\jobs\
REM Runtime workflow bundles are stored under %USERPROFILE%\.ukbe-runner\workflows\
REM
REM Typical workflow:
REM   1. Complete 20_initiative_intake_v1 to produce an approved INIT_FILE
REM   2. Edit the variables below to point to your INIT_FILE
REM   3. Double-click or run this batch file

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
set "TEMPLATE_GROUP=30_delivery_planning_v1"

REM Path to the project containing the initiative
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"

REM Path to the approved initiative file (REQUIRED)
REM Example: docs/delivery/01_initiatives/approved/INIT-20260708-01_example.md
set "INIT_FILE=docs/delivery/01_initiatives/INIT-20260709-01_pre-init-20260709-01-close-github-issue-loop-after-bug-fix-completion.md"

REM Job ID to resume (leave blank to auto-create a new job)
set "JOB_ID="

REM Set DRY_RUN=true to render prompts only (no coder invocation)
set "DRY_RUN=false"

REM Set NEW_JOB=true to force a fresh run even if a previous job exists
set "NEW_JOB=true"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

REM --- Validate ---
if not exist "%TARGET_PROJECT_ROOT%" (
    echo ERROR: Target project root does not exist: %TARGET_PROJECT_ROOT%
    pause
    exit /b 1
)

if "%INIT_FILE%"=="" (
    echo ERROR: INIT_FILE must point to an approved initiative markdown file.
    echo.
    echo Example: set "INIT_FILE=docs/delivery/01_initiatives/approved/INIT-20260708-01_example.md"
    echo.
    echo Tip: Complete 20_initiative_intake_v1 first to generate an approved INIT_FILE.
    pause
    exit /b 1
)

if not exist "%TARGET_PROJECT_ROOT%\%INIT_FILE%" (
    echo ERROR: Approved initiative file does not exist: %TARGET_PROJECT_ROOT%\%INIT_FILE%
    echo.
    echo Tip: Complete 20_initiative_intake_v1 first to generate an approved INIT_FILE.
    pause
    exit /b 1
)

REM --- Build flags ---
set "FLAGS=--project-root "!AGENT_RUNNER_ROOT!" --template-group !TEMPLATE_GROUP! --target-project-root "!TARGET_PROJECT_ROOT!" --set INIT_FILE=!INIT_FILE!"
if /I "!DRY_RUN!"=="true" set "FLAGS=!FLAGS! --dry-run"
if /I "!NEW_JOB!"=="true" set "FLAGS=!FLAGS! --new-job"
if not "%JOB_ID%"=="" set "FLAGS=!FLAGS! --job-id %JOB_ID%"

REM --- Run ---
echo ===========================================================================
echo  Workflow: !TEMPLATE_GROUP!
echo  Target:   !TARGET_PROJECT_ROOT!
echo ===========================================================================
echo  Agent-runner:   !AGENT_RUNNER_ROOT!
echo  Initiative:     !INIT_FILE!
if not "!JOB_ID!"=="" echo  Job ID:          !JOB_ID!
echo  Dry run:        !DRY_RUN!
echo  New job:        !NEW_JOB!
echo ===========================================================================
echo(

ukbe-run-agent run !FLAGS!

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
