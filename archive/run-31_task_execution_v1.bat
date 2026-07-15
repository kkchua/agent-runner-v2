@echo off
REM run-31_task_execution_v1.bat - Edit the variables below, then double-click (or run).
REM
REM Runs ukbe-run-agent for the 31_task_execution_v1 workflow:
REM   Execute an approved task: generate implementation plan, review, execute code changes,
REM   sync documentation, validate. The core "do the work" workflow.
REM
REM Runtime jobs and sidecars are stored under %USERPROFILE%\.ukbe-runner\jobs\
REM Runtime workflow bundles are stored under %USERPROFILE%\.ukbe-runner\workflows\
REM
REM Typical workflow:
REM   1. Complete 30_delivery_planning_v1 to produce a TASK_GRAPH_FILE with tasks
REM   2. Select a specific task from the graph and edit the variables below
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
set "TEMPLATE_GROUP=31_task_execution_v1"

REM Path to the project containing the task
set "TARGET_PROJECT_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"

REM Path to the task contract file (REQUIRED)
REM Example: docs/delivery/03_tasks/TASK-20260708-001_example.md
set "TASK_FILE="

REM Path to the task graph file (optional, provides additional context)
REM Example: docs/delivery/02_task_graphs/TASK_GRAPH-20260708-001.json
set "TASK_GRAPH_FILE="

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

if "%TASK_FILE%"=="" (
    echo ERROR: TASK_FILE must point to a task contract markdown file.
    echo.
    echo Example: set "TASK_FILE=docs/delivery/03_tasks/TASK-20260708-001_example.md"
    echo.
    echo Tip: Complete 30_delivery_planning_v1 first to generate a TASK_GRAPH_FILE, then select a task.
    pause
    exit /b 1
)

if not exist "%TARGET_PROJECT_ROOT%\%TASK_FILE%" (
    echo ERROR: Task contract file does not exist: %TARGET_PROJECT_ROOT%\%TASK_FILE%
    echo.
    echo Tip: Complete 30_delivery_planning_v1 first to generate a TASK_GRAPH_FILE, then select a task.
    pause
    exit /b 1
)

REM --- Build flags ---
set "FLAGS=--project-root "!AGENT_RUNNER_ROOT!" --template-group !TEMPLATE_GROUP! --target-project-root "!TARGET_PROJECT_ROOT!" --set TASK_FILE=!TASK_FILE!"
if not "%TASK_GRAPH_FILE%"=="" set "FLAGS=!FLAGS! --set TASK_GRAPH_FILE=!TASK_GRAPH_FILE!"
if /I "!DRY_RUN!"=="true" set "FLAGS=!FLAGS! --dry-run"
if /I "!NEW_JOB!"=="true" set "FLAGS=!FLAGS! --new-job"
if not "%JOB_ID%"=="" set "FLAGS=!FLAGS! --job-id %JOB_ID%"

REM --- Run ---
echo ===========================================================================
echo  Workflow: !TEMPLATE_GROUP!
echo  Target:   !TARGET_PROJECT_ROOT!
echo ===========================================================================
echo  Agent-runner:      !AGENT_RUNNER_ROOT!
echo  Task File:         !TASK_FILE!
if not "!TASK_GRAPH_FILE!"=="" echo  Task Graph:        !TASK_GRAPH_FILE!
if not "!JOB_ID!"=="" echo  Job ID:              !JOB_ID!
echo  Dry run:           !DRY_RUN!
echo  New job:           !NEW_JOB!
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
