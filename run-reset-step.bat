@echo off
REM run-reset-step.bat - Edit the variables below, then run to reset a job to a specific step.
REM
REM Resets workflow execution state to the selected step using:
REM   ukbe-run-agent run --override-step <step>
REM
REM This does NOT create a new job. It mutates the existing job state so the
REM selected step and all downstream steps can be rerun.
REM
REM Runtime jobs and sidecars are stored under %USERPROFILE%\.ukbe-runner\jobs\
REM Runtime workflow bundles are stored under %USERPROFILE%\.ukbe-runner\workflows\

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "TEMPLATE_GROUP=00_master_docs_bootstrap_v2"
set "JOB_ID=00DOC-20260710-f9cc9341"
set "STEP_NAME=05_review_master_system_docs"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

set "UKBE_CLI=ukbe-run-agent"

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent runner root does not exist: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

if "!TEMPLATE_GROUP!"=="" (
    echo ERROR: TEMPLATE_GROUP is required.
    pause
    exit /b 1
)

if "!JOB_ID!"=="" (
    echo ERROR: JOB_ID is required.
    pause
    exit /b 1
)

if "!STEP_NAME!"=="" (
    echo ERROR: STEP_NAME is required.
    pause
    exit /b 1
)

where "%UKBE_CLI%" >nul 2>nul
if errorlevel 1 (
    echo ERROR: '%UKBE_CLI%' not found on PATH.
    pause
    exit /b 1
)

set "CMD=%UKBE_CLI% run --project-root "%AGENT_RUNNER_ROOT%" --template-group !TEMPLATE_GROUP! --job-id !JOB_ID! --override-step !STEP_NAME!"

echo ===========================================================================
echo  Step Reset
echo ===========================================================================
echo  Agent-runner:   !AGENT_RUNNER_ROOT!
echo  Template group: !TEMPLATE_GROUP!
echo  Job ID:         !JOB_ID!
echo  Reset to step:  !STEP_NAME!
echo(
echo  Command: !CMD!
echo ===========================================================================
echo(

%CMD%
set "EXIT_CODE=%ERRORLEVEL%"

echo(
if "!EXIT_CODE!"=="0" goto :success
echo Step reset failed (exit code !EXIT_CODE!).
echo Check job status: %UKBE_CLI% run --project-root "%AGENT_RUNNER_ROOT%" --template-group !TEMPLATE_GROUP! --job-id !JOB_ID! --check-job-status
pause
exit /b !EXIT_CODE!

:success
echo Step reset recorded successfully.
echo Re-run the normal workflow batch file to continue from !STEP_NAME!.
exit /b 0
