@echo off
REM run-init.bat - Install the packaged bootstrap bundle into runner home and seed workflows
REM
REM Usage:
REM   %~nx0 [--project-root <path>] [--workflow <name>] [--bundle-domain <name>] [--bundle-profile <name>]
REM
REM Sequence:
REM   1. Run run-bootstrap-publish.bat after changing bootstrap docs or repo workflow packages.
REM   2. Run this script to install the packaged bundle into %USERPROFILE%\.ukbe-runner\
REM      and seed the example workflow bundle.
REM
REM What init does:
REM   - installs agent_runner_v2\bootstrap\bundles\core\current
REM     -> %USERPROFILE%\.ukbe-runner\bundles\core\current
REM   - seeds bootstrap/workflows/default/
REM     -> %USERPROFILE%\.ukbe-runner\workflows\example\
REM   - seeds repo workflow packages into the global example workflow bundle

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

set "UKBE_CLI=ukbe-run-agent"
set "PROJECT_ROOT=%CD%"
set "WORKFLOW=default"
set "BUNDLE_DOMAIN=general"
set "BUNDLE_PROFILE=core+workflow"

:parse_args
if "%~1"=="" goto :check_args
if /I "%~1"=="--help" goto :usage
if /I "%~1"=="/?" goto :usage
if /I "%~1"=="--project-root" (
    if "%~2"=="" (
        echo ERROR: --project-root requires a path argument.
        exit /b 1
    )
    set "PROJECT_ROOT=%~2"
    shift
    shift
    goto :parse_args
)
if /I "%~1"=="--workflow" (
    if "%~2"=="" (
        echo ERROR: --workflow requires a value.
        exit /b 1
    )
    set "WORKFLOW=%~2"
    shift
    shift
    goto :parse_args
)
if /I "%~1"=="--bundle-domain" (
    if "%~2"=="" (
        echo ERROR: --bundle-domain requires a value.
        exit /b 1
    )
    set "BUNDLE_DOMAIN=%~2"
    shift
    shift
    goto :parse_args
)
if /I "%~1"=="--bundle-profile" (
    if "%~2"=="" (
        echo ERROR: --bundle-profile requires a value.
        exit /b 1
    )
    set "BUNDLE_PROFILE=%~2"
    shift
    shift
    goto :parse_args
)
echo ERROR: Unknown option: %~1
echo(
call :usage
exit /b 1

:check_args
where "%UKBE_CLI%" >nul 2>nul
if errorlevel 1 (
    echo ERROR: '%UKBE_CLI%' not found on PATH.
    echo Install agent-runner-v2 first: pip install -e .
    exit /b 1
)

if not exist "%PROJECT_ROOT%" (
    echo ERROR: Project root does not exist: %PROJECT_ROOT%
    exit /b 1
)

set "CMD=%UKBE_CLI% init --project-root "%PROJECT_ROOT%" --workflow "%WORKFLOW%" --bundle-domain "%BUNDLE_DOMAIN%" --bundle-profile "%BUNDLE_PROFILE%""

echo ===========================================================================
echo  Runner Init
echo ===========================================================================
echo  Project root:     %PROJECT_ROOT%
echo  Workflow:         %WORKFLOW%
echo  Bundle domain:    %BUNDLE_DOMAIN%
echo  Bundle profile:   %BUNDLE_PROFILE%
echo(
echo  Recommended sequence:
echo    1. run-bootstrap-publish.bat
echo    2. run-init.bat
echo(
echo  Command: !CMD!
echo ===========================================================================
echo(

%CMD%
set "EXIT_CODE=%ERRORLEVEL%"

echo(
if "%EXIT_CODE%"=="0" goto :success
echo Init exited with code %EXIT_CODE%.
exit /b %EXIT_CODE%

:success
echo Init completed successfully.
exit /b 0

:usage
echo Usage: %~nx0 [--project-root ^<path^>] [--workflow ^<name^>] [--bundle-domain ^<name^>] [--bundle-profile ^<name^>]
goto :eof
