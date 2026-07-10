@echo off
REM run-image_csv_gen_v2.bat — Edit the variables below, then double-click (or run).
REM
REM Runs ukbe-run-agent for the image_csv_gen_v2 workflow:
REM   1. extract_desc   — Extract descriptions from all images in a folder
REM   2. gen_prompts    — Generate CSV metadata from the descriptions
REM   3. submit_prompts — Submit prompts to ComfyUI (action step)
REM
REM Typical workflow:
REM   1. Edit the variables below
REM   2. Place source images in IMAGE_FOLDER
REM   3. Double-click or run it

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
set "TEMPLATE_GROUP=image_csv_gen_v3"

REM Path to the project root (source_desc/ and source_csv/ folders will be created here)
set "PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\VideoExpress"

REM Path to the folder containing source images (REQUIRED — must exist)
set "IMAGE_FOLDER=D:\MyProjectSpace\01_Workflows\VideoExpress\input_images"

REM Job ID to resume (leave blank to auto-create a new job)
REM set "JOB_ID=IMGCSV-GEN-20260627-001"
set "JOB_ID=IMGCSV-GEN-20260710-004"

REM Set DRY_RUN=true to render prompts only (no coder invocation)
set "DRY_RUN=false"

REM Set NEW_JOB=true to force a fresh run even if a previous job exists
set "NEW_JOB=false"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

REM --- Validate ---
if not exist "%IMAGE_FOLDER%" (
    echo ERROR: Image folder does not exist: %IMAGE_FOLDER%
    pause
    exit /b 1
)

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent-runner root not found: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

REM --- Build flags ---
set "FLAGS= --set IMAGE_FOLDER=!IMAGE_FOLDER!"
if /I "!DRY_RUN!"=="true" set "FLAGS=!FLAGS! --dry-run"
if /I "!NEW_JOB!"=="true" set "FLAGS=!FLAGS! --new-job"
if not "!JOB_ID!"=="" set "FLAGS=!FLAGS! --job-id !JOB_ID!"

REM --- Run ---
echo ===========================================================================
echo  Workflow: !TEMPLATE_GROUP!
echo  Image folder: !IMAGE_FOLDER!
echo ===========================================================================
echo  Agent-runner:   !AGENT_RUNNER_ROOT!
echo  Project root:   !PROJECT_ROOT!
if not "!JOB_ID!"=="" echo  Job ID:          !JOB_ID!
echo  Dry run:        !DRY_RUN!
echo  New job:        !NEW_JOB!
echo ===========================================================================
echo(

ukbe-run-agent run ^
    --project-root "!PROJECT_ROOT!" ^
    --template-group "!TEMPLATE_GROUP!" ^
    !FLAGS!

set "EXIT_CODE=!ERRORLEVEL!"

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Workflow finished with errors (exit code !EXIT_CODE!).
echo Check output at !PROJECT_ROOT!\source_csv\ for partial results.
pause
exit /b !EXIT_CODE!

:success
echo(
echo Workflow completed successfully.
echo CSV output in: !PROJECT_ROOT!\source_csv\
exit /b 0
