@echo off
REM ukbe-run-delivery.bat - Manual workflow runner (no daemon)
REM
REM Runs ukbe-run-agent run for the specified template group, scaffolding
REM delivery SOPs, templates, and agent contracts into a target repo.
REM
REM Usage:
REM   %~nx0 --target-project-root ^<path^> [options]
REM
REM Options:
REM   --target-project-root ^<path^>   (Required) Target repo to scaffold delivery docs into
REM   --template-group ^<name^>         Workflow template (default: delivery_scaffold_v1)
REM   --project-root ^<path^>           Agent-runner-v2 workspace (default: current dir)
REM   --job-id ^<id^>                   Resume existing job (default: auto-create)
REM   --dry-run                         Render prompts only, skip coder invocation
REM   --new-job                         Force fresh job, skip auto-resume
REM   --help, /?                        Show this usage message
REM
REM Runtime output convention:
REM   Jobs and sidecars are written under %USERPROFILE%\.ukbe-runner\jobs\
REM   Runtime workflow bundles are loaded from %USERPROFILE%\.ukbe-runner\workflows\
REM
REM Examples:
REM   %~nx0 --target-project-root D:\MyProjectSpace\target-repo
REM   %~nx0 --target-project-root D:\MyProjectSpace\target-repo --new-job
REM   %~nx0 --template-group delivery_planning_v1 --target-project-root D:\MyProjectSpace\target-repo
REM   %~nx0 --project-root D:\Other\agent-runner-v2 --target-project-root D:\MyProjectSpace\target-repo

setlocal enabledelayedexpansion

set "UKBE_CLI=ukbe-run-agent"
set "PROJECT_ROOT="
set "TARGET_ROOT="
set "TEMPLATE_GROUP=delivery_scaffold_v1"
set "JOB_ID="
set "DRY_RUN="
set "NEW_JOB="

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
if /I "%~1"=="--target-project-root" (
    if "%~2"=="" (
        echo ERROR: --target-project-root requires a path argument.
        exit /b 1
    )
    set "TARGET_ROOT=%~2"
    shift
    shift
    goto :parse_args
)
if /I "%~1"=="--template-group" (
    if "%~2"=="" (
        echo ERROR: --template-group requires a name argument.
        exit /b 1
    )
    set "TEMPLATE_GROUP=%~2"
    shift
    shift
    goto :parse_args
)
if /I "%~1"=="--job-id" (
    if "%~2"=="" (
        echo ERROR: --job-id requires an ID argument.
        exit /b 1
    )
    set "JOB_ID=%~2"
    shift
    shift
    goto :parse_args
)
if /I "%~1"=="--dry-run" (
    set "DRY_RUN=1"
    shift
    goto :parse_args
)
if /I "%~1"=="--new-job" (
    set "NEW_JOB=1"
    shift
    goto :parse_args
)
echo ERROR: Unknown option: %~1
echo(
call :usage
exit /b 1

:check_args
if "%TARGET_ROOT%"=="" (
    echo ERROR: --target-project-root is required.
    echo(
    call :usage
    exit /b 1
)
if "%PROJECT_ROOT%"=="" (
    set "PROJECT_ROOT=%CD%"
)

REM Verify the CLI exists
where "%UKBE_CLI%" >nul 2>nul
if errorlevel 1 (
    echo ERROR: '%UKBE_CLI%' not found on PATH.
    echo Install agent-runner-v2 first: pip install -e .
    exit /b 1
)

REM Verify target directory exists
if not exist "%TARGET_ROOT%" (
    echo ERROR: Target project root does not exist: %TARGET_ROOT%
    exit /b 1
)

REM Verify project root exists
if not exist "%PROJECT_ROOT%" (
    echo ERROR: Project root does not exist: %PROJECT_ROOT%
    exit /b 1
)

REM Keep scratch space inside the repo so runs are self-contained.
set "TEMP_ROOT=%PROJECT_ROOT%\.tmp"
if not exist "%TEMP_ROOT%" mkdir "%TEMP_ROOT%" >nul 2>nul
set "TEMP=%TEMP_ROOT%"
set "TMP=%TEMP_ROOT%"
set "TMPDIR=%TEMP_ROOT%"

REM If resuming a specific job, show status and stop early when it is already completed.
if not "%JOB_ID%"=="" (
    set "STATUS_FILE=%TEMP_ROOT%\ukbe-run-delivery-status-%RANDOM%.txt"
    %UKBE_CLI% run --project-root "%PROJECT_ROOT%" --template-group %TEMPLATE_GROUP% --job-id %JOB_ID% --check-job-status > "!STATUS_FILE!"
    set "STATUS_EXIT=%ERRORLEVEL%"
    if "!STATUS_EXIT!"=="0" (
        set "JOB_STATUS="
        for /f "tokens=1,* delims=:" %%A in ('findstr /B /C:"Status:" "!STATUS_FILE!"') do set "JOB_STATUS=%%B"
        set "JOB_STATUS=!JOB_STATUS: =!"
        if /I "!JOB_STATUS!"=="COMPLETED" (
            echo ===========================================================================
            echo  Existing Job Status
            echo ===========================================================================
            type "!STATUS_FILE!"
            del "!STATUS_FILE!" >nul 2>nul
            echo(
            echo Job is already completed. Use --new-job to force another run.
            exit /b 0
        )
    )
    del "!STATUS_FILE!" >nul 2>nul
)

REM Build the command
set "CMD=%UKBE_CLI% run --project-root "%PROJECT_ROOT%" --template-group %TEMPLATE_GROUP% --target-project-root "%TARGET_ROOT%"" 
if "%DRY_RUN%"=="1" (
    set "CMD=!CMD! --dry-run"
)
if "%NEW_JOB%"=="1" (
    set "CMD=!CMD! --new-job"
)
if not "%JOB_ID%"=="" (
    set "CMD=!CMD! --job-id %JOB_ID%"
)

REM Show what we're about to run
echo ===========================================================================
echo  Manual Workflow Run
echo ===========================================================================
echo  Template group:   %TEMPLATE_GROUP%
echo  Project root:     %PROJECT_ROOT%
echo  Target root:      %TARGET_ROOT%
if not "%JOB_ID%"==""   echo  Job ID:            %JOB_ID%
if "%DRY_RUN%"=="1"     echo  Mode:              DRY RUN
if "%NEW_JOB%"=="1"     echo  New job:           Force new
echo(
echo  Command: !CMD!
echo ===========================================================================
echo(

REM Run the workflow
%CMD%
set "EXIT_CODE=%ERRORLEVEL%"

echo(
if "%EXIT_CODE%"=="0" goto :success
echo Delivery scaffold exited with code %EXIT_CODE%.
if not "%JOB_ID%"=="" (
    echo Check job status: %UKBE_CLI% run --project-root "%PROJECT_ROOT%" --template-group %TEMPLATE_GROUP% --job-id %JOB_ID% --check-job-status
) else (
    echo Re-run with the same seed or pass --job-id to inspect a specific existing job.
)
exit /b %EXIT_CODE%

:success
echo Delivery scaffold completed successfully.
exit /b 0

:usage
echo Usage: %~nx0 --target-project-root ^<path^> [options]
echo(
echo Options:
echo   --target-project-root ^<path^>   (Required) Target repo to scaffold delivery docs into
echo   --template-group ^<name^>         Workflow template (default: delivery_scaffold_v1)
echo   --project-root ^<path^>           Agent-runner-v2 workspace (default: current dir)
echo   --job-id ^<id^>                   Resume existing job (default: auto-create)
echo   --dry-run                         Render prompts only, skip coder invocation
echo   --new-job                         Force fresh job, skip auto-resume
echo   --help, /?                        Show this usage message
echo(
echo Examples:
echo   %~nx0 --target-project-root D:\MyProjectSpace\target-repo
echo   %~nx0 --target-project-root D:\MyProjectSpace\target-repo --new-job
echo   %~nx0 --template-group delivery_planning_v1 --target-project-root D:\MyProjectSpace\target-repo
echo   %~nx0 --project-root D:\Other\agent-runner-v2 --target-project-root D:\MyProjectSpace\target-repo
goto :eof
