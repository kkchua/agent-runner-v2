@echo off
REM run-bootstrap-publish.bat - Publish repo-local bootstrap docs into the packaged core bundle
REM
REM Usage:
REM   %~nx0 [--project-root <path>] [--source-root <path>] [--bundle-root <path>]
REM
REM Defaults:
REM   --project-root defaults to the current directory
REM   --source-root defaults to <project-root>\docs\system\00_governance\bootstrap
REM   --bundle-root defaults to <project-root>\agent_runner_v2\bootstrap\bundles\core\current

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

set "UKBE_CLI=ukbe-run-agent"
set "PROJECT_ROOT="
set "SOURCE_ROOT="
set "BUNDLE_ROOT="

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
if /I "%~1"=="--source-root" (
    if "%~2"=="" (
        echo ERROR: --source-root requires a path argument.
        exit /b 1
    )
    set "SOURCE_ROOT=%~2"
    shift
    shift
    goto :parse_args
)
if /I "%~1"=="--bundle-root" (
    if "%~2"=="" (
        echo ERROR: --bundle-root requires a path argument.
        exit /b 1
    )
    set "BUNDLE_ROOT=%~2"
    shift
    shift
    goto :parse_args
)
echo ERROR: Unknown option: %~1
echo(
call :usage
exit /b 1

:check_args
if "%PROJECT_ROOT%"=="" (
    set "PROJECT_ROOT=%CD%"
)

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

set "TEMP_ROOT=%PROJECT_ROOT%\temp"
if not exist "%TEMP_ROOT%" mkdir "%TEMP_ROOT%" >nul 2>nul
set "TEMP=%TEMP_ROOT%"
set "TMP=%TEMP_ROOT%"
set "TMPDIR=%TEMP_ROOT%"

set "CMD=%UKBE_CLI% bootstrap-publish --project-root "%PROJECT_ROOT%"" 
if not "%SOURCE_ROOT%"=="" (
    set "CMD=!CMD! --source-root "%SOURCE_ROOT%""
)
if not "%BUNDLE_ROOT%"=="" (
    set "CMD=!CMD! --bundle-root "%BUNDLE_ROOT%""
)

echo =========================================================================== 
echo  Bootstrap Bundle Publish
echo ===========================================================================
echo  Project root:     %PROJECT_ROOT%
if not "%SOURCE_ROOT%"=="" echo  Source root:      %SOURCE_ROOT%
if not "%BUNDLE_ROOT%"=="" echo  Bundle root:      %BUNDLE_ROOT%
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
exit /b 0

:usage
echo Usage: %~nx0 [--project-root ^<path^>] [--source-root ^<path^>] [--bundle-root ^<path^>]
echo(
echo Defaults:
echo   --project-root defaults to the current directory
echo   --source-root defaults to ^<project-root^\docs\system\00_governance\bootstrap
echo   --bundle-root defaults to ^<project-root^\agent_runner_v2\bootstrap\bundles\core\current
goto :eof
