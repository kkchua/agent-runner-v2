@echo off
REM run-approve-step.bat - Edit the variables below, then run to approve a pending workflow step.
REM
REM Records human approval for a specific pending step on an existing job.
REM This is intended for manual recovery of workflows that pause at
REM WAITING_FOR_HUMAN_APPROVAL.
REM
REM Runtime jobs and sidecars are stored under %USERPROFILE%\.ukbe-runner\jobs\
REM Runtime workflow bundles are stored under %USERPROFILE%\.ukbe-runner\workflows\

setlocal enabledelayedexpansion

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "TEMPLATE_GROUP=00_master_docs_bootstrap_v1"
set "JOB_ID=00DOC-GEN-20260701-006"
set "STEP_NAME=05_review_master_system_docs"
set "FORCE_APPROVE=false"

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

set "APPROVAL_FLAG=--approve-step"
if /I "!FORCE_APPROVE!"=="true" set "APPROVAL_FLAG=--force-approve-step"

set "CMD=%UKBE_CLI% run --project-root "%AGENT_RUNNER_ROOT%" --template-group !TEMPLATE_GROUP! --job-id !JOB_ID! !APPROVAL_FLAG! !STEP_NAME!" 

echo ===========================================================================
echo  Step Approval
echo ===========================================================================
echo  Agent-runner:   !AGENT_RUNNER_ROOT!
echo  Template group: !TEMPLATE_GROUP!
echo  Job ID:         !JOB_ID!
echo  Step:           !STEP_NAME!
echo  Force approve:  !FORCE_APPROVE!
echo(
echo  Command: !CMD!
echo ===========================================================================
echo(

%CMD%
set "EXIT_CODE=%ERRORLEVEL%"

echo(
if "!EXIT_CODE!"=="0" goto :success
echo Step approval failed (exit code !EXIT_CODE!).
echo Check job status: %UKBE_CLI% run --project-root "%AGENT_RUNNER_ROOT%" --template-group !TEMPLATE_GROUP! --job-id !JOB_ID! --check-job-status
pause
exit /b !EXIT_CODE!

:success
echo Step approval recorded successfully.
exit /b 0
