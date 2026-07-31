@echo off
REM run-cleanup.bat - Cleanup old job history and runtime files
REM
REM Usage:
REM   %~nx0 [--confirm] [--keep-days <N>] [--target <jobs|runtime|all>]
REM
REM Options:
REM   --confirm     Actually delete files (default: dry-run only)
REM   --keep-days   Override config.json cleanup_keep_days (default: 7)
REM   --target      Clean specific area: jobs, runtime, or all (default: all)
REM
REM Examples:
REM   %~nx0                     # Dry-run: show what would be deleted
REM   %~nx0 --confirm           # Actually delete old files
REM   %~nx0 --keep-days 3       # Keep only last 3 days
REM   %~nx0 --target jobs       # Only clean job folders

setlocal enabledelayedexpansion

REM --- Activate .venv if it exists ---
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
)

set "UKBE_CLI=ukbe-run-agent"
set "CONFIRM="
set "KEEP_DAYS="
set "TARGET="

:parse_args
if "%~1"=="" goto :check_args
if /I "%~1"=="--help" goto :usage
if /I "%~1"=="/?" goto :usage
if /I "%~1"=="--confirm" (
    set "CONFIRM=--confirm"
    shift
    goto :parse_args
)
if /I "%~1"=="--keep-days" (
    if "%~2"=="" (
        echo ERROR: --keep-days requires a value.
        exit /b 1
    )
    set "KEEP_DAYS=--keep-days %~2"
    shift
    shift
    goto :parse_args
)
if /I "%~1"=="--target" (
    if "%~2"=="" (
        echo ERROR: --target requires a value (jobs, runtime, or all).
        exit /b 1
    )
    set "TARGET=--target %~2"
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

set "CMD=%UKBE_CLI% cleanup %CONFIRM% %KEEP_DAYS% %TARGET%"

echo ===========================================================================
echo  Runner Cleanup
echo ===========================================================================
echo  Runner home:      %USERPROFILE%\.ukbe-runner
echo  Mode:             %CONFIRM:--confirm=DRY-RUN%
if not defined CONFIRM echo                    (use --confirm to actually delete)
if defined KEEP_DAYS echo  Keep days:        %KEEP_DAYS:--keep-days =%
if not defined KEEP_DAYS echo  Keep days:        (from config.json, default: 7)
if defined TARGET echo  Target:           %TARGET:--target =%
if not defined TARGET echo  Target:           all
echo(
echo  Targets:
echo    - jobs/%USERPROFILE%\.ukbe-runner\jobs\<workflow>\<job-id>
echo    - runtime/%USERPROFILE%\.ukbe-runner\runtime\worker\
echo(
echo  Command: !CMD!
echo ===========================================================================
echo(

!CMD!
set "EXIT_CODE=%ERRORLEVEL%"

echo(
if "%EXIT_CODE%"=="0" goto :success
echo Cleanup exited with code %EXIT_CODE%.
exit /b %EXIT_CODE%

:success
echo Cleanup completed successfully.
exit /b 0

:usage
echo Usage: %~nx0 [--confirm] [--keep-days ^<N^>] [--target ^<jobs^|runtime^|all^>]
echo(
echo Options:
echo   --confirm      Actually delete files ^(default: dry-run only shows what would be deleted^)
echo   --keep-days    Number of days to keep ^(default: from config.json or 7^)
echo   --target       Clean specific area only: jobs, runtime, or all ^(default: all^)
echo(
echo Examples:
echo   %~nx0                      # Preview what would be deleted
echo   %~nx0 --confirm            # Actually delete old files
echo   %~nx0 --keep-days 3        # Keep only last 3 days
echo   %~nx0 --target jobs        # Only clean job folders
goto :eof
