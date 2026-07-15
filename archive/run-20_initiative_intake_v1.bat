@echo off
REM run-20_initiative_intake_v1.bat - Edit the variables below, then double-click (or run).
REM
REM Runs ukbe-run-agent for the 20_initiative_intake_v1 workflow:
REM   Draft initiative intake and pre-init refinement for new features, refactors, or improvements.
REM
REM Runtime jobs and sidecars are stored under %USERPROFILE%\.ukbe-runner\jobs\
REM Runtime workflow bundles are stored under %USERPROFILE%\.ukbe-runner\workflows\
REM
REM Typical workflow:
REM   1. Use the draft-initiative-pre-init skill to create a DRAFT_INIT_FILE
REM      OR manually create a draft at docs/delivery/01_initiatives/draft/
REM   2. Edit the variables below to point to your DRAFT_INIT_FILE
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
set "TEMPLATE_GROUP=20_initiative_intake_v1"

REM Path to the project containing the draft
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"

REM Path to the draft initiative file (REQUIRED)
REM Example: docs/delivery/01_initiatives/draft/INIT-DRAFT-20260708-01_close-github-issue-loop.md
set "DRAFT_INIT_FILE=docs/delivery/01_initiatives/draft/INIT-DRAFT-20260708-01_close-github-issue-loop.md"

REM Job ID to resume (leave blank to auto-create a new job)
set "JOB_ID=20PREINIT-GEN-20260709-001"

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

if "%DRAFT_INIT_FILE%"=="" (
    echo ERROR: DRAFT_INIT_FILE must point to a draft initiative markdown file.
    echo.
    echo Example: set "DRAFT_INIT_FILE=docs/delivery/01_initiatives/draft/DRAFT-20260707-01_example.md"
    echo.
    echo Tip: Use the draft-initiative-pre-init skill to help you create an initiative draft.
    pause
    exit /b 1
)

if not exist "%TARGET_PROJECT_ROOT%\%DRAFT_INIT_FILE%" (
    echo ERROR: Draft initiative file does not exist: %TARGET_PROJECT_ROOT%\%DRAFT_INIT_FILE%
    echo.
    echo Tip: Use the draft-initiative-pre-init skill to help you create an initiative draft.
    pause
    exit /b 1
)

REM --- Build flags ---
set "FLAGS=--project-root "!AGENT_RUNNER_ROOT!" --template-group !TEMPLATE_GROUP! --target-project-root "!TARGET_PROJECT_ROOT!" --set DRAFT_INIT_FILE=!DRAFT_INIT_FILE!"
if /I "!DRY_RUN!"=="true" set "FLAGS=!FLAGS! --dry-run"
if /I "!NEW_JOB!"=="true" set "FLAGS=!FLAGS! --new-job"
if not "%JOB_ID%"=="" set "FLAGS=!FLAGS! --job-id %JOB_ID%"

REM --- Run ---
echo ===========================================================================
echo  Workflow: !TEMPLATE_GROUP!
echo  Target:   !TARGET_PROJECT_ROOT!
echo ===========================================================================
echo  Agent-runner:   !AGENT_RUNNER_ROOT!
echo  Draft Init:     !DRAFT_INIT_FILE!
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
