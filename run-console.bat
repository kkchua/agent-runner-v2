@echo off
REM run-console.bat - Launch the Flet-based operator console.
REM
REM Starts the operator console in the foreground:
REM   .venv\Scripts\python.exe -m agent_runner_v2.run_agent console [options]
REM
REM Prerequisites:
REM   1. Install console dependencies:
REM        .\.venv\Scripts\python.exe -m pip install -e ".[console]"
REM   2. Ensure %USERPROFILE%\.ukbe-runner\config.json contains backend_url and worker_id
REM   3. Create or update the operator console config JSON

setlocal enabledelayedexpansion

REM ==================================================================
REM EDIT THESE VARIABLES to match your setup:
REM ==================================================================

set "AGENT_RUNNER_ROOT=D:\MyProjectSpace\01_Workflows\agent-runner-v2"
set "CONSOLE_CONFIG=%USERPROFILE%\.ukbe-runner\operator-console.json"

REM ==================================================================
REM No changes needed below this line.
REM ==================================================================

if not exist "%AGENT_RUNNER_ROOT%" (
    echo ERROR: Agent-runner root does not exist: %AGENT_RUNNER_ROOT%
    pause
    exit /b 1
)

set "VENV_PYTHON=%AGENT_RUNNER_ROOT%\.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    echo ERROR: Repo venv Python not found: %VENV_PYTHON%
    echo Create the repo venv and install editable first:
    echo   .\.venv\Scripts\python.exe -m pip install -e ".[dev,console]"
    pause
    exit /b 1
)

set "FLAGS="
if not "!CONSOLE_CONFIG!"=="" set "FLAGS=!FLAGS! --config ""!CONSOLE_CONFIG!"""

echo ===========================================================================
echo  Mode:            Operator Console
echo  Agent-runner:    !AGENT_RUNNER_ROOT!
echo  Python:          !VENV_PYTHON!
if not "!CONSOLE_CONFIG!"=="" (
echo  Console Config:  !CONSOLE_CONFIG!
) else (
echo  Console Config:  ^<from %USERPROFILE%\.ukbe-runner\operator-console.json^>
)
echo ===========================================================================
echo(

pushd "%AGENT_RUNNER_ROOT%"
call "!VENV_PYTHON!" -m agent_runner_v2.run_agent console !FLAGS!
set "EXIT_CODE=!ERRORLEVEL!"
popd

if "!EXIT_CODE!"=="0" goto :success
echo(
echo Operator console exited with code !EXIT_CODE!.
pause
exit /b !EXIT_CODE!

:success
echo(
echo Operator console closed normally.
exit /b 0
