@echo off
REM run-cleanup-generated-docs.bat - Manual cleanup for stale workflow-generated docs.
REM
REM This uses the workflow manifest to remove or quarantine workflow-owned docs
REM that no longer match the canonical output paths for a workflow.
REM
REM Default action is REMOVE. Change ACTION to REPORT or QUARANTINE if needed.
REM
REM Cleanup scope is controlled by TEMPLATE_GROUP and JOB_ID.

setlocal enabledelayedexpansion

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "TEMPLATE_GROUP=00_master_docs_bootstrap_v1"
set "JOB_ID="
set "MODE=bootstrap"
set "ACTION=remove"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent runner root does not exist: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

if "!JOB_ID!"=="" (
    for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Get-ChildItem -Path '%AGENT_RUNNER_ROOT%\docs\system\00_governance\bootstrap' -Filter '*-bootstrap-validation.md' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty BaseName"`) do (
        set "JOB_BASE=%%I"
    )
    if defined JOB_BASE (
        set "JOB_ID=!JOB_BASE:-bootstrap-validation=!"
    )
)

if "!JOB_ID!"=="" (
    echo ERROR: JOB_ID is required or no bootstrap validation file was found to infer it.
    pause
    exit /b 1
)

set "PY_CMD=python"
where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo ERROR: python or py not found on PATH.
        pause
        exit /b 1
    )
    set "PY_CMD=py -3"
)

set "CMD=!PY_CMD! -m agent_runner_v2.cleanup_generated_docs --project-root "%AGENT_RUNNER_ROOT%" --template-group !TEMPLATE_GROUP! --job-id !JOB_ID! --mode !MODE! --action !ACTION!"

echo ===========================================================================
echo  Workflow Docs Cleanup
echo ===========================================================================
echo  Agent-runner:   !AGENT_RUNNER_ROOT!
echo  Template group: !TEMPLATE_GROUP!
echo  Job ID:         !JOB_ID!
echo  Mode:           !MODE!
echo  Action:         !ACTION!
echo(
echo  Command: !CMD!
echo ===========================================================================
echo(

%CMD%
set "EXIT_CODE=%ERRORLEVEL%"

echo(
if "!EXIT_CODE!"=="0" goto :success
echo Cleanup failed (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!

:success
echo Cleanup completed successfully.
pause
exit /b 0
