@echo off
REM run-00-validate-workflow-bundle.bat - Validate one or more workflow bundles locally
REM
REM Usage:
REM   %~nx0 [workflow_name ...] [--workflows-root <path>] [--output <path>]
REM
REM Examples:
REM   %~nx0
REM   %~nx0 00_core_governance_bootstrap_v1
REM   %~nx0 00_core_governance_bootstrap_v1 10_execution_scaffold_v2

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

set "UKBE_CLI=ukbe-run-agent"
set "RUNNER_CMD="
set "WORKFLOWS_ROOT=%~dp0agent_runner_v2\bootstrap\workflows\default"
set "DEFAULT_WORKFLOW=00_core_governance_bootstrap_v1"

if exist "%~dp0.venv\Scripts\python.exe" (
    set "RUNNER_CMD=%~dp0.venv\Scripts\python.exe -m agent_runner_v2.run_agent"
) else (
    where "%UKBE_CLI%" >nul 2>nul
    if errorlevel 1 (
        echo ERROR: '%UKBE_CLI%' not found on PATH.
        echo Install agent-runner-v2 first: pip install -e .
        exit /b 1
    )
    set "RUNNER_CMD=%UKBE_CLI%"
)

set "TEMP_ROOT=%CD%\temp"
if not exist "%TEMP_ROOT%" mkdir "%TEMP_ROOT%" >nul 2>nul
set "TEMP=%TEMP_ROOT%"
set "TMP=%TEMP_ROOT%"
set "TMPDIR=%TEMP_ROOT%"

set "CMD=%RUNNER_CMD% validate-workflow-bundle --workflows-root "%WORKFLOWS_ROOT%""

if "%~1"=="" (
    set "CMD=!CMD! "%DEFAULT_WORKFLOW%""
    goto :run
)

:append_args
if "%~1"=="" goto :run
set "CMD=!CMD! "%~1""
shift
goto :append_args

:run
echo ===========================================================================
echo  Workflow Bundle Validation
echo ===========================================================================
echo  Project root:     %CD%
echo  Workflows root:   %WORKFLOWS_ROOT%
echo  Default workflow: %DEFAULT_WORKFLOW%
echo  Command:          !CMD!
echo ===========================================================================
echo(

%CMD%
set "EXIT_CODE=%ERRORLEVEL%"

echo(
if "%EXIT_CODE%"=="0" (
    echo Workflow bundle validation completed successfully.
    exit /b 0
)

echo Workflow bundle validation failed with code %EXIT_CODE%.
exit /b %EXIT_CODE%
