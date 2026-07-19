@echo off
REM run-bootstrap-publish.bat - Build the packaged bootstrap bundle from repo-local docs and workflow packages
REM
REM Usage:
REM   %~nx0
REM
REM Sequence:
REM   1. Run this script after changing:
REM      - docs/system/00_governance/bootstrap
REM      - workflows/<name>/workflow.toml packages
REM   2. Run run-init.bat to install the packaged bundle into %USERPROFILE%\.ukbe-runner\
REM
setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

set "UKBE_CLI=ukbe-run-agent"
set "RUNNER_CMD="

:parse_args
if "%~1"=="" goto :check_args
if /I "%~1"=="--help" goto :usage
if /I "%~1"=="/?" goto :usage
echo ERROR: Unknown option: %~1
echo(
call :usage
exit /b 1

:check_args

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

if not exist "%CD%\workflows" (
    echo ERROR: Required workflow source folder is missing: %CD%\workflows
    exit /b 1
)

set "TEMP_ROOT=%CD%\temp"
if not exist "%TEMP_ROOT%" mkdir "%TEMP_ROOT%" >nul 2>nul
set "TEMP=%TEMP_ROOT%"
set "TMP=%TEMP_ROOT%"
set "TMPDIR=%TEMP_ROOT%"

set "CMD=%RUNNER_CMD% bootstrap-publish"

echo ===========================================================================
echo  Bootstrap Bundle Publish
echo ===========================================================================
echo  Repository root:  %CD%
echo(
echo  Next step after publish:
echo    run-init.bat
echo(
echo  Command: !CMD!
echo ===========================================================================
echo(

%CMD%
set "EXIT_CODE=%ERRORLEVEL%"

echo(
if "%EXIT_CODE%"=="0" goto :success
echo Bootstrap publish exited with code %EXIT_CODE%.
exit /b %EXIT_CODE%

:success
echo Bootstrap publish completed successfully.
echo Next step: run-init.bat
exit /b 0

:usage
echo Usage: %~nx0
goto :eof
