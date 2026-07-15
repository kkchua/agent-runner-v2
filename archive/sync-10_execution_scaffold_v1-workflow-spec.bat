@echo off
REM sync-10_execution_scaffold_v1-workflow-spec.bat - Export the authoritative local step spec.
REM
REM This does not update the backend database directly.
REM It generates the local workflow step-spec snapshot that the daemon now
REM reconciles against each claimed backend step before execution.

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "WORKFLOW_NAME=default"
set "TEMPLATE_GROUP=10_execution_scaffold_v1"
set "OUTPUT_FILE=%AGENT_RUNNER_ROOT%\temp\10_execution_scaffold_v1.step-spec.json"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent-runner root does not exist: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%" (
    echo ERROR: Project root does not exist: %PROJECT_ROOT%
    pause
    exit /b 1
)

where ukbe-run-agent >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot find ukbe-run-agent on PATH.
    echo Install the package first, for example: pip install -e .
    pause
    exit /b 1
)

echo ===========================================================================
echo  Workflow Spec Export
echo ===========================================================================
echo  Agent-runner:   %AGENT_RUNNER_ROOT%
echo  Project Root:   %PROJECT_ROOT%
echo  Workflow Name:  %WORKFLOW_NAME%
echo  Template Group: %TEMPLATE_GROUP%
echo  Output File:    %OUTPUT_FILE%
echo ===========================================================================
echo(

pushd "%AGENT_RUNNER_ROOT%"
call ukbe-run-agent workflow-spec ^
    --project-root "%PROJECT_ROOT%" ^
    --workflow-name "%WORKFLOW_NAME%" ^
    --template-group "%TEMPLATE_GROUP%" ^
    --output "%OUTPUT_FILE%"
set "EXIT_CODE=!ERRORLEVEL!"
popd

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Workflow spec export failed (exit code !EXIT_CODE!).
pause
exit /b !EXIT_CODE!

:success
echo(
echo Workflow spec exported successfully.
exit /b 0
