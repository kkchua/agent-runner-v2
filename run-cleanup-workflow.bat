@echo off
REM run-cleanup-workflow.bat - Delete execution history for a workflow before re-sync.
REM
REM Calls the backend cleanup endpoint to remove workflow runs, step runs,
REM and artifacts for a specific workflow. Useful when sync fails due to
REM database constraints from modified step definitions.
REM
REM Usage:
REM   run-cleanup-workflow.bat <workflow_name>
REM   run-cleanup-workflow.bat 00_repo_master_docs_bootstrap_v1
REM
REM After cleanup, re-run sync:
REM   sync-workflows-to-backend.bat <workflow_name>

setlocal enabledelayedexpansion

REM ==================================================================
REM Configuration
REM ==================================================================

set "BACKEND_URL=http://192.168.0.4:8100"

REM ==================================================================
REM Argument validation
REM ==================================================================

if "%~1"=="" (
    echo ERROR: Missing workflow_name argument.
    echo.
    echo Usage: run-cleanup-workflow.bat ^<workflow_name^>
    echo Example: run-cleanup-workflow.bat 00_repo_master_docs_bootstrap_v1
    pause
    exit /b 1
)

set "WORKFLOW_NAME=%~1"

echo ===========================================================================
echo  Workflow Execution Cleanup
echo ===========================================================================
echo  Backend URL:     %BACKEND_URL%
echo  Workflow Name:   %WORKFLOW_NAME%
echo ===========================================================================
echo.

REM ==================================================================
REM Step 1: Dry-run to preview deletions
REM ==================================================================

echo [Step 1] Dry-run: Previewing deletions...
echo.

powershell -Command ^
    "$body = @{ dry_run = $true; include_workers = $false; scope = @{ workflow_name = '%WORKFLOW_NAME%' } } | ConvertTo-Json -Depth 3; " ^
    "try { " ^
    "    $response = Invoke-RestMethod -Uri '%BACKEND_URL%/api/admin/execution/cleanup' -Method POST -ContentType 'application/json' -Body $body; " ^
    "    Write-Host 'Dry-run result:'; " ^
    "    $response.PSObject.Properties | ForEach-Object { Write-Host ('  {0}: {1}' -f $_.Name, $_.Value) }; " ^
    "    exit 0; " ^
    "} catch { " ^
    "    Write-Host ('ERROR: ' + $_.Exception.Message); " ^
    "    if ($_.Exception.Response) { " ^
    "        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream()); " ^
    "        Write-Host ($reader.ReadToEnd()); " ^
    "    } " ^
    "    exit 1; " ^
    "}"

if %ERRORLEVEL% neq 0 (
    echo.
    echo Dry-run failed. Check the error message above.
    pause
    exit /b 1
)

echo.
echo ===========================================================================
echo  The above counts show what WOULD be deleted.
echo ===========================================================================
echo.

REM ==================================================================
REM Step 2: Confirm before actual deletion
REM ==================================================================

set /p CONFIRM="Proceed with actual deletion? [y/N]: "
if /i not "%CONFIRM%"=="y" (
    echo Aborted. No changes were made.
    exit /b 0
)

echo.
echo [Step 2] Executing cleanup...
echo.

powershell -Command ^
    "$body = @{ dry_run = $false; include_workers = $false; scope = @{ workflow_name = '%WORKFLOW_NAME%' } } | ConvertTo-Json -Depth 3; " ^
    "try { " ^
    "    $response = Invoke-RestMethod -Uri '%BACKEND_URL%/api/admin/execution/cleanup' -Method POST -ContentType 'application/json' -Body $body; " ^
    "    Write-Host 'Cleanup result:'; " ^
    "    $response.PSObject.Properties | ForEach-Object { Write-Host ('  {0}: {1}' -f $_.Name, $_.Value) }; " ^
    "    exit 0; " ^
    "} catch { " ^
    "    Write-Host ('ERROR: ' + $_.Exception.Message); " ^
    "    if ($_.Exception.Response) { " ^
    "        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream()); " ^
    "        Write-Host ($reader.ReadToEnd()); " ^
    "    } " ^
    "    exit 1; " ^
    "}"

if %ERRORLEVEL% neq 0 (
    echo.
    echo Cleanup failed. Check the error message above.
    pause
    exit /b 1
)

echo.
echo ===========================================================================
echo  Cleanup completed successfully.
echo ===========================================================================
echo.
echo Next step: Re-sync the workflow
echo   sync-workflows-to-backend.bat %WORKFLOW_NAME%
echo.

set /p SYNC_NOW="Run sync now? [Y/n]: "
if /i "%SYNC_NOW%"=="n" (
    echo Skipped. Run sync manually when ready.
    exit /b 0
)

echo.
echo [Step 3] Syncing workflow to backend...
echo.

call "%~dp0sync-workflows-to-backend.bat" "%WORKFLOW_NAME%"

exit /b %ERRORLEVEL%