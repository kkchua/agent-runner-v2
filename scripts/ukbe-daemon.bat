@echo off
REM ukbe-daemon.bat - Simple Windows wrapper for ukbe-run-agent daemon

set "UKBE_CLI=ukbe-run-agent"
set "CONFIG_DIR=%USERPROFILE%\.ukbe-runner"
set "PID_DIR=%CONFIG_DIR%\workers"
set "LOG_DIR=%CONFIG_DIR%\logs"

if "%~1"=="" goto :usage

set "WORKER_ID=%~2"
if "%~2"=="" set "WORKER_ID=kode-worker-01"

set "PID_FILE=%PID_DIR%\%WORKER_ID%.pid"
set "LOG_FILE=%LOG_DIR%\worker-%WORKER_ID%.log"

if /I "%~1"=="start" goto :do_start
if /I "%~1"=="stop" goto :do_stop
if /I "%~1"=="status" goto :do_status
if /I "%~1"=="logs" goto :do_logs
if /I "%~1"=="restart" goto :do_restart
goto :usage

:do_start
if not exist "%PID_DIR%" mkdir "%PID_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if exist "%PID_FILE%" (
    echo Worker '%WORKER_ID%' is already running.
    goto :eof
)
del /f /q "%PID_FILE%" 2>nul
echo Starting worker '%WORKER_ID%'...
echo   Log: %LOG_FILE%
start /b "" %UKBE_CLI% daemon %WORKER_ID% >"%LOG_FILE%" 2>&1
timeout /t 2 /nobreak >nul
echo Worker '%WORKER_ID%' started.
echo   Log: %LOG_FILE%
goto :eof

:do_stop
if not exist "%PID_FILE%" (
    echo Worker '%WORKER_ID%' is not running.
    goto :eof
)
set /p PID=<"%PID_FILE%"
if "%PID%"=="" goto :cleanup_and_stop
echo Stopping worker '%WORKER_ID%' (PID %PID%)...
taskkill /PID %PID% 2>nul
timeout /t 2 /nobreak >nul
tasklist /FI "PID eq %PID%" 2>nul | findstr "%PID%" >nul
if not errorlevel 1 taskkill /F /PID %PID% 2>nul
:cleanup_and_stop
del /f /q "%PID_FILE%" 2>nul
echo Worker '%WORKER_ID%' stopped.
goto :eof

:do_status
if not exist "%PID_FILE%" (
    echo Worker '%WORKER_ID%' is not running.
    goto :eof
)
set /p PID=<"%PID_FILE%"
if "%PID%"=="" (
    del /f /q "%PID_FILE%" 2>nul
    echo Worker '%WORKER_ID%' is not running.
    goto :eof
)
tasklist /FI "PID eq %PID%" 2>nul | findstr "%PID%" >nul
if errorlevel 1 (
    del /f /q "%PID_FILE%" 2>nul
    echo Worker '%WORKER_ID%' is not running.
) else (
    echo Worker '%WORKER_ID%' is running (PID %PID%).
    echo   Log: %LOG_FILE%
)
goto :eof

:do_logs
if not exist "%LOG_FILE%" (
    echo No log file found at %LOG_FILE%
    goto :eof
)
echo Showing logs for '%WORKER_ID%' - Press Ctrl+C to exit:
echo.
type "%LOG_FILE%"
goto :eof

:do_restart
call :do_stop
timeout /t 1 /nobreak >nul
call :do_start
goto :eof

:usage
echo Usage: %~nx0 ^<command^> [worker-id]
echo.
echo Commands:
echo   start   - Start worker daemon
echo   stop    - Stop worker daemon  
echo   status  - Check worker status
echo   logs    - Show worker logs
echo   restart - Restart worker
echo.
echo Worker ID defaults to: kode-worker-01
echo.
echo Examples:
echo   %~nx0 start            - Start kode-worker-01
echo   %~nx0 start my-worker  - Start my-worker
echo   %~nx0 status            - Check kode-worker-01 status
